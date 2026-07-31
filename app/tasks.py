from celery import Celery
import os
import requests
from app.connectors.meta import MetaWebhookHandler
from app.models import Lead
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json

CELERY_BROKER = os.getenv("CELERY_BROKER", "redis://redis:6379/0")
CELERY_BACKEND = os.getenv("CELERY_BACKEND", "redis://redis:6379/1")
app = Celery("tasks", broker=CELERY_BROKER, backend=CELERY_BACKEND)
GRAPH_API_VERSION = os.getenv("GRAPH_API_VERSION", "v17.0")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/postgres")
engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine)

meta_handler = MetaWebhookHandler()

@app.task(bind=True, max_retries=3)
def process_lead_event(self, lead_info):
    # lead_info: {"leadgen_id": "123", "page_id":"..."}
    page_id = lead_info.get("page_id")
    lead_id = lead_info.get("leadgen_id")
    # Get page token from config store (DB or Vault)
    page_token = os.getenv(f"PAGE_TOKEN_{page_id}")
    if not page_token:
        # TODO: retrieve from secure store; if missing, log and return
        return {"error": "no page token"}
    url = meta_handler.build_graph_url(lead_id, page_token)
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    lead_data = r.json()
    # Extract fields
    form_fields = {f.get("name"): f.get("values") for f in lead_data.get("field_data", [])}
    # Simple mapping
    first = form_fields.get("first_name", [None])[0]
    last = form_fields.get("last_name", [None])[0]
    phone = form_fields.get("phone_number", [None])[0]
    email = form_fields.get("email", [None])[0]
    # persist
    db = SessionLocal()
    lead = Lead(
        leadgen_id=lead_id,
        page_id=page_id,
        form_id=lead_data.get("form_id"),
        raw_payload=lead_data,
        first_name=first,
        last_name=last,
        phone=phone,
        email=email,
        source="meta"
    )
    db.add(lead)
    db.commit()
    db.close()
    return {"status": "saved", "lead_id": lead.leadgen_id}
