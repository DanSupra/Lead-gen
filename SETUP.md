# Setup Guide

## Step 1: Create Facebook App

1. Go to [Facebook Developers](https://developers.facebook.com)
2. Click "My Apps" → "Create App"
3. Choose "Business" type
4. Fill in app details and create

## Step 2: Get Page Access Token

1. In your app dashboard, go to "Settings" → "Basic"
2. Copy your **App ID** and **App Secret**
3. Go to "Tools" → "Graph API Explorer"
4. Select your app from dropdown
5. Change from "User Token" to "Page Access Token"
6. Select the page you want to scrape
7. Add permissions: `pages_read_engagement`, `pages_read_user_content`
8. Generate the token and copy it

### Getting a Long-Lived Token (Recommended)

Long-lived tokens last 60 days and are better for automated scraping.

```bash
# Replace with your values
curl -i -X GET "https://graph.facebook.com/oauth/access_token?
  grant_type=fb_exchange_token&
  client_id=YOUR_APP_ID&
  client_secret=YOUR_APP_SECRET&
  fb_exchange_token=SHORT_LIVED_TOKEN"
```

## Step 3: Get Your Page ID

1. Go to your Facebook page
2. Click "About" section
3. Scroll to find "Page ID" at the bottom
4. Or, use the Graph API: `https://graph.facebook.com/me?access_token=YOUR_TOKEN`

## Step 4: Configuration

### Node.js Setup

```bash
# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Edit .env with your credentials
FACEBOOK_ACCESS_TOKEN=your_long_lived_token
FACEBOOK_PAGE_ID=your_page_id
```

### Python Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with your credentials
FACEBOOK_ACCESS_TOKEN=your_long_lived_token
FACEBOOK_PAGE_ID=your_page_id
```

## Step 5: Run Scraper

### Node.js

```bash
# Scrape your default page
node scraper.js

# Scrape specific page
node scraper.js --page-id YOUR_PAGE_ID

# Scrape with date range
node scraper.js --page-id YOUR_PAGE_ID --since 2026-01-01 --until 2026-01-31

# Scrape multiple pages
node scraper.js --pages PAGE_ID1,PAGE_ID2,PAGE_ID3

# Limit number of posts
node scraper.js --limit 50
```

### Python

```bash
# Scrape your default page
python scraper.py

# Scrape specific page
python scraper.py --page-id YOUR_PAGE_ID

# Scrape with date range
python scraper.py --page-id YOUR_PAGE_ID --since 2026-01-01 --until 2026-01-31

# Scrape multiple pages
python scraper.py --pages PAGE_ID1,PAGE_ID2,PAGE_ID3

# Limit number of posts
python scraper.py --limit 50
```

## Troubleshooting

### "Invalid access token"

- Token may have expired
- Go back to Graph API Explorer and generate a new one
- Make sure you're using a **long-lived token** (not a short-lived one)

### "User does not have permission"

- Check token has `pages_read_engagement` and `pages_read_user_content` permissions
- Make sure token is for a page admin account
- Regenerate token and try again

### "Page not found"

- Double-check the Page ID is correct
- Ensure you have access to this page
- Page ID should be numeric only

### Rate Limiting

- The scraper includes automatic retry logic with exponential backoff
- Default delay between requests is 1 second (adjustable in `.env`)
- Facebook has limits: typically 200 calls per hour for most endpoints

### Permission Errors

Required token permissions:
- `pages_read_engagement` - Read post insights and reactions
- `pages_read_user_content` - Read posts and comments
- `instagram_basic` - If scraping Instagram (future enhancement)

Add permissions in App Settings → Permissions & Features

## Output Format

Data is saved to `output/` directory as JSON files:

```
output/
├── YourPageName_2026-01-20_14-30-45.json
└── AnotherPage_2026-01-20_15-45-30.json
```

Each file contains an array of posts matching the schema.

## Security

- **Never commit `.env` file** to version control
- Use long-lived tokens (60 days) for production use
- Rotate tokens periodically
- Use environment variables for sensitive data
- Consider using a secrets manager for production

## Advanced Options

Edit `.env` to customize:

```
OUTPUT_DIR=./output          # Where to save data
OUTPUT_FORMAT=json           # Output format
BATCH_SIZE=25                # Posts per API call
DELAY_MS=1000                # Milliseconds between requests
MAX_RETRIES=3                # Retry attempts on rate limit
TIMEOUT_MS=30000             # Request timeout
```

## Next Steps

- Set up automated cron jobs to run scraper regularly
- Integrate with a database for storing posts
- Add sentiment analysis or keyword extraction
- Set up monitoring and alerts for scraping errors
