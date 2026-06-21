# Document RAG Chatbot — upload docs, ask questions, get cited answers

A production-style Retrieval-Augmented Generation chatbot: point it at a set of documents (PDF / Markdown / text), ask questions in plain language, and get **answers grounded in your documents with source citations and a confidence score**. When the answer isn't in the documents it **says so and escalates** instead of hallucinating. Conversation memory handles follow-up questions.

This is the exact build behind the common Upwork brief: *"document-based RAG chatbot, users upload documents, answers with source references."*

## Run

```bash
pip install -r requirements.txt
python test_rag.py                              # smoke test (no key needed)
python cli.py samples/support "I was charged twice"
streamlit run app.py                            # web chat UI (upload your own docs)
```

Three sample knowledge bases are included — `samples/support`, `samples/product`, `samples/policy` — so you can see it answer across three different domains.

## Architecture

```
load (PDF/MD/TXT) → chunk (header-aware) → embed → vector store
                                                       │
query → embed → cosine top-k → relevance filter → grounded answer + citations + confidence
                                     │
                          below threshold → escalate to human
```

| Stage | Default (no key) | Upgrades to |
|-------|------------------|-------------|
| Embeddings | TF-IDF | OpenAI `text-embedding-3-small`, or local `sentence-transformers` |
| Generation | extractive (top chunk) | Claude (`ANTHROPIC_API_KEY`) or OpenAI (`OPENAI_API_KEY`) |

It **runs end-to-end with zero API keys** and upgrades automatically when keys or packages are present — same interface either way. `rag.backend` reports which path is active.

## What it demonstrates
- Real retrieval pipeline (chunking, embeddings, vector search) — not a prompt wrapper
- **Source citations + confidence** on every answer
- **Anti-hallucination:** low-confidence questions escalate instead of guessing
- **Conversation memory** with safe follow-up handling
- Pluggable embedding + generation backends (OpenAI / Claude / local)
- Web UI (upload your own documents) + CLI + a passing smoke test

## Files
`rag_core.py` engine · `app.py` Streamlit UI · `cli.py` command line · `test_rag.py` test · `samples/` three knowledge bases
