# Privacy

**No telemetry.** ContentForge sends nothing to its author or to any analytics service. There is no account, no sign-up and no tracking code in the plugin.

**Your AI host does the model calls.** ContentForge is a set of instructions and local scripts that run inside the agent you already use (Claude Code, Cowork, Codex, Cursor, Copilot CLI, Antigravity, Hermes Agent, OpenClaw or Grok). Prompts and outputs go to that host's model provider under that provider's own terms and privacy policy.

**Where your data lives.** Brand profiles, run artifacts and lifecycle records (audits, AEO checks, telemetry) are written on your machine under `~/.claude-marketing/` (or your host's plugin data folder). Finished `.docx` files go to `~/Documents/ContentForge/` (or the folder in `CONTENTFORGE_PUBLISH_DIR`). On Cowork with Google Drive connected, they go to the Drive folder you choose.

**Connections you choose.** The plugin ships with no connector switched on. When you connect a service yourself (for example a CMS, Google Drive, Airtable or an image provider), the data you ask it to send goes to that service under its own terms. API keys you configure stay on your machine or in your host's credential store.

**Web access.** Research, fact-checking and audit steps read public web pages you or the task point at, mostly through your host's own web tools. The brand-site harvester, the one script that crawls, identifies itself by name and obeys robots.txt.

## Network endpoints and credentials

Nothing connects on install: there are no hooks and no `.mcp.json` ships. Web research during a pipeline run uses your host's own web tools. A ContentForge script opens a network connection only when you, or a skill you invoked, run it, and only to the endpoints below.

| What | When | Endpoint | Credential |
|---|---|---|---|
| `scripts/harvest-brand-pages.py` | when you harvest a brand's website | the site you name, and its robots.txt (it sends `ContentForge-BrandHarvester/1.0` with this repo's URL and skips disallowed paths); only public http(s) addresses, every redirect hop re-checked, sitemaps only from the same site | none |
| `scripts/drive-uploader.py`, `scripts/sheets-tracker.py`, `scripts/airtable-tracker.py`, `scripts/backend-migrator.py` (and `scripts/setup.py` when it checks those credentials) | only when you choose Google Drive / Sheets or Airtable as the publish or tracking backend | the Google Drive and Google Sheets APIs, the Airtable API, and the https attachment URLs they return (downloaded into a temporary folder that the migrator removes afterwards) | the Google service-account JSON you save at `~/.claude-marketing/google-credentials.json`, or `AIRTABLE_TOKEN` |
| `scripts/refresh_models.py` | when you refresh the model registry | the model-list endpoints of api.anthropic.com, api.openai.com and generativelanguage.googleapis.com | the matching key; a provider without one is skipped |
| `scripts/generate-docx.py --c2pa-sign` | when you sign a `.docx` | `http://timestamp.digicert.com` (plain HTTP): an RFC 3161 timestamp request that carries a hash of the signature, not your file. With no certificate of your own, a throwaway self-signed key is created in a temporary folder for that one file and deleted afterwards | none |
| `scripts/_common.py` `pip_install` | **only** when you set `CONTENTFORGE_INSTALL_DEPS=1` for a run. Without it nothing is installed: the script prints the exact pinned command and exits non-zero. The packages are `python-docx` (every `.docx`), `c2pa-python` and `cryptography` (`--c2pa-sign`), and the Google and Airtable packages for the backend you chose | PyPI (exact versions from `PINNED_DEPENDENCIES`) | none |
| Opt-in MCP connectors | only after you copy an entry into `.mcp.json` yourself | the provider's endpoint in `.mcp.json.connectors-reference` | OAuth or an API key with that provider |

**Deleting your data.** Remove the folders listed above. Uninstalling the plugin through your host removes the plugin's own files.

**Questions.** Open an issue at https://github.com/indranilbanerjee/contentforge/issues or use a private security advisory for anything sensitive.

The code is MIT-licensed; see [LICENSE](LICENSE) for the terms of use.
