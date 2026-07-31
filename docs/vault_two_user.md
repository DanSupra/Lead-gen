Vault setup for two-user deployment

This document describes a minimal Vault setup suitable for a small two-operator deployment.

Assumptions
- You have a Vault server accessible to the application and operators (HA recommended).
- Operators have administrative access to Vault for initial setup.

Steps
1) Install Vault (or use managed Vault) and enable KV v2 at path `secret/`:
   vault secrets enable -path=secret kv-v2

2) Create a policy for the application to read secrets under `secret/leadgen`:
   cat <<EOF > app-policy.hcl
   path "secret/data/leadgen/*" {
     capabilities = ["read"]
   }
   EOF

   vault policy write app-policy app-policy.hcl

3) Create a policy for operators (rotate tokens, write secrets):
   cat <<EOF > operator-policy.hcl
   path "secret/data/leadgen/*" {
     capabilities = ["create", "read", "update", "delete"]
   }
   EOF

   vault policy write operator-policy operator-policy.hcl

4) Create tokens or AppRole for the app and operators:
   # Operator token (long lived or use OIDC)
   vault token create -policy=operator-policy -orphan

   # App token or AppRole (short-lived)
   vault token create -policy=app-policy -orphan

5) Seed example secrets:
   ./scripts/vault_seed.sh

6) Application configuration:
   - Set VAULT_ADDR and VAULT_TOKEN (or use AppRole) in your environment for the app.
   - The SecretManager in app/secrets.py will read secrets from Vault when configured.

Security notes
- Rotate operator tokens regularly and prefer AppRole/OIDC-based auth for the app.
- Audit Vault access and enable mlock and eviction policies per your compliance needs.
