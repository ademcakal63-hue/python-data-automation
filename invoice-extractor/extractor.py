"""
Invoice / document -> structured JSON extractor.
Two paths:
  1. LLM path (Anthropic Claude) — handles ANY layout. Needs ANTHROPIC_API_KEY.
  2. Regex fallback — no API key, extracts common fields. Always available.
"""
import os
import re
import json
import pdfplumber

# Fields we extract from an invoice
FIELDS = ["vendor", "invoice_number", "date", "due_date", "currency",
          "subtotal", "tax", "total", "line_items"]


def extract_text(file) -> str:
    """Pull raw text from a PDF (works on text-based PDFs)."""
    parts = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            parts.append(page.extract_text() or "")
    return "\n".join(parts).strip()


def extract_with_llm(text: str) -> dict:
    """Layout-agnostic extraction via Claude. Returns a dict."""
    import anthropic  # imported lazily so the regex path works without the dep

    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env
    schema = ", ".join(FIELDS)
    prompt = (
        "You extract structured data from invoices. "
        "Return ONLY valid JSON (no prose, no markdown) with exactly these keys: "
        f"{schema}. line_items is a list of objects "
        "with keys: description, quantity, unit_price, amount. "
        "Use null for anything not present. Numbers as numbers, dates as YYYY-MM-DD when possible.\n\n"
        "INVOICE TEXT:\n" + text
    )
    resp = client.messages.create(
        model="claude-haiku-4-5-20251001",   # cheap + capable; switch to claude-sonnet-4-6 for harder docs
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = resp.content[0].text.strip()
    # strip accidental code fences
    raw = re.sub(r"^```(?:json)?|```$", "", raw, flags=re.MULTILINE).strip()
    return json.loads(raw)


def _find(pattern, text, group=1, flags=re.I):
    m = re.search(pattern, text, flags)
    return m.group(group).strip() if m else None


def _line_amount(text, label_re):
    """Last numeric amount on the first line matching label_re, ignoring percentages like '20%'."""
    for ln in text.splitlines():
        if re.search(label_re, ln, re.I):
            cleaned = re.sub(r"\d+\s*%", "", ln)            # drop percentages
            nums = re.findall(r"[0-9][0-9.,]*[0-9]", cleaned)
            if nums:
                return nums[-1]
    return None


def extract_with_regex(text: str) -> dict:
    """No-API-key heuristic extraction of the most common invoice fields."""
    lines = [l for l in text.splitlines() if l.strip()]

    # total: prefer grand/genel total; else the largest 'total' amount that is NOT a subtotal
    total = _line_amount(text, r"grand\s*total|genel\s*toplam")
    if not total:
        cands = []
        for ln in lines:
            if re.search(r"(?<![a-z])(?:total|toplam)", ln, re.I) and not re.search(r"sub\s*-?\s*total|ara\s*toplam", ln, re.I):
                cleaned = re.sub(r"\d+\s*%", "", ln)
                cands += re.findall(r"[0-9][0-9.,]*[0-9]", cleaned)
        if cands:
            total = max(cands, key=lambda x: float(x.replace(",", "")))

    return {
        "vendor": (lines[0].strip() if lines else None),
        "invoice_number": _find(r"(?:invoice|fatura)\s*(?:no|number|#|:)?\s*[:#]?\s*([A-Z0-9][A-Z0-9\-\/]+)", text),
        "date": _find(r"(?<!due\s)(?:date|tarih)\s*[:#]?\s*([0-9]{1,4}[\.\-\/][0-9]{1,2}[\.\-\/][0-9]{1,4})", text),
        "due_date": _find(r"(?:due\s*date|vade)\s*[:#]?\s*([0-9]{1,4}[\.\-\/][0-9]{1,2}[\.\-\/][0-9]{1,4})", text),
        "currency": _find(r"\b(USD|EUR|TRY|GBP|TL)\b", text) or _find(r"([\$€£])", text),
        "subtotal": _line_amount(text, r"sub\s*-?\s*total|ara\s*toplam"),
        "tax": _line_amount(text, r"\b(?:tax|vat|kdv)\b"),
        "total": total,
        "line_items": [],
    }


def extract_invoice(file):
    """
    Returns (data: dict, method: str).
    Uses the LLM path if ANTHROPIC_API_KEY is set, else the regex fallback.
    """
    text = extract_text(file)
    if not text:
        return {"error": "No selectable text found (scanned image?). OCR needed."}, "none"
    if os.getenv("ANTHROPIC_API_KEY"):
        try:
            return extract_with_llm(text), "llm (Claude)"
        except Exception as e:  # noqa
            return {**extract_with_regex(text), "_llm_error": str(e)}, "regex (llm failed)"
    return extract_with_regex(text), "regex (no API key)"


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python extractor.py <invoice.pdf>")
        sys.exit(1)
    with open(sys.argv[1], "rb") as f:
        result, method = extract_invoice(f)
    print(f"# method: {method}\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))
