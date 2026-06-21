# Client Reporting Automation — Ad CSV → Branded Report

The monthly client report every ad/SEO agency assembles **by hand**: export the numbers, calculate KPIs, format a deck, write a summary. This does it in one command — drop a CSV, get a **client-ready branded HTML report** with KPIs, per-campaign breakdown, and an optional AI-written summary.

## Run

```bash
pip install -r requirements.txt          # only needed for the AI summary
python report.py sample_ads.csv "Acme Agency"
# -> writes report.html  (open in a browser / print to PDF)
```

No API key → KPIs, cards, and campaign table render fine. Set `ANTHROPIC_API_KEY` to add the plain-language summary paragraph.

## Input
A CSV with any of: `date, campaign, spend, clicks, impressions, conversions, revenue`. Export it from Google Ads, Meta Ads Manager, or GA4 — column names are flexible.

## Output (computed)
Spend · Clicks · Impressions · Conversions · Revenue · **CTR · CPC · CPA · ROAS · Conv. rate**, plus a per-campaign table sorted by spend, all in a branded dark report you can hand to the client or print to PDF.

## Roadmap
- Direct Google Ads / Meta / GA4 API pulls (no manual export)
- White-label: agency logo + colors per client
- Scheduled monthly auto-send (email/WhatsApp)
- Month-over-month deltas + charts
