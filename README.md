# Lead-gen - Facebook Page Scraper

This repository contains both a lead-generation platform scaffold and a Facebook Page Scraper tool.

## 📦 Facebook Page Scraper

A Node.js/Python-based scraper to collect data from your own Facebook page(s).

### Features

- ✅ Scrapes posts from Facebook pages you own or have access to
- ✅ Extracts post text, media, reactions, comments, and shares
- ✅ Handles hashtags and external links in posts
- ✅ Stores data in JSON format matching industry standards
- ✅ Supports batch scraping of multiple pages
- ✅ Built-in rate limiting and error handling

### Quick Start

**Installation:**
```bash
# Windows
install.bat

# macOS/Linux
bash install.sh
```

**Configuration:**
```bash
cp .env.example .env
# Edit .env with your Facebook credentials
```

**Usage:**
```bash
# Node.js
node scraper.js --page-id YOUR_PAGE_ID --limit 100

# Python
python scraper.py --page-id YOUR_PAGE_ID --limit 100
```

### Detailed Setup

See [SETUP.md](./SETUP.md) for:
- How to create a Facebook App
- Getting access tokens
- Finding your Page ID
- Troubleshooting common issues
- Advanced configuration options

### Output Format

Scraped data is saved as JSON with the following schema:
```json
{
  "facebookUrl": "string",
  "postId": "string",
  "pageName": "string",
  "url": "string",
  "time": "ISO 8601 timestamp",
  "timestamp": "Unix timestamp",
  "user": {...},
  "text": "string",
  "likes": 146,
  "comments": 3,
  "shares": 27,
  "media": [],
  "reactionLikeCount": 135,
  "reactionLoveCount": 8,
  ...
}
```

### Commands

```bash
# Single page
node scraper.js --page-id PAGE_ID
python scraper.py --page-id PAGE_ID

# Multiple pages
node scraper.js --pages PAGE_ID1,PAGE_ID2,PAGE_ID3
python scraper.py --pages PAGE_ID1,PAGE_ID2,PAGE_ID3

# With date range
node scraper.js --page-id PAGE_ID --since 2026-01-01 --until 2026-01-31
python scraper.py --page-id PAGE_ID --since 2026-01-01 --until 2026-01-31

# Limit posts
node scraper.js --page-id PAGE_ID --limit 50
python scraper.py --page-id PAGE_ID --limit 50

# Validate configuration
node validate.js
python validate.py
```

---

## 🚀 Lead Generation Platform Scaffold

The original lead-generation platform scaffold for Meta Lead Ads and public signals.

**What's included:**
- FastAPI webhook endpoint for Meta Lead Ads (app/main.py)
- Connector abstractions and example connectors (app/connectors)
- SQLAlchemy models (app/models.py)
- Celery background worker and tasks (app/tasks.py)
- Docker configuration for local development
- requirements.txt

**Security note:** This scaffold does NOT include secrets or tokens. Use environment variables or a secure secret store.

**Quick start:**
1. `cp .env.example .env` and fill in values
2. `docker-compose up --build`
3. Test: `curl "http://localhost:8000/webhook/meta-leads?hub.mode=subscribe&hub.verify_token=change_me&hub.challenge=12345"`

---

## 📋 Repository Structure

```
lead-gen/
├── scraper.js              # Node.js scraper
├── scraper.py              # Python scraper
├── validate.js             # Node.js config validator
├── validate.py             # Python config validator
├── install.sh              # Unix/Linux installation
├── install.bat             # Windows installation
├── .env.example            # Configuration template
├── package.json            # Node.js dependencies
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── SETUP.md                # Detailed setup guide
├── app/                    # Lead generation platform (original)
├── docker-compose.yml      # Docker configuration
└── output/                 # Scraped data (created at runtime)
```

---

## ⚖️ Legal & Compliance

- Only scrape your own pages or pages with explicit permission
- Comply with Facebook's Terms of Service
- Respect privacy laws (GDPR, CCPA, etc.)
- Be mindful of API rate limits
- This tool is for personal/research use

---

## 📝 License

MIT
