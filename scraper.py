#!/usr/bin/env python3

import os
import json
import time
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import requests
from dotenv import load_dotenv
import pytz

load_dotenv()

class FacebookScraper:
    def __init__(self):
        self.access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
        self.api_version = 'v18.0'
        self.base_url = f'https://graph.facebook.com/{self.api_version}'
        self.output_dir = os.getenv('OUTPUT_DIR', './output')
        self.delay_ms = int(os.getenv('DELAY_MS', 1000))
        self.max_retries = int(os.getenv('MAX_RETRIES', 3))
        self.timeout = int(os.getenv('TIMEOUT_MS', 30000)) / 1000

        if not self.access_token:
            raise ValueError('FACEBOOK_ACCESS_TOKEN not set in .env file')

        Path(self.output_dir).mkdir(parents=True, exist_ok=True)

    def delay(self):
        time.sleep(self.delay_ms / 1000)

    def make_request(self, url, retries=0):
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError as e:
            if retries < self.max_retries:
                print(f'Rate limited. Retrying in {self.delay_ms * (retries + 1)}ms...')
                time.sleep(self.delay_ms * (retries + 1) / 1000)
                return self.make_request(url, retries + 1)
            raise e

    def get_page_info(self, page_id):
        url = f'{self.base_url}/{page_id}?fields=id,name,link,picture&access_token={self.access_token}'
        return self.make_request(url)

    def get_posts(self, page_id, limit=100, after=None, since=None, until=None):
        fields = ','.join([
            'id',
            'created_time',
            'message',
            'type',
            'link',
            'picture',
            'full_picture',
            'permalink_url',
            'reactions.summary(total_count).limit(0)',
            'comments.summary(total_count).limit(0)',
            'shares'
        ])

        url = f'{self.base_url}/{page_id}/feed?fields={fields}&limit={limit}&access_token={self.access_token}'

        if after:
            url += f'&after={after}'

        if since:
            since_timestamp = int(datetime.strptime(since, '%Y-%m-%d').replace(
                hour=0, minute=0, second=0, tzinfo=pytz.UTC
            ).timestamp())
            url += f'&since={since_timestamp}'

        if until:
            until_timestamp = int(datetime.strptime(until, '%Y-%m-%d').replace(
                hour=23, minute=59, second=59, tzinfo=pytz.UTC
            ).timestamp())
            url += f'&until={until_timestamp}'

        return self.make_request(url)

    def get_post_details(self, post_id):
        fields = ','.join([
            'id',
            'created_time',
            'message',
            'type',
            'link',
            'picture',
            'full_picture',
            'permalink_url',
            'reactions.summary(breakdown=reaction_type).limit(0)',
            'comments.summary(total_count).limit(0)',
            'shares'
        ])

        url = f'{self.base_url}/{post_id}?fields={fields}&access_token={self.access_token}'
        return self.make_request(url)

    def format_post(self, post, page_info):
        reactions = post.get('reactions', {}).get('summary', {})
        reaction_breakdown = {}

        if reactions.get('data'):
            for reaction in reactions['data']:
                key = f"reaction{reaction['type'].capitalize()}Count"
                reaction_breakdown[key] = reaction_breakdown.get(key, 0) + 1

        post_time = datetime.fromisoformat(post['created_time'].replace('Z', '+00:00'))

        return {
            'facebookUrl': page_info['link'],
            'postId': post['id'].split('_')[1],
            'pageName': page_info['name'],
            'url': post.get('permalink_url', ''),
            'time': post_time.isoformat(),
            'timestamp': int(post_time.timestamp()),
            'user': {
                'id': page_info['id'],
                'name': page_info['name'],
                'profileUrl': f"https://www.facebook.com/{page_info['id']}",
                'profilePic': page_info.get('picture', {}).get('data', {}).get('url', '')
            },
            'collaborators': [],
            'text': post.get('message', ''),
            'textReferences': [],
            'link': post.get('link', ''),
            'likes': reactions.get('total_count', 0),
            'comments': post.get('comments', {}).get('summary', {}).get('total_count', 0),
            'shares': post.get('shares', {}).get('count', 0),
            'media': [],
            'feedbackId': __import__('base64').b64encode(f"feedback:{post['id']}".encode()).decode(),
            'reactionLikeCount': reaction_breakdown.get('reactionLikeCount', 0),
            'reactionLoveCount': reaction_breakdown.get('reactionLoveCount', 0),
            'reactionCareCount': reaction_breakdown.get('reactionCareCount', 0),
            'reactionHahaCount': reaction_breakdown.get('reactionHahaCount', 0),
            'reactionWowCount': reaction_breakdown.get('reactionWowCount', 0),
            'reactionSadCount': reaction_breakdown.get('reactionSadCount', 0),
            'reactionAngryCount': reaction_breakdown.get('reactionAngryCount', 0),
            'topLevelUrl': f"https://www.facebook.com/{post['id'].replace('_', '/posts/')}",
            'facebookId': page_info['id'],
            'pageAdLibrary': {
                'is_business_page_active': False,
                'id': page_info['id']
            },
            'inputUrl': page_info['link']
        }

    def scrape_page(self, page_id, limit=100, since=None, until=None):
        print(f'\n🔍 Scraping page: {page_id}')

        try:
            page_info = self.get_page_info(page_id)
            print(f"✓ Page info retrieved: {page_info['name']}")

            posts = []
            after = None
            iteration = 0
            max_iterations = (limit + 24) // 25

            while len(posts) < limit and iteration < max_iterations:
                print(f'  Fetching batch {iteration + 1}...')

                feed_data = self.get_posts(page_id, 25, after, since, until)

                if not feed_data.get('data') or len(feed_data['data']) == 0:
                    break

                for post in feed_data['data']:
                    if len(posts) >= limit:
                        break

                    try:
                        post_details = self.get_post_details(post['id'])
                        formatted_post = self.format_post(post_details, page_info)
                        posts.append(formatted_post)
                        print('.', end='', flush=True)
                    except Exception as e:
                        print(f'\n  Error processing post {post["id"]}: {str(e)}')

                    self.delay()

                after = feed_data.get('paging', {}).get('cursors', {}).get('after')
                iteration += 1

                if not after:
                    break

            print(f'\n✓ Scraped {len(posts)} posts from {page_info["name"]}')
            return page_info, posts

        except Exception as e:
            print(f'✗ Error scraping page {page_id}: {str(e)}')
            raise

    def save_posts(self, page_info, posts):
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = f"{page_info['name'].replace(' ', '_')}_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(posts, f, indent=2, ensure_ascii=False)

        print(f'💾 Saved to: {filepath}')
        return filepath

    def run(self, page_ids=None, limit=100, since=None, until=None):
        try:
            if not page_ids:
                page_ids = [os.getenv('FACEBOOK_PAGE_ID')]

            if not page_ids[0]:
                raise ValueError('No page IDs provided. Use --page-id/--pages option or set FACEBOOK_PAGE_ID in .env')

            for page_id in page_ids:
                page_info, posts = self.scrape_page(page_id, limit, since, until)
                self.save_posts(page_info, posts)

            print('\n✅ Scraping complete!')

        except Exception as e:
            print(f'\n❌ Fatal error: {str(e)}')
            exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scrape Facebook page data')
    parser.add_argument('--page-id', '-p', help='Facebook Page ID to scrape')
    parser.add_argument('--pages', help='Comma-separated list of page IDs')
    parser.add_argument('--limit', type=int, default=100, help='Max posts to scrape per page')
    parser.add_argument('--since', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--until', help='End date (YYYY-MM-DD)')

    args = parser.parse_args()

    page_ids = None
    if args.page_id:
        page_ids = [args.page_id]
    elif args.pages:
        page_ids = [pid.strip() for pid in args.pages.split(',')]

    scraper = FacebookScraper()
    scraper.run(page_ids, args.limit, args.since, args.until)
