# Lead-gen

This repository contains a scaffold for a lead-generation and signals ingestion platform focused on Meta Lead Ads (webhook + Graph API) and public/licensed signals (NOAA/NWS, Socrata municipal permits).

What's included:
- FastAPI webhook endpoint for Meta Lead Ads (app/main.py)
- Connector abstractions and example connectors for Socrata and NWS (app/connectors)
- SQLAlchemy models (app/models.py)
- Celery background worker and tasks to fetch lead details and persist (app/tasks.py)
- Dockerfile and docker-compose for local development
- requirements.txt

Security note: This scaffold does NOT include any secrets or tokens. Add PAGE access tokens and APP secrets via environment variables or a secure secret store.

Next steps:
- Add alembic migrations
- Wire a secret store (Vault or GitHub Secrets) for Page tokens
- Configure production deployment and CI

Run locally (quick demo):
1. Copy .env.example -> .env and fill values
2. docker-compose up --build
3. Test webhook verification: curl "http://localhost:8000/webhook/meta-leads?hub.mode=subscribe&hub.verify_token=change_me&hub.challenge=12345"
