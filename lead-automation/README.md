# Lead Automation — Form/Ad Lead → Qualify → CRM + Notify

The bread-and-butter automation: an inbound lead (website form, Meta Lead Ad, WhatsApp) hits a webhook → gets **qualified (hot/warm/cold + score)** → stored in a CRM/database → a **notification** is fired so a hot lead never sits cold.

This is the "trigger → AI → store + notify" pattern agencies resell and SMBs pay a retainer for.

## Run

```bash
pip install -r requirements.txt
python flow.py                       # process a sample lead
uvicorn app:app --reload             # live webhook at /webhook
```

POST a lead:
```bash
curl -X POST http://127.0.0.1:8000/webhook -H "Content-Type: application/json" \
  -d '{"name":"Ayse","email":"a@x.com","message":"fiyat teklifi istiyorum, acil"}'
```

## How it works
| Step | |
|------|--|
| Trigger | webhook (form / Meta Lead Ads / Typeform / WhatsApp) |
| Qualify | Claude (intent + score) — or a no-key rules fallback |
| Store | SQLite (swap for HubSpot/Sheets/any CRM) |
| Notify | message string (wire to Slack/WhatsApp/email) |

## Roadmap
- Real CRM connectors (HubSpot, Pipedrive, Google Sheets)
- Slack / WhatsApp / email delivery of the notification
- Auto-reply to the lead in their language
