"""
Client Reporting Automation: ad-performance CSV -> KPIs -> branded HTML report (+ optional AI summary).
The monthly client report every ad/SEO agency builds by hand. Drop a CSV, get a client-ready report.
Works with no API key (KPIs + tables). Set ANTHROPIC_API_KEY for an AI-written summary.
"""
import os
import sys
import csv
import json


def load(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def num(x):
    try:
        return float(str(x).replace(",", "").replace("$", "").replace("₺", "").strip() or 0)
    except ValueError:
        return 0.0


def kpis(rows):
    spend = sum(num(r.get("spend")) for r in rows)
    clicks = sum(num(r.get("clicks")) for r in rows)
    impr = sum(num(r.get("impressions")) for r in rows)
    conv = sum(num(r.get("conversions")) for r in rows)
    rev = sum(num(r.get("revenue")) for r in rows)
    return {
        "spend": round(spend, 2), "clicks": int(clicks), "impressions": int(impr),
        "conversions": int(conv), "revenue": round(rev, 2),
        "ctr_pct": round(clicks / impr * 100, 2) if impr else 0,
        "cpc": round(spend / clicks, 2) if clicks else 0,
        "cpa": round(spend / conv, 2) if conv else 0,
        "roas": round(rev / spend, 2) if spend else 0,
        "conv_rate_pct": round(conv / clicks * 100, 2) if clicks else 0,
    }


def by_campaign(rows):
    agg = {}
    for r in rows:
        a = agg.setdefault(r.get("campaign", "-"), {"spend": 0.0, "clicks": 0.0, "conversions": 0.0})
        a["spend"] += num(r.get("spend"))
        a["clicks"] += num(r.get("clicks"))
        a["conversions"] += num(r.get("conversions"))
    return agg


def ai_summary(k):
    if not os.getenv("ANTHROPIC_API_KEY"):
        return None
    import anthropic
    client = anthropic.Anthropic()
    r = client.messages.create(
        model="claude-haiku-4-5-20251001", max_tokens=300,
        messages=[{"role": "user", "content":
                   "Write a 3-sentence client-facing summary of this month's ad performance "
                   f"in plain, positive-but-honest language. Data: {k}"}],
    )
    return r.content[0].text.strip()


def html(k, camps, brand, summary):
    card = lambda label, val: f'<div class="c"><div class="v">{val}</div><div class="l">{label}</div></div>'
    cards = "".join([
        card("Spend", f"${k['spend']:,.0f}"), card("Clicks", f"{k['clicks']:,}"),
        card("Conversions", f"{k['conversions']:,}"), card("ROAS", f"{k['roas']}x"),
        card("CPA", f"${k['cpa']}"), card("CTR", f"{k['ctr_pct']}%"),
    ])
    rows = "".join(
        f"<tr><td>{c}</td><td>${v['spend']:,.0f}</td><td>{int(v['clicks']):,}</td>"
        f"<td>{int(v['conversions']):,}</td><td>${(v['spend']/v['conversions']) if v['conversions'] else 0:,.0f}</td></tr>"
        for c, v in sorted(camps.items(), key=lambda x: -x[1]["spend"])
    )
    summ = f'<div class="sum"><b>Summary</b><p>{summary}</p></div>' if summary else ""
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>{brand} — Performance Report</title>
<style>
body{{font-family:Inter,system-ui,sans-serif;background:#0b0d11;color:#eceef2;margin:0;padding:40px}}
.wrap{{max-width:900px;margin:0 auto}}
h1{{font-size:26px;margin:0 0 4px}} .mut{{color:#9aa1ad;margin-bottom:28px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:14px;margin-bottom:28px}}
.c{{background:#14171e;border:1px solid #232834;border-radius:14px;padding:18px}}
.v{{font-size:26px;font-weight:700;color:#5b8cff}} .l{{color:#9aa1ad;font-size:13px;margin-top:4px}}
table{{width:100%;border-collapse:collapse;background:#14171e;border:1px solid #232834;border-radius:14px;overflow:hidden}}
th,td{{padding:12px 14px;text-align:left;border-bottom:1px solid #232834;font-size:14px}}
th{{color:#9aa1ad;font-weight:600}} .sum{{background:#14171e;border:1px solid #232834;border-radius:14px;padding:20px;margin-bottom:24px}}
.sum p{{color:#c6ccd6;margin:8px 0 0}}
</style></head><body><div class="wrap">
<h1>{brand}</h1><div class="mut">Monthly Performance Report</div>
{summ}<div class="grid">{cards}</div>
<table><thead><tr><th>Campaign</th><th>Spend</th><th>Clicks</th><th>Conv.</th><th>CPA</th></tr></thead><tbody>{rows}</tbody></table>
</div></body></html>"""


def build(csv_path, brand="Your Agency", out="report.html"):
    rows = load(csv_path)
    k = kpis(rows)
    with open(out, "w", encoding="utf-8") as f:
        f.write(html(k, by_campaign(rows), brand, ai_summary(k)))
    return k, out


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "sample_ads.csv"
    brand = sys.argv[2] if len(sys.argv) > 2 else "Acme Agency"
    k, out = build(path, brand)
    print(json.dumps(k, indent=2))
    print("report ->", out)
