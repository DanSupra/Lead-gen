#!/bin/bash
# Vault seeding script (example)
# Usage: VAULT_ADDR=https://vault.example.com VAULT_TOKEN=... ./scripts/vault_seed.sh
set -euo pipefail

if [ -z "${VAULT_ADDR+x}" ] || [ -z "${VAULT_TOKEN+x}" ]; then
  echo "VAULT_ADDR and VAULT_TOKEN must be set"
  exit 1
fi

# Example: write a page token secret at secret/data/leadgen/PAGE_TOKEN_1234567890
vault kv put secret/leadgen PAGE_TOKEN_1234567890="your_page_token_here"

# Example: write META_APP_SECRET
vault kv put secret/leadgen META_APP_SECRET="your_meta_app_secret_here"

echo "Seeded example secrets to Vault path secret/leadgen"
