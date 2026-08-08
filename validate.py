#!/usr/bin/env python3

"""
Utility script to validate configuration
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

print('🔍 Validating Facebook Scraper Configuration...\n')

has_errors = False

# Check for required environment variables
required_vars = ['FACEBOOK_ACCESS_TOKEN', 'FACEBOOK_PAGE_ID']

for var_name in required_vars:
    if not os.getenv(var_name):
        print(f'❌ Missing required environment variable: {var_name}')
        has_errors = True
    else:
        print(f'✓ {var_name} is set')

# Check output directory
output_dir = os.getenv('OUTPUT_DIR', './output')
if not os.path.exists(output_dir):
    print(f'\n📁 Creating output directory: {output_dir}')
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    print('✓ Output directory created')
else:
    print(f'✓ Output directory exists: {output_dir}')

# Check if dependencies are installed
print('\n📦 Checking dependencies...')
try:
    import requests
    print('✓ requests installed')
except ImportError:
    print('❌ requests not found. Run: pip install -r requirements.txt')
    has_errors = True

try:
    import dotenv
    print('✓ python-dotenv installed')
except ImportError:
    print('❌ python-dotenv not found. Run: pip install -r requirements.txt')
    has_errors = True

# Summary
print('\n' + ('❌ Validation failed' if has_errors else '✅ Validation successful'))
print('\nPlease fix the above errors before running the scraper.' if has_errors else '\nYou are ready to run the scraper!')
print('\nUsage: python scraper.py [options]')
print('Run: python scraper.py --help for more options\n')

sys.exit(1 if has_errors else 0)
