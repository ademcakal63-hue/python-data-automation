# Python Data Extraction & Automation — Demos

Working demos I build for clients: turning messy / unstructured data into clean, structured output, and wiring up the automations that move it. Every demo runs — most work with **no API key** (transparent fallback) and light up further with Claude.

### 1. Invoice / Document → JSON · [`invoice-extractor/`](invoice-extractor/)
Drop a PDF invoice → structured JSON (vendor, number, dates, subtotal, tax, total, line items). Claude for any layout + a regex fallback that needs no API key. Streamlit upload UI.

### 2. Web Scraper → CSV / JSON · [`web-scraper/`](web-scraper/)
Paginated product catalog → clean CSV + JSON (title, price, availability, rating). `requests` + `BeautifulSoup`, auto-pagination. Swap the selectors for any site.

### 3. Messy CSV → Clean DB + API · [`csv-etl/`](csv-etl/)
Ugly spreadsheet (dupes, bad casing, `$1,200`, mixed dates) → normalized SQLite + a FastAPI query service. `pandas`.

### 4. Document RAG Chatbot → Cited Answers · [`rag-chatbot/`](rag-chatbot/)
Upload documents (PDF / MD / TXT) → ask questions → **answers grounded in your docs with source citations + a confidence score**. Low confidence → escalates instead of hallucinating. Conversation memory for follow-ups. Real pipeline: chunk → embed → vector search → grounded answer. Pluggable backends (TF-IDF/OpenAI/local embeddings · Claude/OpenAI/extractive generation), runs with **no key**. Streamlit chat UI + CLI + 3 sample knowledge bases (support / product / policy).

### 5. Lead Automation → Qualify + CRM + Notify · [`lead-automation/`](lead-automation/)
Inbound lead (form / Meta Lead Ad / WhatsApp) hits a webhook → **qualified (hot/warm/cold + score)** → stored → notification fired. FastAPI endpoint, Claude or rules fallback. The "trigger → AI → store + notify" pattern.

### 6. Client Reporting Automation → Branded Report · [`ad-reporting/`](ad-reporting/)
Ad-performance CSV (Google Ads / Meta / GA4) → **client-ready branded HTML report**: KPIs (CTR, CPC, CPA, ROAS), per-campaign breakdown, optional AI-written summary. The monthly report agencies build by hand, in one command.

### 7. AI Content Generator → SEO Content Pack · [`ai-content/`](ai-content/)
Product name + features + keyword → **meta title, meta description, product description, feature bullets**. Built for generating content across hundreds of SKUs. Template fallback (no key) + Claude copy.

Each folder has its own README and run steps.

---

**Send me a sample — an invoice, a URL, a CSV, or an ad export — and I'll return the structured output before you commit.**
