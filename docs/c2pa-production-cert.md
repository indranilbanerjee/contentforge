# C2PA Production Signing Certificate

**Master guide:** lives in the DMP repo at `digital-marketing-pro/docs/c2pa-production-cert-guide.md` — read that first.
**Short version for ContentForge users below.**

## TL;DR

`scripts/generate-docx.py --c2pa-sign` ships with a dev-only path that auto-generates a 90-day self-signed certificate. Production deployment requires a certificate from a **CAI-recognized signing authority**. The dev cert path signs successfully and the sidecar `.c2pa.json` parses correctly, but it verifies as "signer not in trust list" at contentcredentials.org/verify and won't pass EU AI Act Article 50 review for AI-assisted long-form text on matters of public interest.

## Four recognized authorities (May 2026)

| Option | Best for | Cost |
|---|---|---|
| **Adobe Content Credentials** | Brands on Creative Cloud | Free basic tier; partner cert via https://contentauthenticity.org/community/cr-cli |
| **Truepic** | High-volume API-first signing | Tiered SaaS — contact for quote |
| **Numbers Protocol** | Brands wanting on-chain anchoring | Free tier exists |
| **Microsoft Azure Confidential Ledger** | Azure shops with KMS policy | Azure consumption pricing |

## Using a production cert with ContentForge

```bash
python3 scripts/generate-docx.py \
    --content output/humanized.md \
    --output output/article.docx \
    --reports output/reports.json \
    --brand "Acme Corp" --content-type article \
    --c2pa-sign \
    --c2pa-signing-cert /secure/c2pa-prod-cert.pem \
    --c2pa-signing-key /secure/c2pa-prod-key.pem
```

The script writes both the .docx and a `.c2pa.json` sidecar (c2pa-python 0.32 doesn't yet support .docx MIME for inline embedding — when that lands the script will auto-embed inline AND keep producing the sidecar).

## Important — ContentForge editorial-responsibility claim

EU AI Act Article 50 lets you skip explicit AI-generated-text disclosure on matters of public interest IF a human reviewer assumes editorial responsibility. The ContentForge manifest records this explicitly:

```json
{
  "action": "c2pa.edited",
  "when": "<timestamp>",
  "parameters": {
    "description": "Human-reviewed via Phase 7 reviewer scorecard before delivery"
  }
}
```

Your brand still needs an actual internal sign-off process backing this claim — the Phase 7 reviewer scorecard is the AI-side record, but a human editorial owner needs to actually review and sign off before the .docx ships.

## Key handling rules

1. Never commit cert + key to git
2. Use a secret store for team environments
3. Rotate annually
4. Revoke immediately if compromised

## Timeline

EU AI Act Article 50 enforcement: **2 August 2026** (~76 days from 17 May 2026).

## Full reference

See `digital-marketing-pro/docs/c2pa-production-cert-guide.md` for the detailed walkthrough.
