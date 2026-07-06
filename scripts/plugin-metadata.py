#!/usr/bin/env python3
"""
plugin-metadata.py
==================
Single source of truth for "what's in this ContentForge install right now."
Returns LIVE counts and lists by reading the filesystem and plugin.json —
nothing hardcoded.

Why this exists: the cf-help skill (and several other places) used to bake
in stale version + count strings ("Version: 3.8.0 · Agents: 13 · Skills: 19
· Connectors: 9 HTTP + 19 npx") that drifted out of sync with reality
every time a connector was added or a release shipped. As of v3.12.8,
cf-help calls this script and presents whatever it returns.

Usage:
    python plugin-metadata.py                # all metadata, JSON
    python plugin-metadata.py --section version
    python plugin-metadata.py --section assets
    python plugin-metadata.py --section connectors
    python plugin-metadata.py --section skills-list
    python plugin-metadata.py --section commands-list
    python plugin-metadata.py --section all-with-environment
    python plugin-metadata.py --format text     # human-readable instead of JSON
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common  # noqa: E402

_common.ensure_utf8_stdout()

PLUGIN_ROOT = Path(__file__).resolve().parent.parent


# ─────────────────────────────────────────────────────────────────────────────
# Per-section probes — all read live state, none hardcoded
# ─────────────────────────────────────────────────────────────────────────────

def probe_version() -> dict:
    """Read version + name + description from plugin.json."""
    pj = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"
    if not pj.exists():
        return {"error": f"plugin.json missing at {pj}"}
    try:
        data = json.loads(pj.read_text(encoding="utf-8"))
        return {
            "name": data.get("name"),
            "version": data.get("version"),
            "license": data.get("license"),
            "homepage": data.get("homepage"),
        }
    except (json.JSONDecodeError, OSError) as e:
        return {"error": f"{type(e).__name__}: {e}"}


def probe_assets() -> dict:
    """Count agents / skills / commands / scripts on disk."""
    return {
        "agents": _count_files(PLUGIN_ROOT / "agents", "*.md"),
        "skills_total": _count_dirs(PLUGIN_ROOT / "skills"),
        "commands": _count_files(PLUGIN_ROOT / "commands", "*.md"),
        "scripts": _count_files(PLUGIN_ROOT / "scripts", "*.py"),
        "reference_docs": _count_files(PLUGIN_ROOT / "docs", "*.md"),
    }


def probe_connectors() -> dict:
    """Count HTTP + npx connectors from the reference catalog + example file."""
    http_ref = PLUGIN_ROOT / ".mcp.json.connectors-reference"
    npx_example = PLUGIN_ROOT / ".mcp.json.example"
    active = PLUGIN_ROOT / ".mcp.json"

    http_count = 0
    if http_ref.exists():
        try:
            data = json.loads(http_ref.read_text(encoding="utf-8"))
            servers = data.get("mcpServers_reference") or data.get("mcpServers") or {}
            http_count = sum(1 for cfg in servers.values()
                             if isinstance(cfg, dict) and cfg.get("type") == "http")
        except (json.JSONDecodeError, OSError):
            pass

    npx_count = 0
    if npx_example.exists():
        try:
            data = json.loads(npx_example.read_text(encoding="utf-8"))
            servers = data.get("mcpServers") or {}
            npx_count = sum(1 for cfg in servers.values()
                            if isinstance(cfg, dict) and cfg.get("command") == "npx")
        except (json.JSONDecodeError, OSError):
            pass

    active_count = 0
    active_names: list[str] = []
    if active.exists():
        try:
            data = json.loads(active.read_text(encoding="utf-8"))
            servers = data.get("mcpServers") or {}
            active_count = len(servers)
            active_names = sorted(servers.keys())
        except (json.JSONDecodeError, OSError):
            pass

    return {
        "available_http": http_count,
        "available_npx": npx_count,
        "available_total": http_count + npx_count,
        "active_count": active_count,
        "active_names": active_names,
        "cowork_compatible_count": http_count,  # only HTTP works in Cowork
    }


def probe_skills_list() -> list[dict]:
    """List every skill with its slash-command form + first-line description."""
    skills_dir = PLUGIN_ROOT / "skills"
    if not skills_dir.exists():
        return []
    out = []
    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        slash_name = skill_dir.name  # /contentforge:<slash_name>
        description = ""
        if skill_md.exists():
            description = _extract_description(skill_md)
        out.append({
            "skill_dir": skill_dir.name,
            "slash_command": f"/contentforge:{slash_name}",
            "description": description,
        })
    return out


def probe_commands_list() -> list[dict]:
    """List every command with its slash-command form + first-line description."""
    cmd_dir = PLUGIN_ROOT / "commands"
    if not cmd_dir.exists():
        return []
    out = []
    for cmd_md in sorted(cmd_dir.glob("*.md")):
        slash_name = cmd_md.stem
        description = _extract_description(cmd_md)
        out.append({
            "command_file": cmd_md.name,
            "slash_command": f"/contentforge:{slash_name}",
            "description": description,
        })
    return out


def probe_environment() -> dict:
    """Detect runtime environment hints — local Claude Code vs Cowork sandbox."""
    import os
    import platform
    cwd = Path.cwd()
    cwd_str = str(cwd).replace("\\", "/")
    home = str(Path.home()).replace("\\", "/")

    indicators = {
        "platform": platform.system(),
        "python": platform.python_version(),
        "cwd": cwd_str,
        "home": home,
        "writable_cwd": _is_writable(cwd),
    }

    # Cowork sandbox heuristics
    is_cowork = (
        "/sessions/" in cwd_str
        or cwd_str.startswith("/mnt")
        or "remote-plugins" in cwd_str
        or os.environ.get("ANTHROPIC_COWORK_SESSION_ID")
    )
    is_windows_host = platform.system() == "Windows" and home.startswith("C:")

    environment = (
        "cowork-sandbox" if is_cowork
        else "claude-code-windows" if is_windows_host
        else "claude-code-mac" if platform.system() == "Darwin"
        else "claude-code-linux" if platform.system() == "Linux"
        else "unknown"
    )

    # Cowork file-write limitations
    cowork_warning = None
    if is_cowork:
        cowork_warning = (
            "Cowork sandbox detected. ContentForge file writes "
            "(~/Documents/ContentForge/, ~/.claude-marketing/) target the "
            "Linux sandbox filesystem, NOT the user's Windows/macOS host. "
            "Files persist for the session only. To get host writes, run "
            "ContentForge in local Claude Code (CLI or IDE extension) "
            "instead of Cowork."
        )

    return {
        "environment": environment,
        "indicators": indicators,
        "cowork_warning": cowork_warning,
    }


def probe_pipeline_phases() -> list[dict]:
    """Reads agent file names to enumerate pipeline phases. (Agents are named
    `<order>-<role>.md` like `01-researcher.md`.)"""
    agents_dir = PLUGIN_ROOT / "agents"
    if not agents_dir.exists():
        return []
    out = []
    for agent_md in sorted(agents_dir.glob("*.md")):
        stem = agent_md.stem
        m = re.match(r"^(\d+(?:\.\d+)?)-(.+)$", stem)
        if m:
            phase, role = m.groups()
            description = _extract_description(agent_md)
            out.append({
                "phase": phase,
                "role": role.replace("-", " ").title(),
                "agent_file": agent_md.name,
                "description": description,
            })
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _count_files(directory: Path, pattern: str) -> int:
    if not directory.exists():
        return 0
    return len(list(directory.glob(pattern)))


def _count_dirs(directory: Path) -> int:
    if not directory.exists():
        return 0
    return sum(1 for p in directory.iterdir() if p.is_dir())


def _extract_description(md_path: Path) -> str:
    """Read the YAML frontmatter description (if any), else first prose line."""
    try:
        text = md_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    # Try YAML frontmatter
    m = re.match(r"^---\n(.*?)\n---", text, flags=re.DOTALL)
    if m:
        fm = m.group(1)
        dm = re.search(r'^description:\s*["\']?(.*?)["\']?\s*$', fm, flags=re.MULTILINE)
        if dm:
            return dm.group(1).strip().rstrip('"\'')
    # Fall back: first non-heading line
    for line in text.splitlines():
        line = line.strip()
        if line and not line.startswith("#") and not line.startswith("---"):
            return line[:200]
    return ""


def _is_writable(p: Path) -> bool:
    try:
        test = p / ".cf-write-probe"
        test.write_text("ok")
        test.unlink()
        return True
    except (OSError, PermissionError):
        return False


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def all_sections() -> dict:
    return {
        "version": probe_version(),
        "assets": probe_assets(),
        "connectors": probe_connectors(),
        "skills": probe_skills_list(),
        "commands": probe_commands_list(),
        "pipeline_phases": probe_pipeline_phases(),
    }


def format_text(data: dict) -> str:
    """Pretty text rendering for the help skill."""
    lines = []
    v = data.get("version", {})
    a = data.get("assets", {})
    c = data.get("connectors", {})
    env = data.get("environment", {})

    lines.append(f"=== CONTENTFORGE ===")
    lines.append(f"Version: {v.get('version', '?')}")
    lines.append(f"Agents: {a.get('agents', '?')}  |  Skills: {a.get('skills_total', '?')}  "
                 f"|  Commands: {a.get('commands', '?')}  |  Scripts: {a.get('scripts', '?')}")
    lines.append(f"Connectors: {c.get('available_http', '?')} HTTP + "
                 f"{c.get('available_npx', '?')} npx available  "
                 f"({c.get('active_count', 0)} currently active)")
    lines.append(f"Cowork-compatible connectors: {c.get('cowork_compatible_count', '?')} "
                 f"(HTTP only — npx connectors don't run in Cowork)")

    if env:
        e = env.get("environment", "unknown")
        lines.append(f"Environment: {e}")
        warn = env.get("cowork_warning")
        if warn:
            lines.append("")
            lines.append(f"WARNING: {warn}")

    cmds = data.get("commands", [])
    if cmds:
        lines.append("")
        lines.append(f"Slash commands ({len(cmds)}):")
        for c in cmds:
            lines.append(f"  {c['slash_command']:40s}  {c['description'][:60]}")

    skills = data.get("skills", [])
    if skills:
        lines.append("")
        lines.append(f"Skills ({len(skills)}):")
        for s in skills:
            lines.append(f"  {s['slash_command']:40s}  {s['description'][:60]}")
    return "\n".join(lines)


def render_text(section: str, result) -> str:
    """Human-readable rendering for EVERY section (the old code silently fell
    back to JSON for anything except all-with-environment)."""
    if section in ("all", "all-with-environment"):
        return format_text(result)
    if isinstance(result, list):
        lines = []
        for item in result:
            if isinstance(item, dict):
                label = (item.get("slash_command") or item.get("phase")
                         or item.get("name") or item.get("skill_dir") or "")
                desc = item.get("description", "")
                if section == "pipeline":
                    label = f"Phase {item.get('phase', '?'):>4}  {item.get('role', '')}"
                lines.append(f"  {str(label):40s}  {str(desc)[:70]}")
            else:
                lines.append(f"  {item}")
        return "\n".join(lines) if lines else "(empty)"
    if isinstance(result, dict):
        lines = []
        for k, v in result.items():
            if isinstance(v, (dict, list)):
                v = json.dumps(v, ensure_ascii=False)
            lines.append(f"{k}: {v}")
        return "\n".join(lines)
    return str(result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--section",
                        choices=["all", "all-with-environment", "version", "assets",
                                 "connectors", "skills-list", "commands-list",
                                 "pipeline", "environment"],
                        default="all")
    parser.add_argument("--format", choices=["json", "text"], default="json")
    args = parser.parse_args()

    if args.section in ("all", "all-with-environment"):
        result = all_sections()
        if args.section == "all-with-environment":
            result["environment"] = probe_environment()
    elif args.section == "version":
        result = probe_version()
    elif args.section == "assets":
        result = probe_assets()
    elif args.section == "connectors":
        result = probe_connectors()
    elif args.section == "skills-list":
        result = probe_skills_list()
    elif args.section == "commands-list":
        result = probe_commands_list()
    elif args.section == "pipeline":
        result = probe_pipeline_phases()
    elif args.section == "environment":
        result = probe_environment()
    else:
        result = {"error": f"unknown section: {args.section}"}

    if args.format == "text":
        print(render_text(args.section, result))
        return
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
