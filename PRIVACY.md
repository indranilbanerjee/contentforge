# Privacy

**No telemetry.** ContentForge sends nothing to its author or to any analytics service. There is no account, no sign-up and no tracking code in the plugin.

**Your AI host does the model calls.** ContentForge is a set of instructions and local scripts that run inside the agent you already use (Claude Code, Cowork, Codex, Cursor, Copilot CLI, Antigravity, Hermes Agent, OpenClaw or Grok). Prompts and outputs go to that host's model provider under that provider's own terms and privacy policy.

**Where your data lives.** Brand profiles, run artifacts and lifecycle records (audits, AEO checks, telemetry) are written on your machine under `~/.claude-marketing/` (or your host's plugin data folder). Finished `.docx` files go to `~/Documents/ContentForge/` (or the folder in `CONTENTFORGE_PUBLISH_DIR`). On Cowork with Google Drive connected, they go to the Drive folder you choose.

**Connections you choose.** The plugin ships with no connector switched on. When you connect a service yourself (for example a CMS, Google Drive, Airtable or an image provider), the data you ask it to send goes to that service under its own terms. API keys you configure stay on your machine or in your host's credential store.

**Web access.** Research, fact-checking and audit steps read public web pages you or the task point at, mostly through your host's own web tools. The brand-site harvester, the one script that crawls, identifies itself by name and obeys robots.txt.

## Network endpoints and credentials

Nothing connects on install: there are no hooks and `.mcp.json` ships empty. Web research during a pipeline run uses your host's own web tools. A ContentForge script opens a network connection only when you, or a skill you invoked, run it, and only to the endpoints below.

| What | When | Endpoint | Credential |
|---|---|---|---|
| `scripts/harvest-brand-pages.py` | when you harvest a brand's website | the site you name, and its robots.txt (it sends `ContentForge-BrandHarvester/1.0` with this repo's URL and skips disallowed paths) | none |
| `scripts/drive-uploader.py`, `scripts/sheets-tracker.py`, `scripts/airtable-tracker.py`, `scripts/backend-migrator.py` (and `scripts/setup.py` when it checks those credentials) | only when you choose Google Drive / Sheets or Airtable as the publish or tracking backend | the Google Drive and Google Sheets APIs, the Airtable API, and the attachment URLs they return | the Google service-account JSON you save at `~/.claude-marketing/google-credentials.json`, or `AIRTABLE_TOKEN` |
| `scripts/refresh_models.py` | when you refresh the model registry | the model-list endpoints of api.anthropic.com, api.openai.com and generativelanguage.googleapis.com | the matching key; a provider without one is skipped |
| `scripts/_common.py` `pip_install` | when a backend you chose needs a package and you run its setup | PyPI | none |
| Opt-in MCP connectors | only after you copy an entry into `.mcp.json` yourself | the provider's endpoint in `.mcp.json.connectors-reference` | OAuth or an API key with that provider |

**Deleting your data.** Remove the folders listed above. Uninstalling the plugin through your host removes the plugin's own files.

**Questions.** Open an issue at https://github.com/indranilbanerjee/contentforge/issues or use a private security advisory for anything sensitive.

The code is MIT-licensed; see [LICENSE](LICENSE) for the terms of use.
