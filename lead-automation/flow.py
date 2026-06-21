"""
Lead automation: incoming lead -> qualify/enrich -> store (SQLite) -> notification.
The 'trigger -> AI -> store + notify' pattern that agencies & SMBs pay for.
Uses Claude if ANTHROPIC_API_KEY is set, else a transparent rules fallback.
"""
import os
import re
import json
import sqlite3

DB = "leads.db"


def _init():
    con = sqlite3.connect(DB)
    con.execute(
        "CREATE TABLE IF NOT EXISTS leads("
        "name TEXT, email TEXT, phone TEXT, message TEXT, intent TEXT, score INTEGER, notify TEXT)"
    )
    con.commit()
    con.close()


def qualify_rules(lead: dict) -> dict:
    msg = (lead.get("message") or "").lower()
    hot_words = ["price", "quote", "buy", "fiyat", "teklif", "randevu", "urgent", "asap", "acil"]
    hot = any(w in msg for w in hot_words)
    has_contact = bool(lead.get("email") or lead.get("phone"))
    score = (50 if hot else 20) + (40 if has_contact else 0) + (10 if len(msg) > 40 else 0)
    score = min(score, 100)
    intent = "hot" if score >= 80 else "warm" if score >= 50 else "cold"
    return {"intent": intent, "score": score}


def qualify_llm(lead: dict) -> dict:
    import anthropic
    client = anthropic.Anthropic()
    prompt = (
        "Classify this inbound lead. Return ONLY JSON: "
        '{"intent": "hot|warm|cold", "score": 0-100}. '
        "hot = clear buying intent + contact info.\nLEAD:\n" + json.dumps(lead)
    )
    r = client.messages.create(
        model="claude-haiku-4-5-20251001", max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = re.sub(r"^```(?:json)?|```$", "", r.content[0].text.strip(), flags=re.M).strip()
    return json.loads(raw)


def process_lead(lead: dict) -> dict:
    _init()
    q = qualify_llm(lead) if os.getenv("ANTHROPIC_API_KEY") else qualify_rules(lead)
    contact = lead.get("email") or lead.get("phone") or "no contact"
    if q["intent"] == "hot":
        notify = f"HOT lead: {lead.get('name')} ({contact}) score {q['score']} - follow up now!"
    else:
        notify = f"New {q['intent']} lead: {lead.get('name')} ({contact}) score {q['score']}"
    con = sqlite3.connect(DB)
    con.execute(
        "INSERT INTO leads VALUES(?,?,?,?,?,?,?)",
        (lead.get("name"), lead.get("email"), lead.get("phone"), lead.get("message"),
         q["intent"], q["score"], notify),
    )
    con.commit()
    con.close()
    return {**lead, **q, "notification": notify}


if __name__ == "__main__":
    sample = {"name": "Ayse Yilmaz", "email": "ayse@example.com",
              "message": "Merhaba, fiyat teklifi almak istiyorum, acil lazim."}
    print(json.dumps(process_lead(sample), indent=2, ensure_ascii=False))
