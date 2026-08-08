const axios = require('axios');
const fs = require('fs-extra');
const path = require('path');
const moment = require('moment');
require('dotenv').config();
const yargs = require('yargs/yargs')(process.argv.slice(2));

const argv = yargs
  .option('page-id', {
    description: 'Facebook Page ID to scrape',
    type: 'string',
    alias: 'p'
  })
  .option('pages', {
    description: 'Comma-separated list of page IDs',
    type: 'string'
  })
  .option('since', {
    description: 'Start date (YYYY-MM-DD)',
    type: 'string'
  })
  .option('until', {
    description: 'End date (YYYY-MM-DD)',
    type: 'string'
  })
  .option('limit', {
    description: 'Max posts to scrape per page',
    type: 'number',
    default: 100
  })
  .help()
  .alias('help', 'h').argv;

class FacebookScraper {
  constructor() {
    this.accessToken = process.env.FACEBOOK_ACCESS_TOKEN;
    this.apiVersion = 'v18.0';
    this.baseUrl = `https://graph.facebook.com/${this.apiVersion}`;
    this.outputDir = process.env.OUTPUT_DIR || './output';
    this.delayMs = parseInt(process.env.DELAY_MS) || 1000;
    this.maxRetries = parseInt(process.env.MAX_RETRIES) || 3;

    if (!this.accessToken) {
      throw new Error('FACEBOOK_ACCESS_TOKEN not set in .env file');
    }

    fs.ensureDirSync(this.outputDir);
  }

  async delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  async makeRequest(url, retries = 0) {
    try {
      const response = await axios.get(url, {
        timeout: parseInt(process.env.TIMEOUT_MS) || 30000
      });
      return response.data;
    } catch (error) {
      if (retries < this.maxRetries && error.response?.status === 429) {
        console.log(`Rate limited. Retrying in ${this.delayMs * (retries + 1)}ms...`);
        await this.delay(this.delayMs * (retries + 1));
        return this.makeRequest(url, retries + 1);
      }
      throw error;
    }
  }

  async getPageInfo(pageId) {
    const url = `${this.baseUrl}/${pageId}?fields=id,name,link,picture&access_token=${this.accessToken}`;
    return this.makeRequest(url);
  }

  async getPosts(pageId, limit = 100, after = null) {
    const fields = [
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
    ].join(',');

    let url = `${this.baseUrl}/${pageId}/feed?fields=${fields}&limit=${limit}&access_token=${this.accessToken}`;

    if (after) {
      url += `&after=${after}`;
    }

    if (argv.since) {
      const sinceTimestamp = Math.floor(moment(argv.since).startOf('day').unix());
      url += `&since=${sinceTimestamp}`;
    }

    if (argv.until) {
      const untilTimestamp = Math.floor(moment(argv.until).endOf('day').unix());
      url += `&until=${untilTimestamp}`;
    }

    return this.makeRequest(url);
  }

  async getPostDetails(postId) {
    const fields = [
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
    ].join(',');

    const url = `${this.baseUrl}/${postId}?fields=${fields}&access_token=${this.accessToken}`;
    return this.makeRequest(url);
  }

  async getReactions(postId) {
    const url = `${this.baseUrl}/${postId}/reactions?fields=type&summary=true&access_token=${this.accessToken}`;
    return this.makeRequest(url);
  }

  formatPost(post, pageInfo) {
    const reactions = post.reactions?.summary || {};
    const reactionBreakdown = {};

    if (reactions.data) {
      reactions.data.forEach(reaction => {
        const key = `reaction${reaction.type.charAt(0).toUpperCase() + reaction.type.slice(1)}Count`;
        reactionBreakdown[key] = (reactionBreakdown[key] || 0) + 1;
      });
    }

    const postTime = moment(post.created_time);

    return {
      facebookUrl: pageInfo.link,
      postId: post.id.split('_')[1],
      pageName: pageInfo.name,
      url: post.permalink_url,
      time: postTime.toISOString(),
      timestamp: postTime.unix(),
      user: {
        id: pageInfo.id,
        name: pageInfo.name,
        profileUrl: `https://www.facebook.com/${pageInfo.id}`,
        profilePic: pageInfo.picture?.data?.url || ''
      },
      collaborators: [],
      text: post.message || '',
      textReferences: [],
      link: post.link || '',
      likes: post.reactions?.summary?.total_count || 0,
      comments: post.comments?.summary?.total_count || 0,
      shares: post.shares?.count || 0,
      media: [],
      feedbackId: Buffer.from(`feedback:${post.id}`).toString('base64'),
      reactionLikeCount: reactionBreakdown.reactionLikeCount || 0,
      reactionLoveCount: reactionBreakdown.reactionLoveCount || 0,
      reactionCareCount: reactionBreakdown.reactionCareCount || 0,
      reactionHahaCount: reactionBreakdown.reactionHahaCount || 0,
      reactionWowCount: reactionBreakdown.reactionWowCount || 0,
      reactionSadCount: reactionBreakdown.reactionSadCount || 0,
      reactionAngryCount: reactionBreakdown.reactionAngryCount || 0,
      topLevelUrl: `https://www.facebook.com/${post.id.replace('_', '/posts/')}`,
      facebookId: pageInfo.id,
      pageAdLibrary: {
        is_business_page_active: false,
        id: pageInfo.id
      },
      inputUrl: pageInfo.link
    };
  }

  async scrapePage(pageId, limit = 100) {
    console.log(`\n🔍 Scraping page: ${pageId}`);

    try {
      const pageInfo = await this.getPageInfo(pageId);
      console.log(`✓ Page info retrieved: ${pageInfo.name}`);

      const posts = [];
      let after = null;
      let iteration = 0;
      const maxIterations = Math.ceil(limit / 25);

      while (posts.length < limit && iteration < maxIterations) {
        console.log(`  Fetching batch ${iteration + 1}...`);

        const feedData = await this.getPosts(pageId, 25, after);

        if (!feedData.data || feedData.data.length === 0) {
          break;
        }

        for (const post of feedData.data) {
          if (posts.length >= limit) break;

          try {
            const postDetails = await this.getPostDetails(post.id);
            const formattedPost = this.formatPost(postDetails, pageInfo);
            posts.push(formattedPost);
            process.stdout.write('.');
          } catch (error) {
            console.error(`\n  Error processing post ${post.id}: ${error.message}`);
          }

          await this.delay(this.delayMs);
        }

        after = feedData.paging?.cursors?.after;
        iteration++;

        if (!after) break;
      }

      console.log(`\n✓ Scraped ${posts.length} posts from ${pageInfo.name}`);
      return { pageInfo, posts };
    } catch (error) {
      console.error(`✗ Error scraping page ${pageId}: ${error.message}`);
      throw error;
    }
  }

  async savePosts(pageInfo, posts) {
    const timestamp = moment().format('YYYY-MM-DD_HH-mm-ss');
    const filename = `${pageInfo.name.replace(/\s+/g, '_')}_${timestamp}.json`;
    const filepath = path.join(this.outputDir, filename);

    await fs.writeJSON(filepath, posts, { spaces: 2 });
    console.log(`💾 Saved to: ${filepath}`);
    return filepath;
  }

  async run() {
    try {
      const pageIds = argv['page-id'] 
        ? [argv['page-id']]
        : argv.pages 
        ? argv.pages.split(',').map(id => id.trim())
        : [process.env.FACEBOOK_PAGE_ID];

      if (!pageIds || pageIds.length === 0) {
        throw new Error('No page IDs provided. Use --page-id or --pages option or set FACEBOOK_PAGE_ID in .env');
      }

      const limit = argv.limit || 100;

      for (const pageId of pageIds) {
        const { pageInfo, posts } = await this.scrapePage(pageId, limit);
        await this.savePosts(pageInfo, posts);
      }

      console.log('\n✅ Scraping complete!');
    } catch (error) {
      console.error('\n❌ Fatal error:', error.message);
      process.exit(1);
    }
  }
}

// Run the scraper
const scraper = new FacebookScraper();
scraper.run();
