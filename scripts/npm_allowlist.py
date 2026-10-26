#!/usr/bin/env python3
"""
npm_allowlist.py
================
The only npm packages ContentForge will ever tell anyone to run with `npx`.

`npx -y <name>` downloads whatever is published under that name and runs it with the
user's environment, including the API keys the connector setup tells them to export.
A name nobody has registered yet can be registered by anyone, and a name registered
by a stranger runs the stranger's code. So ContentForge ships a runnable command only
for a package its VENDOR publishes, and that list lives in config/verified-npx-packages.json:
package name, the npm maintainer account(s) expected on it, and the vendor's repository.
Every other connector is "no verified connector": the setup guide prints the options
(the vendor's own MCP server, an HTTP aggregator, or skipping) and no command.

Checks, both stdlib-only:

  --check            OFFLINE. Every runnable package found in the shipped MCP config files and in the
                     connector registry must be in the allowlist. Exit 1 lists the ones that are not.
  --online           NETWORK (registry.npmjs.org, read-only). Every allowlisted package must still exist,
                     still have versions, still be published by the expected account, still point at the
                     vendor's repository, and its latest version must not be deprecated. Exit 1 lists the
                     failures; --report FILE writes them as JSON and as a Markdown issue body. The weekly
                     workflow (.github/workflows/npm-allowlist.yml) runs this and opens an issue.

Usage:
    python scripts/npm_allowlist.py --check
    python scripts/npm_allowlist.py --online --report npm-allowlist-report
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
ALLOWLIST_PATH = PLUGIN_ROOT / "config" / "verified-npx-packages.json"
# Shipped MCP config files that can carry a runnable command.
CONFIG_FILES = (".mcp.json", ".mcp.json.example", ".mcp.json.connectors-reference")
# Commands that fetch a package and execute it.
RUNNERS = {"npx", "bunx", "pnpx"}
NPM_REGISTRY = "https://registry.npmjs.org/"


def load(path=None) -> dict:
    """name -> allowlist entry."""
    data = json.loads(Path(path or ALLOWLIST_PATH).read_text(encoding="utf-8-sig"))
    return data.get("packages", {})


def package_name(spec: str) -> str:
    """`@scope/name@1.2.3` -> `@scope/name`; `name@latest` -> `name`."""
    spec = spec.strip()
    at = spec.rfind("@")
    return spec[:at] if at > 0 else spec


def is_verified(name: str, allow=None) -> bool:
    return package_name(name) in (load() if allow is None else allow)


def runnable_packages(config) -> list:
    """(server name, package) for every entry of a parsed MCP config that executes an npm package."""
    found = []

    def walk(obj, trail=""):
        if isinstance(obj, dict):
            command, args = obj.get("command"), obj.get("args")
            if isinstance(command, str) and isinstance(args, list):
                words = [a for a in args if isinstance(a, str)]
                if command in RUNNERS or (command in ("pnpm", "yarn") and words[:1] == ["dlx"]):
                    names = [w for w in words if not w.startswith("-") and w != "dlx"]
                    if names:
                        found.append((trail.strip("/") or "?", package_name(names[0])))
            for key, value in obj.items():
                walk(value, trail + "/" + str(key))
        elif isinstance(obj, list):
            for index, value in enumerate(obj):
                walk(value, trail + "/" + str(index))

    walk(config)
    return found


def mentioned_runnables(text: str) -> list:
    """Package names that text tells someone to run: `npx -y NAME` (or `--yes`), `bunx -y NAME`, or a `"-y", "NAME"` pair.

    Placeholders (<...>) are skipped, and so is prose that merely follows the flag ("`npx -y` downloads ..."): a package
    name contains a hyphen, a slash or an @."""
    names = []
    for pattern in (r"\b(?:npx|bunx|pnpx)\s+(?:-y|--yes)\s+(?:-{1,2}[A-Za-z-]+\s+)*(@?[A-Za-z0-9][A-Za-z0-9_./@-]*)",
                    r"[\"']-y[\"']\s*,\s*[\"']([^\"']+)[\"']"):
        for match in re.finditer(pattern, text):
            name = match.group(1)
            if "<" in name or ">" in name or not re.search(r"[-/@]", name):
                continue
            names.append(package_name(name))
    return names


def _load_registry():
    spec = importlib.util.spec_from_file_location("cf_connector_status", Path(__file__).resolve().parent / "connector-status.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.CONNECTOR_REGISTRY


def registry_runnables(registry) -> list:
    """(connector, package) for every registry entry that would be given a runnable command."""
    return [(name, conn.get("package", "")) for cat in registry.values() for name, conn in cat["connectors"].items()
            if conn.get("transport") == "npx"]


def offline_problems(allow=None, config_texts=None, registry=None) -> list:
    """Runnable packages that are not in the allowlist, as readable strings. Empty means clean."""
    allow = load() if allow is None else allow
    problems = []
    if config_texts is None:
        config_texts = {}
        for name in CONFIG_FILES:
            path = PLUGIN_ROOT / name
            if path.is_file():
                config_texts[name] = path.read_text(encoding="utf-8-sig")
    for where, text in config_texts.items():
        try:
            parsed = json.loads(text)
        except ValueError:
            problems.append(f"{where}: not valid JSON, so its commands could not be checked")
            continue
        for server, package in runnable_packages(parsed):
            if package not in allow:
                problems.append(f"{where}: server '{server}' runs npm package '{package}', which is not in the vendor-verified allowlist")
    for connector, package in registry_runnables(_load_registry() if registry is None else registry):
        if package not in allow:
            problems.append(f"connector registry: '{connector}' would be given a runnable command for '{package}', which is not in the allowlist")
    return problems


def _normalise_repo(url: str) -> str:
    url = (url or "").strip().lower()
    url = re.sub(r"^git\+", "", url)
    url = re.sub(r"^git://", "https://", url)
    url = re.sub(r"^ssh://git@", "https://", url)
    url = url.rstrip("/")
    url = re.sub(r"\.git$", "", url)
    return url.rstrip("/")


def check_package_online(name: str, entry: dict, doc) -> list:
    """Problems with one allowlisted package, given the registry document for it (None when npm says 404)."""
    if doc is None:
        return [f"{name}: not on npm (404). The name is free for anyone to register, and the next `npx -y {name}` would run their code"]
    problems = []
    versions = doc.get("versions") or {}
    latest = (doc.get("dist-tags") or {}).get("latest")
    if not versions or not latest or latest not in versions:
        return [f"{name}: no published versions (dist-tags.latest = {latest!r})"]
    maintainers = sorted({m.get("name", "") for m in doc.get("maintainers", []) if isinstance(m, dict)})
    expected = sorted(entry.get("npm_publishers", []))
    if not set(maintainers) & set(expected):
        problems.append(f"{name}: publisher changed. npm maintainers are {maintainers or 'none'}, expected one of {expected}")
    repo = versions[latest].get("repository") or doc.get("repository") or {}
    repo_url = repo.get("url") if isinstance(repo, dict) else repo
    if _normalise_repo(repo_url) != _normalise_repo(entry.get("repository", "")):
        problems.append(f"{name}: repository changed. npm says {repo_url!r}, expected {entry.get('repository')!r}")
    if versions[latest].get("deprecated"):
        problems.append(f"{name}: the latest version {latest} is marked deprecated: {versions[latest]['deprecated']}")
    return problems


def fetch_npm(name: str):
    """The registry document for `name`, or None for a 404. Other failures raise."""
    url = NPM_REGISTRY + name.replace("/", "%2F")
    request = urllib.request.Request(url, headers={"User-Agent": "contentforge-npm-allowlist/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        raise


def online_problems(allow=None, fetch=None) -> list:
    allow = load() if allow is None else allow
    fetch = fetch or fetch_npm
    problems = []
    for name, entry in allow.items():
        try:
            doc = fetch(name)
        except Exception as exc:  # noqa: BLE001 - a registry we cannot reach is a failure to report, not to hide
            problems.append(f"{name}: could not read npm ({exc})")
            continue
        problems += check_package_online(name, entry, doc)
    return problems


def issue_body(problems: list) -> str:
    lines = ["The weekly check of ContentForge's vendor-verified npm packages failed.", ""]
    lines += [f"- {p}" for p in problems]
    lines += ["", "Until this is resolved, treat the package named above as unverified: remove its entry from "
              "`config/verified-npx-packages.json` (connector setup then stops offering a command for it).",
              "", "Source: `scripts/npm_allowlist.py --online`."]
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Check ContentForge's vendor-verified npx package allowlist")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="offline: every runnable package must be allowlisted")
    mode.add_argument("--online", action="store_true", help="network: every allowlisted package must still be the vendor's")
    parser.add_argument("--report", default=None, help="with --online: write <REPORT>.json and <REPORT>.md (the issue body)")
    args = parser.parse_args(argv)
    problems = offline_problems() if args.check else online_problems()
    result = {"mode": "check" if args.check else "online", "ok": not problems, "problems": problems,
              "allowlisted": sorted(load())}
    print(json.dumps(result, indent=2))
    if args.report and problems:
        Path(args.report + ".json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        Path(args.report + ".md").write_text(issue_body(problems), encoding="utf-8")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
