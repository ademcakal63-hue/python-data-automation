"""
Paginated catalog scraper -> CSV + JSON.
Demo target: books.toscrape.com (a sandbox site built for legal scraping practice).
Swap the selectors + BASE to point it at any product/listing site.

Run:  python scraper.py            # all pages
      python scraper.py 5          # first 5 pages
"""
import csv
import json
import re
import sys
import time
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

BASE = "https://books.toscrape.com/catalogue/"
START = "https://books.toscrape.com/catalogue/page-1.html"
RATING = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def parse_page(html: str):
    soup = BeautifulSoup(html, "html.parser")
    items = []
    for art in soup.select("article.product_pod"):
        price_el = art.select_one(".price_color")
        price_str = price_el.get_text(strip=True) if price_el else ""
        price = float(re.sub(r"[^0-9.]", "", price_str)) if price_str else None

        title_a = getattr(art.h3, "a", None) if art.h3 else None
        title = title_a["title"] if title_a and title_a.has_attr("title") else None

        avail_el = art.select_one(".availability")
        availability = avail_el.get_text(strip=True) if avail_el else None

        star_el = art.select_one(".star-rating")
        rating_cls = [c for c in star_el.get("class", []) if c != "star-rating"] if star_el else []

        items.append({
            "title": title,
            "price": price,
            "availability": availability,
            "rating": RATING.get(rating_cls[0]) if rating_cls else None,
        })
    nxt = soup.select_one("li.next a")
    next_url = urljoin(BASE, nxt["href"]) if nxt and nxt.has_attr("href") else None
    return items, next_url


def scrape(max_pages: int = 100, delay: float = 0.3):
    url, all_items, n = START, [], 0
    sess = requests.Session()
    sess.headers["User-Agent"] = "demo-scraper/1.0 (+portfolio)"
    while url and n < max_pages:
        r = sess.get(url, timeout=20)
        r.raise_for_status()
        items, url = parse_page(r.text)
        all_items.extend(items)
        n += 1
        print(f"page {n}: +{len(items)} (total {len(all_items)})")
        time.sleep(delay)  # be polite
    return all_items


def save(items, base="books"):
    with open(f"{base}.json", "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)
    with open(f"{base}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["title", "price", "availability", "rating"])
        w.writeheader()
        w.writerows(items)


if __name__ == "__main__":
    pages = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    rows = scrape(max_pages=pages)
    save(rows)
    print(f"Done: {len(rows)} items -> books.csv + books.json")
