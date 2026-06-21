"""
CLI: load a docs folder, ask one question, or chat interactively (with memory).

    python cli.py samples/support "I was charged twice"
    python cli.py samples/support           # interactive chat
"""
import sys
import json
from rag_core import RAG


def main():
    folder = sys.argv[1] if len(sys.argv) > 1 else "samples/support"
    rag = RAG().ingest_dir(folder)
    print("backend:", rag.backend)

    if len(sys.argv) > 2:
        print(json.dumps(rag.answer(" ".join(sys.argv[2:])), indent=2, ensure_ascii=False))
        return

    print("\nChat - blank line to quit. Conversation memory is on.\n")
    while True:
        try:
            q = input("you> ").strip()
        except EOFError:
            break
        if not q:
            break
        out = rag.answer(q)
        tag = "ESCALATE" if out["escalate"] else f"sources: {', '.join(out['citations'])}"
        print(f"\nbot> {out['answer']}\n     [confidence {out['confidence']} | {tag}]\n")


if __name__ == "__main__":
    main()
