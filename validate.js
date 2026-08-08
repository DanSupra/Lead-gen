#!/usr/bin/env node

/**
 * Utility script to validate configuration
 */

const fs = require('fs');
const path = require('path');
require('dotenv').config();

console.log('🔍 Validating Facebook Scraper Configuration...\n');

let hasErrors = false;

// Check for required environment variables
const requiredVars = ['FACEBOOK_ACCESS_TOKEN', 'FACEBOOK_PAGE_ID'];

requiredVars.forEach(varName => {
  if (!process.env[varName]) {
    console.error(`❌ Missing required environment variable: ${varName}`);
    hasErrors = true;
  } else {
    console.log(`✓ ${varName} is set`);
  }
});

// Check output directory
const outputDir = process.env.OUTPUT_DIR || './output';
if (!fs.existsSync(outputDir)) {
  console.log(`\n📁 Creating output directory: ${outputDir}`);
  fs.mkdirSync(outputDir, { recursive: true });
  console.log('✓ Output directory created');
} else {
  console.log(`✓ Output directory exists: ${outputDir}`);
}

// Check if dependencies are installed
console.log('\n📦 Checking dependencies...');
try {
  require('axios');
  console.log('✓ axios installed');
} catch (e) {
  console.error('❌ axios not found. Run: npm install');
  hasErrors = true;
}

try {
  require('moment');
  console.log('✓ moment installed');
} catch (e) {
  console.error('❌ moment not found. Run: npm install');
  hasErrors = true;
}

// Summary
console.log('\n' + (hasErrors ? '❌ Validation failed' : '✅ Validation successful'));
console.log(hasErrors ? '\nPlease fix the above errors before running the scraper.' : '\nYou are ready to run the scraper!');
console.log('\nUsage: node scraper.js [options]');
console.log('Run: node scraper.js --help for more options\n');

process.exit(hasErrors ? 1 : 0);
