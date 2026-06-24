"""
Streamlit chat UI for the RAG engine.
    streamlit run app.py
Pick a sample knowledge base or upload your own PDFs/MD/TXT, then chat.
Answers show source citations + a confidence score; low confidence escalates.
"""
import io
import streamlit as st
from rag_core import RAG, load_dir

st.set_page_config(page_title="Document RAG Chatbot", page_icon="📄")
st.title("📄 Document RAG Chatbot")


def docs_from_uploads(files):
    docs = []
    for f in files or []:
        data = f.read()
        if f.name.lower().endswith(".pdf"):
            import pdfplumber
            with pdfplumber.open(io.BytesIO(data)) as pdf:
                text = "\n".join(p.extract_text() or "" for p in pdf.pages)
        else:
            text = data.decode("utf-8", errors="ignore")
        docs.append((f.name, text))
    return docs


with st.sidebar:
    st.header("Knowledge base")
    mode = st.radio("Source", ["Sample: support", "Sample: product", "Sample: policy", "Upload your own"])
    uploads = None
    if mode == "Upload your own":
        uploads = st.file_uploader("PDF / TXT / MD", type=["pdf", "txt", "md"], accept_multiple_files=True)
    build = st.button("Build / rebuild index", type="primary")

if build or "rag" not in st.session_state:
    docs = docs_from_uploads(uploads) if mode == "Upload your own" else load_dir("samples/" + mode.split(": ")[1])
    if docs:
        rag = RAG().ingest_docs(docs)
        st.session_state.rag = rag
        st.session_state.messages = []
        st.sidebar.success(f"Indexed {len(docs)} document(s)")

rag = st.session_state.get("rag")
if not rag:
    st.info("Upload documents and click **Build index** to start.")
    st.stop()

b = rag.backend
st.caption(f"embeddings: **{b['embeddings']}**  ·  generation: **{b['generation']}**  ·  {b['chunks']} chunks")
st.caption("'Confidence' is retrieval similarity to your docs — with TF-IDF (no API key) these numbers run low; that's expected.")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if q := st.chat_input("Ask about your documents..."):
    st.session_state.messages.append({"role": "user", "content": q})
    with st.chat_message("user"):
        st.markdown(q)
    out = rag.answer(q)
    with st.chat_message("assistant"):
        st.markdown(out["answer"])
        if out["escalate"]:
            st.warning(f"Low confidence ({out['confidence']}) — escalated to a human agent.")
        else:
            st.caption("Sources: " + ", ".join(out["citations"]) + f"  ·  confidence {out['confidence']}")
    st.session_state.messages.append({"role": "assistant", "content": out["answer"]})
