"""
rag_core.py - production-style RAG engine.

Pipeline:  load -> chunk -> embed -> store -> retrieve -> grounded answer
           (+ source citations, confidence score, escalation, conversation memory)

Embeddings:  OpenAI text-embedding-3-small  (OPENAI_API_KEY)
          -> sentence-transformers all-MiniLM-L6-v2  (if installed)
          -> TF-IDF                                  (no key, always works)

Generation:  Claude  (ANTHROPIC_API_KEY)
          -> OpenAI  (OPENAI_API_KEY)
          -> extractive fallback  (no key)

Runs with ZERO keys (TF-IDF retrieval + extractive answer) and upgrades
automatically when keys / packages are present. Same interface either way.
"""
import os
import re
import glob

import numpy as np


# --------------------------------------------------------------------------- #
# Loading
# --------------------------------------------------------------------------- #
def load_text(path: str) -> str:
    if path.lower().endswith(".pdf"):
        import pdfplumber
        with pdfplumber.open(path) as pdf:
            return "\n".join(p.extract_text() or "" for p in pdf.pages)
    with open(path, encoding="utf-8", errors="ignore") as f:
        return f.read()


def load_dir(folder: str, exts=(".md", ".txt", ".pdf")):
    docs = []
    for path in sorted(glob.glob(os.path.join(folder, "**", "*"), recursive=True)):
        if path.lower().endswith(exts):
            docs.append((os.path.basename(path), load_text(path)))
    return docs


# --------------------------------------------------------------------------- #
# Chunking  (paragraph-aware, packed to ~size with overlap)
# --------------------------------------------------------------------------- #
def chunk_text(text: str, size: int = 600):
    """Markdown header-aware: each ## section becomes one focused chunk
    (falls back to paragraph splitting for plain text)."""
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if re.search(r"(?m)^#{1,3}\s", text):
        units = [u.strip() for u in re.split(r"(?m)^(?=#{1,3}\s)", text) if u.strip()]
    else:
        units = [u.strip() for u in text.split("\n\n") if u.strip()]
    chunks = []
    for u in units:
        if len(u) < 25:          # skip lone title lines
            continue
        if len(u) <= size:
            chunks.append(u)
        else:
            for i in range(0, len(u), size):
                chunks.append(u[i:i + size])
    return chunks or [text[:size]]


# --------------------------------------------------------------------------- #
# Embeddings  (3-tier, cosine via L2-normalised vectors)
# --------------------------------------------------------------------------- #
class Embedder:
    def __init__(self):
        if os.getenv("OPENAI_API_KEY"):
            self.mode = "openai"
        else:
            try:
                from sentence_transformers import SentenceTransformer
                self._st = SentenceTransformer("all-MiniLM-L6-v2")
                self.mode = "sbert"
            except Exception:
                self.mode = "tfidf"

    @staticmethod
    def _norm(m):
        m = np.asarray(m, dtype="float32")
        if m.ndim == 1:
            m = m.reshape(1, -1)
        n = np.linalg.norm(m, axis=1, keepdims=True)
        n[n == 0] = 1.0
        return m / n

    def _openai(self, texts):
        import openai
        client = openai.OpenAI()
        r = client.embeddings.create(model="text-embedding-3-small", input=texts)
        return [d.embedding for d in r.data]

    def fit_encode(self, texts):
        if self.mode == "tfidf":
            from sklearn.feature_extraction.text import TfidfVectorizer
            self._vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
            return self._norm(self._vec.fit_transform(texts).toarray())
        if self.mode == "sbert":
            return self._norm(self._st.encode(texts))
        return self._norm(self._openai(texts))

    def encode_query(self, q):
        if self.mode == "tfidf":
            return self._norm(self._vec.transform([q]).toarray())[0]
        if self.mode == "sbert":
            return self._norm(self._st.encode([q]))[0]
        return self._norm(self._openai([q]))[0]


# --------------------------------------------------------------------------- #
# RAG engine
# --------------------------------------------------------------------------- #
class RAG:
    def __init__(self, threshold: float = 0.12):
        self.chunks = []          # [{"text":..., "source":...}]
        self.threshold = threshold
        self._emb = Embedder()
        self._matrix = None
        self.history = []         # [(question, answer)]

    @property
    def backend(self):
        gen = ("claude" if os.getenv("ANTHROPIC_API_KEY")
               else "openai" if os.getenv("OPENAI_API_KEY") else "extractive")
        return {"embeddings": self._emb.mode, "generation": gen, "chunks": len(self.chunks)}

    def ingest_docs(self, docs):
        for src, text in docs:
            for ch in chunk_text(text):
                self.chunks.append({"text": ch, "source": src})
        self._build()
        return self

    def ingest_dir(self, folder):
        return self.ingest_docs(load_dir(folder))

    def _build(self):
        self._matrix = self._emb.fit_encode([c["text"] for c in self.chunks])

    def retrieve(self, query, k=4):
        # contextualise ONLY short follow-ups ("what about express?") so an
        # unrelated new question isn't polluted by the previous one.
        q = query
        if self.history and len(query.split()) <= 4:
            q = self.history[-1][0] + " " + query
        qv = self._emb.encode_query(q)
        sims = self._matrix @ qv
        idx = np.argsort(-sims)[:k]
        return [(self.chunks[i], float(sims[i])) for i in idx]

    def _generate(self, query, context):
        system = (
            "You are a support assistant. Answer the question using ONLY the context. "
            "Cite the sources you used as [source-name]. If the answer is not in the "
            "context, say you don't know - never invent facts. Be concise."
        )
        user = f"Context:\n{context}\n\nQuestion: {query}"
        hist = []
        for q, a in self.history[-2:]:
            hist += [{"role": "user", "content": q}, {"role": "assistant", "content": a}]
        if os.getenv("ANTHROPIC_API_KEY"):
            import anthropic
            c = anthropic.Anthropic()
            r = c.messages.create(model="claude-haiku-4-5-20251001", max_tokens=500,
                                  system=system, messages=hist + [{"role": "user", "content": user}])
            return r.content[0].text.strip()
        if os.getenv("OPENAI_API_KEY"):
            import openai
            c = openai.OpenAI()
            r = c.chat.completions.create(
                model="gpt-4o-mini", max_tokens=500,
                messages=[{"role": "system", "content": system}] + hist + [{"role": "user", "content": user}])
            return r.choices[0].message.content.strip()
        # extractive fallback (no key): return all retrieved passages so the
        # answer text always matches the cited sources (no citation mismatch).
        return "Based on the documents:\n\n" + context.strip()

    def answer(self, query, k=4):
        hits = self.retrieve(query, k)
        top = hits[0][1] if hits else 0.0
        if top < self.threshold:
            out = {"answer": "I couldn't find this in the provided documents - escalating to a human agent.",
                   "citations": [], "confidence": round(top, 3), "escalate": True, "sources": []}
            self.history.append((query, out["answer"]))
            return out
        # keep only genuinely relevant hits (near the top score) for context + citations
        floor = max(self.threshold, top * 0.55)
        rel = [h for h in hits if h[1] >= floor] or hits[:1]
        context = "\n\n---\n\n".join(
            f"(source: {h[0]['source']})\n{h[0]['text']}" for h in rel)
        ans = self._generate(query, context)
        out = {
            "answer": ans,
            "citations": sorted({h[0]["source"] for h in rel}),
            "confidence": round(top, 3),
            "escalate": False,
            "sources": [{"source": h[0]["source"], "score": round(h[1], 3)} for h in rel],
        }
        self.history.append((query, ans))
        return out

    def reset_memory(self):
        self.history = []
