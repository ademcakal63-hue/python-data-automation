"""
FastAPI webhook: POST a lead -> qualified + stored + notification returned.
Run:  uvicorn app:app --reload   (POST JSON to http://127.0.0.1:8000/webhook)
Connect a website form / Meta Lead Ads / Typeform webhook to this endpoint.
"""
from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
from flow import process_lead

app = FastAPI(title="Lead Automation", description="Form/ad lead -> AI qualify -> CRM + notify")


class Lead(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    message: Optional[str] = None


@app.post("/webhook")
def webhook(lead: Lead):
    return process_lead(lead.model_dump())
