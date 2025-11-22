# Security notes (development scaffold)

- Do NOT commit real API keys. Use environment variables and `.env` files excluded by `.gitignore`.
- For production, use a secrets manager (Vault, AWS Secrets Manager, GCP Secret Manager).
- Rate-limit and authenticate endpoints; do not rely on a static `DEFAULT_API_KEY` in production.
- Validate and sanitize on-chain addresses and amounts server-side.
- Use HTTPS and secure cookie/session settings for web apps.
- Rotate keys and monitor usages via auditing.
