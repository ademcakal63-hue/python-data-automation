# Web Scraper → CSV / JSON

Scrapes a paginated product catalog into clean **CSV + JSON** — title, price, availability, rating — following "next page" links automatically.

Demo target is **books.toscrape.com** (a sandbox site explicitly built for legal scraping practice). To use it on a real site, swap `BASE`/`START` and the CSS selectors in `parse_page()`.

## Run

```bash
pip install -r requirements.txt
python scraper.py            # all pages
python scraper.py 5          # first 5 pages only
```

Outputs `books.csv` and `books.json` in the folder.

## Built in
- Automatic pagination (follows `next` links)
- Polite: custom User-Agent + delay between requests
- Clean typed output (price → float, rating → int)
- One function to change per target site (`parse_page`)

## Roadmap
- Playwright version for JS-rendered sites
- Proxy rotation + retry/backoff for protected sites
- Scheduled runs (cron) → fresh data daily
