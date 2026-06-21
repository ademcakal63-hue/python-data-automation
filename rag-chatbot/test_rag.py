"""
Smoke test: retrieval grounds to the right document, off-topic escalates,
and conversation memory persists. Runs with no API key (TF-IDF + extractive).
"""
from rag_core import RAG


def test():
    rag = RAG().ingest_dir("samples/support")
    print("backend:", rag.backend)

    a = rag.answer("I was charged twice, what do I do?")
    assert not a["escalate"], "billing question should not escalate"
    assert "billing.md" in a["citations"], f"expected billing.md, got {a['citations']}"
    print("Q1 ok  -> cites", a["citations"], "| conf", a["confidence"])

    b = rag.answer("How long does international shipping take?")
    assert "shipping.md" in b["citations"], f"expected shipping.md, got {b['citations']}"
    print("Q2 ok  -> cites", b["citations"], "| conf", b["confidence"])

    c = rag.answer("What is the capital of France?")
    assert c["escalate"], "off-topic question should escalate"
    print("Q3 ok  -> escalated (conf", c["confidence"], ")")

    assert len(rag.history) == 3, "memory should hold 3 turns"
    print("memory -> ", len(rag.history), "turns retained")
    print("\nALL PASS")


if __name__ == "__main__":
    test()
