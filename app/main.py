from fastapi import FastAPI, Request, Header, HTTPException
from app.connectors.meta import MetaWebhookHandler
from app.tasks import process_lead_event
import os
import hmac
import hashlib
import json

app = FastAPI(title="Leads+Signals API")

APP_SECRET = os.getenv("META_APP_SECRET", "")
VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN", "change_me")

meta_handler = MetaWebhookHandler()

@app.get("/webhook/meta-leads")
async def meta_verify(hub_mode: str = None, hub_verify_token: str = None, hub_challenge: str = None):
    # Facebook webhook verification handshake
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return int(hub_challenge)
    raise HTTPException(status_code=403, detail="Verification token mismatch")

@app.post("/webhook/meta-leads")
async def handle_meta_webhook(request: Request, x_hub_signature: str | None = Header(None)):
    body = await request.body()
    # validate signature (support sha1 or sha256)
    if APP_SECRET:
        valid = False
        if x_hub_signature:
            # header format: sha1=... or sha256=...
            try:
                algo, signature = x_hub_signature.split("=")
                hashed = hmac.new(APP_SECRET.encode(), body, getattr(hashlib, algo))
                valid = hmac.compare_digest(hashed.hexdigest(), signature)
            except Exception:
                valid = False
        if not valid:
            raise HTTPException(status_code=401, detail="Invalid signature")
    payload = json.loads(body)
    # Enqueue processing quickly
    # Example: extract the leadgen_id(s) from payload entries
    entries = meta_handler.extract_lead_ids(payload)
    for lead in entries:
        # push to background task
        process_lead_event.delay(lead)  # Celery task
    return {"status": "ok"}

# Simple health
@app.get("/healthz")
async def health():
    return {"status": "ok"}
