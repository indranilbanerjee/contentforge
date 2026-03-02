#!/usr/bin/env python3
"""
connector-status.py
===================
Connector discovery and status reporting for ContentForge.

Reports which MCP connectors are configured (HTTP and npx), which are
available but not yet connected, and which ContentForge workflows gain
capabilities from each connector category.

Usage:
    python connector-status.py --action status          # Full status dashboard
    python connector-status.py --action list-available   # All available connectors
    python connector-status.py --action check <name>     # Check specific connector
    python connector-status.py --action setup-guide <name>  # Setup instructions for a connector
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Plugin root = parent of scripts/
PLUGIN_ROOT = Path(__file__).resolve().parent.parent
MCP_JSON = PLUGIN_ROOT / ".mcp.json"
MCP_EXAMPLE = PLUGIN_ROOT / ".mcp.json.example"

# ── Connector Registry ──────────────────────────────────────────────
# Every connector ContentForge knows about, grouped by category.
# "http" = available as HTTP connector (works in Cowork + Claude Code)
# "npx"  = requires local npx server (Claude Code only)

CONNECTOR_REGISTRY = {
    "knowledge-base": {
        "description": "Knowledge management and documentation — store requirements, brand docs, reference material",
        "connectors": {
            "notion": {
                "transport": "http",
                "url": "https://mcp.notion.com/mcp",
                "description": "Notion — store content requirements, brand docs, editorial calendars",
                "env_vars": [],
                "skills_unlocked": [
                    "contentforge", "batch-process", "content-refresh",
                    "cf-brief", "cf-audit", "cf-style-guide",
                ],
            },
            "confluence": {
                "transport": "npx",
                "package": "mcp-confluence",
                "description": "Confluence — team wikis, brand guidelines, knowledge bases",
                "env_vars": ["CONFLUENCE_URL", "CONFLUENCE_TOKEN"],
                "skills_unlocked": [
                    "contentforge", "cf-style-guide",
                ],
            },
        },
    },
    "design": {
        "description": "Visual design and creative assets — featured images, infographics, social graphics",
        "connectors": {
            "canva": {
                "transport": "http",
                "url": "https://mcp.canva.com/mcp",
                "description": "Canva — featured images, social graphics, infographics, brand kit",
                "env_vars": [],
                "skills_unlocked": [
                    "contentforge", "batch-process", "cf-social-adapt",
                ],
            },
            "figma": {
                "transport": "http",
                "url": "https://mcp.figma.com/mcp",
                "description": "Figma — design assets, illustrations, visual elements",
                "env_vars": [],
                "skills_unlocked": [
                    "contentforge", "cf-social-adapt",
                ],
            },
        },
    },
    "cms": {
        "description": "Content management and publishing — push finished content to live sites",
        "connectors": {
            "webflow": {
                "transport": "http",
                "url": "https://mcp.webflow.com/sse",
                "description": "Webflow — publish articles, blog posts, landing pages to CMS",
                "env_vars": [],
                "skills_unlocked": [
                    "cf-publish", "contentforge", "batch-process",
                ],
            },
            "wordpress": {
                "transport": "npx",
                "package": "mcp-wordpress",
                "description": "WordPress — publish posts, pages, manage categories and metadata",
                "env_vars": ["WORDPRESS_SITE_URL", "WORDPRESS_AUTH_TOKEN"],
                "skills_unlocked": [
                    "cf-publish", "contentforge", "batch-process",
                ],
            },
            "hubspot-cms": {
                "transport": "npx",
                "package": "mcp-hubspot-cms",
                "description": "HubSpot CMS — blog posts, landing pages, email content",
                "env_vars": ["HUBSPOT_ACCESS_TOKEN"],
                "skills_unlocked": [
                    "cf-publish",
                ],
            },
        },
    },
    "chat": {
        "description": "Team messaging and notifications — production status updates, batch alerts",
        "connectors": {
            "slack": {
                "transport": "http",
                "url": "https://mcp.slack.com/mcp",
                "description": "Slack — batch status notifications, content approval alerts, team updates",
                "env_vars": [],
                "skills_unlocked": [
                    "batch-process", "cf-publish", "cf-calendar",
                ],
            },
        },
    },
    "email": {
        "description": "Email communication — draft sharing, delivery notifications",
        "connectors": {
            "gmail": {
                "transport": "http",
                "url": "https://gmail.mcp.claude.com/mcp",
                "description": "Gmail — share drafts, deliver finished content, review notifications",
                "env_vars": [],
                "skills_unlocked": [
                    "batch-process", "cf-publish",
                ],
            },
        },
    },
    "calendar": {
        "description": "Calendar and scheduling — content calendar, publishing schedule, deadlines",
        "connectors": {
            "google-calendar": {
                "transport": "http",
                "url": "https://gcal.mcp.claude.com/mcp",
                "description": "Google Calendar — content calendar events, publishing deadlines, review reminders",
                "env_vars": [],
                "skills_unlocked": [
                    "cf-calendar", "batch-process",
                ],
            },
        },
    },
    "spreadsheets": {
        "description": "Data intake and requirement management — batch content briefs, tracking sheets",
        "connectors": {
            "google-sheets": {
                "transport": "script",
                "script": "scripts/sheets-tracker.py",
                "description": "Google Sheets — batch requirement intake, content tracking, quality score history (via Python script + service account)",
                "env_vars": [],
                "credentials": "~/.claude-marketing/google-credentials.json",
                "skills_unlocked": [
                    "batch-process", "cf-analytics", "cf-audit",
                ],
                "note": "Uses scripts/sheets-tracker.py with Google service account. Works in Cowork + Claude Code. Also available as npx MCP server (@anthropic/mcp-google-sheets) for Claude Code only.",
            },
        },
    },
    "file-storage": {
        "description": "File storage and brand knowledge — brand assets, reference docs, style guides",
        "connectors": {
            "google-drive": {
                "transport": "script",
                "script": "scripts/drive-uploader.py",
                "description": "Google Drive — output delivery, folder organization, visual asset upload (via Python script + service account)",
                "env_vars": [],
                "credentials": "~/.claude-marketing/google-credentials.json",
                "skills_unlocked": [
                    "contentforge", "batch-process", "content-refresh",
                    "cf-style-guide", "cf-audit",
                ],
                "note": "Uses scripts/drive-uploader.py with Google service account. Works in Cowork + Claude Code. Also available as native Claude platform integration (Settings > Integrations) and as npx MCP server.",
            },
        },
    },
    "seo": {
        "description": "Search engine optimization — keyword data, backlink analysis, competitor research",
        "connectors": {
            "ahrefs": {
                "transport": "http",
                "url": "https://api.ahrefs.com/mcp/mcp",
                "description": "Ahrefs — keyword research, backlink data, content gap analysis",
                "env_vars": [],
                "skills_unlocked": [
                    "cf-brief", "cf-audit", "content-refresh",
                ],
            },
            "similarweb": {
                "transport": "http",
                "url": "https://mcp.similarweb.com",
                "description": "Similarweb — traffic analysis, competitor content benchmarks",
                "env_vars": [],
                "skills_unlocked": [
                    "cf-brief", "cf-audit",
                ],
            },
            "semrush": {
                "transport": "npx",
                "package": "mcp-semrush",
                "description": "SEMrush — keyword research, site audit, position tracking",
                "env_vars": ["SEMRUSH_API_KEY"],
                "skills_unlocked": [
                    "cf-brief", "cf-audit",
                ],
            },
        },
    },
    "translation": {
        "description": "Translation and localization — multilingual content production",
        "connectors": {
            "deepl": {
                "transport": "npx",
                "package": "deepl-mcp-server",
                "description": "DeepL — professional translation, 30+ languages, brand voice preservation",
                "env_vars": ["DEEPL_API_KEY"],
                "skills_unlocked": [
                    "cf-translate",
                ],
            },
            "sarvam-ai": {
                "transport": "npx",
                "package": "sarvam-mcp-server",
                "description": "Sarvam AI — 22 Indian languages specialist",
                "env_vars": ["SARVAM_API_KEY"],
                "skills_unlocked": [
                    "cf-translate",
                ],
            },
        },
    },
    "social-media": {
        "description": "Social media publishing — post adapted content directly to platforms",
        "connectors": {
            "twitter-x": {
                "transport": "npx",
                "package": "mcp-twitter",
                "description": "Twitter/X — post tweets, threads, media uploads",
                "env_vars": [
                    "TWITTER_API_KEY", "TWITTER_API_SECRET",
                    "TWITTER_ACCESS_TOKEN", "TWITTER_ACCESS_SECRET",
                ],
                "skills_unlocked": ["cf-social-adapt"],
            },
            "linkedin-publishing": {
                "transport": "npx",
                "package": "mcp-linkedin-publishing",
                "description": "LinkedIn — post articles, share updates, company pages",
                "env_vars": ["LINKEDIN_ACCESS_TOKEN"],
                "skills_unlocked": ["cf-social-adapt"],
            },
            "instagram": {
                "transport": "npx",
                "package": "mcp-instagram",
                "description": "Instagram — publish images/carousels, insights",
                "env_vars": [
                    "INSTAGRAM_ACCESS_TOKEN",
                    "INSTAGRAM_BUSINESS_ACCOUNT_ID",
                ],
                "skills_unlocked": ["cf-social-adapt"],
            },
        },
    },
    "analytics": {
        "description": "Website analytics — content performance tracking, traffic analysis",
        "connectors": {
            "google-analytics": {
                "transport": "npx",
                "package": "@anthropic/mcp-google-analytics",
                "description": "Google Analytics 4 — content traffic, engagement, conversions",
                "env_vars": [
                    "GA_PROPERTY_ID", "GOOGLE_APPLICATION_CREDENTIALS",
                ],
                "skills_unlocked": [
                    "cf-analytics", "cf-audit",
                ],
            },
            "google-search-console": {
                "transport": "npx",
                "package": "@anthropic/mcp-google-search-console",
                "description": "Google Search Console — rankings, impressions, CTR for content",
                "env_vars": [
                    "GSC_SITE_URL", "GOOGLE_APPLICATION_CREDENTIALS",
                ],
                "skills_unlocked": [
                    "cf-analytics", "cf-audit", "cf-brief",
                ],
            },
        },
    },
}


def _load_mcp_json():
    """Load the active .mcp.json and return configured server names."""
    if not MCP_JSON.exists():
        return {}
    try:
        data = json.loads(MCP_JSON.read_text(encoding="utf-8"))
        return data.get("mcpServers", {})
    except (json.JSONDecodeError, KeyError):
        return {}


def _is_configured(name, connector_info, active_servers):
    """Check if a connector is currently configured."""
    # HTTP connectors in .mcp.json
    if name in active_servers:
        return True
    # Script-based connectors — check if credentials file exists
    if connector_info["transport"] == "script":
        creds_path = connector_info.get("credentials", "")
        if creds_path:
            return Path(creds_path).expanduser().exists()
        return True  # No credentials needed
    # Check env vars for npx connectors
    if connector_info["transport"] == "npx" and connector_info.get("env_vars"):
        return all(os.environ.get(v) for v in connector_info["env_vars"])
    return False


def status_dashboard():
    """Full status dashboard of all connectors."""
    active_servers = _load_mcp_json()

    categories = []
    total_connected = 0
    total_available = 0

    for cat_key, cat_info in CONNECTOR_REGISTRY.items():
        connected = []
        available = []

        for name, conn in cat_info["connectors"].items():
            total_available += 1
            entry = {
                "name": name,
                "description": conn["description"],
                "transport": conn["transport"],
                "skills_unlocked": conn["skills_unlocked"],
            }

            if _is_configured(name, conn, active_servers):
                entry["status"] = "connected"
                connected.append(entry)
                total_connected += 1
            else:
                entry["status"] = "available"
                if conn["transport"] == "npx":
                    entry["env_vars_needed"] = conn["env_vars"]
                    entry["note"] = "Claude Code only (requires npx)"
                elif conn["transport"] == "script":
                    entry["credentials_needed"] = conn.get("credentials", "")
                    entry["note"] = "Python script — works in Cowork + Claude Code (needs service account)"
                else:
                    entry["note"] = "HTTP connector — works in Cowork + Claude Code"
                if "note" in conn:
                    entry["platform_note"] = conn["note"]
                available.append(entry)

        categories.append({
            "category": cat_key,
            "description": cat_info["description"],
            "connected": connected,
            "available": available,
            "connected_count": len(connected),
            "total_count": len(connected) + len(available),
        })

    return {
        "summary": {
            "total_connected": total_connected,
            "total_available": total_available,
            "coverage_percent": round(
                (total_connected / total_available * 100) if total_available else 0
            ),
        },
        "categories": categories,
    }


def list_available():
    """List all available connectors not yet configured."""
    active_servers = _load_mcp_json()
    available = []

    for cat_key, cat_info in CONNECTOR_REGISTRY.items():
        for name, conn in cat_info["connectors"].items():
            if not _is_configured(name, conn, active_servers):
                entry = {
                    "name": name,
                    "category": cat_key,
                    "description": conn["description"],
                    "transport": conn["transport"],
                    "skills_unlocked": conn["skills_unlocked"],
                }
                if conn["transport"] == "npx":
                    entry["env_vars_needed"] = conn["env_vars"]
                available.append(entry)

    return {"available_connectors": available, "count": len(available)}


def check_connector(name):
    """Check status of a specific connector."""
    active_servers = _load_mcp_json()

    for cat_key, cat_info in CONNECTOR_REGISTRY.items():
        if name in cat_info["connectors"]:
            conn = cat_info["connectors"][name]
            configured = _is_configured(name, conn, active_servers)

            result = {
                "name": name,
                "category": cat_key,
                "description": conn["description"],
                "transport": conn["transport"],
                "status": "connected" if configured else "not_connected",
                "skills_unlocked": conn["skills_unlocked"],
            }

            if conn["transport"] == "http":
                result["url"] = conn.get("url", "")
                result["setup"] = "HTTP connector — auto-connects via OAuth when you first use it"
            else:
                result["package"] = conn.get("package", "")
                result["env_vars"] = conn.get("env_vars", [])
                if not configured:
                    env_status = {}
                    for v in conn.get("env_vars", []):
                        env_status[v] = "set" if os.environ.get(v) else "missing"
                    result["env_var_status"] = env_status
                    result["setup"] = (
                        f"Requires npx server. Set environment variables: "
                        f"{', '.join(conn['env_vars'])}. "
                        f"Then add to .mcp.json or use /cf:connect."
                    )

            return result

    return {"error": f"Unknown connector: {name}", "hint": "Run --action list-available to see all connectors"}


def setup_guide(name):
    """Detailed setup guide for a specific connector."""
    active_servers = _load_mcp_json()

    for cat_key, cat_info in CONNECTOR_REGISTRY.items():
        if name in cat_info["connectors"]:
            conn = cat_info["connectors"][name]
            configured = _is_configured(name, conn, active_servers)

            guide = {
                "name": name,
                "category": cat_key,
                "description": conn["description"],
                "already_configured": configured,
                "skills_unlocked": conn["skills_unlocked"],
            }

            if conn["transport"] == "http":
                guide["transport"] = "http"
                guide["url"] = conn.get("url", "")
                guide["steps"] = [
                    f"This connector is already in .mcp.json as an HTTP connector.",
                    f"When you first use a skill that needs {name}, Claude will prompt you to authorize via OAuth.",
                    f"No API keys or environment variables needed — authentication is handled by the platform.",
                    f"Works in both Claude Code and Cowork.",
                ]
                if configured:
                    guide["status_message"] = (
                        f"{name} is configured. Use any of these skills to activate it: "
                        + ", ".join(f"/cf:{s}" if not s.startswith("cf-") else f"/{s}" for s in conn["skills_unlocked"])
                    )
            elif conn["transport"] == "script":
                guide["transport"] = "script"
                guide["script"] = conn.get("script", "")
                guide["credentials"] = conn.get("credentials", "")
                creds_path = Path(conn.get("credentials", "")).expanduser()
                guide["steps"] = [
                    f"1. Go to Google Cloud Console > IAM & Admin > Service Accounts",
                    f"2. Create a service account (e.g., 'contentforge-pipeline')",
                    f"3. Create a JSON key and download it",
                    f"4. Save the key to: {conn.get('credentials', '~/.claude-marketing/google-credentials.json')}",
                    f"5. Share your Google Sheet/Drive folder with the service account email (Editor access)",
                    f"6. Set tracking_sheet_id and drive_output_folder_id in your brand profile",
                ]
                if configured:
                    guide["status_message"] = (
                        f"{name} is configured (credentials found at {creds_path}). "
                        f"Script: {conn.get('script', '')}. "
                        f"Ensure tracking_sheet_id and drive_output_folder_id are set in your brand profile."
                    )
                guide["notes"] = [
                    "Uses Python scripts with Google API (no npx/Node.js required).",
                    "Works in both Claude Code and Cowork.",
                    "Credentials are stored locally, never in the plugin repository.",
                    "Dependencies (gspread, google-api-python-client) auto-install on first run.",
                ]
            else:
                guide["transport"] = "npx"
                guide["package"] = conn.get("package", "")
                guide["env_vars"] = conn.get("env_vars", [])
                guide["steps"] = [
                    f"1. Obtain API credentials from the {name} platform.",
                    f"2. Set these environment variables: {', '.join(conn['env_vars'])}",
                    f"3. Add the connector to .mcp.json using /cf:connect {name}",
                    f"   Or manually add this to .mcp.json:",
                ]
                guide["mcp_json_entry"] = {
                    name: {
                        "command": "npx",
                        "args": ["-y", conn["package"]],
                        "env": {v: f"${{{v}}}" for v in conn["env_vars"]},
                    }
                }
                guide["notes"] = [
                    "npx connectors require Node.js installed locally.",
                    "Works in Claude Code only (not Cowork).",
                    "API keys are read from environment variables — never stored in plugin files.",
                ]

            return guide

    return {"error": f"Unknown connector: {name}", "hint": "Run --action list-available to see all connectors"}


def main():
    parser = argparse.ArgumentParser(description="ContentForge connector status and discovery")
    parser.add_argument("--action", required=True,
                        choices=["status", "list-available", "check", "setup-guide"])
    parser.add_argument("--name", help="Connector name (for check/setup-guide)")
    parser.add_argument("name_positional", nargs="?", help="Connector name (positional)")
    args = parser.parse_args()

    name = args.name or args.name_positional

    if args.action == "status":
        result = status_dashboard()
    elif args.action == "list-available":
        result = list_available()
    elif args.action == "check":
        if not name:
            result = {"error": "Provide connector name: --name <name>"}
        else:
            result = check_connector(name)
    elif args.action == "setup-guide":
        if not name:
            result = {"error": "Provide connector name: --name <name>"}
        else:
            result = setup_guide(name)
    else:
        result = {"error": f"Unknown action: {args.action}"}

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
