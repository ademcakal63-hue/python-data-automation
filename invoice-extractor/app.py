"""
Streamlit UI: drop a PDF invoice -> get clean structured JSON back.
Run:  streamlit run app.py
"""
import json
import streamlit as st
from extractor import extract_invoice, extract_text

st.set_page_config(page_title="Invoice → JSON", page_icon="🧾", layout="wide")

st.title("🧾 Invoice → Structured JSON")
st.caption("Drop an invoice PDF and get clean, structured data — vendor, number, dates, totals, line items.")

file = st.file_uploader("Upload an invoice (PDF)", type=["pdf"])

if file:
    with st.spinner("Extracting…"):
        data, method = extract_invoice(file)
        file.seek(0)
        raw_text = extract_text(file)

    st.success(f"Extracted via: **{method}**")
    left, right = st.columns(2)
    with left:
        st.subheader("📄 Source text")
        st.text_area("Raw text from the PDF", raw_text, height=460, label_visibility="collapsed")
    with right:
        st.subheader("🧩 Structured JSON")
        st.json(data)
        st.download_button(
            "⬇️ Download JSON",
            data=json.dumps(data, indent=2, ensure_ascii=False),
            file_name="invoice.json",
            mime="application/json",
        )
else:
    st.info("Tip: no API key set → uses the built-in regex extractor. "
            "Set ANTHROPIC_API_KEY for layout-agnostic Claude extraction.")
