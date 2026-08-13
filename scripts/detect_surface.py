#!/usr/bin/env python3
"""
detect_surface.py — which AI harness is this pipeline running on?

Consumed by the Phase 8 output manager to decide whether the brand's
AI-assistance disclosure applies when `ai_disclosure.mode` is
"claude-surfaces" (the default). The classification is deliberately
conservative and the payload carries its evidence:

    {"surface": "claude" | "non-claude" | "uncertain", "basis": [...]}

Fail-safe direction: "uncertain" means the disclosure APPLIES in
claude-surfaces mode. Over-disclosure is harmless; under-disclosure is the
compliance risk — so skipping the disclosure requires an AFFIRMATIVE
non-Claude fingerprint, never the absence of a Claude one.

Stdlib only. Pure classifier + thin I/O wrapper, mirroring
plugin-metadata.classify_environment (which it reuses for Cowork evidence).
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# Env vars that affirmatively identify a Claude harness (Claude Code sets
# CLAUDECODE=1; Cowork sets its session id; the SDK sets its version).
_CLAUDE_ENV = (
    "CLAUDECODE",
    "CLAUDE_CODE_SESSION_ID",
    "CLAUDE_CODE_ENTRYPOINT",
    "CLAUDE_AGENT_SDK_VERSION",
    "ANTHROPIC_COWORK_SESSION_ID",
)

# Best-effort affirmative fingerprints of NON-Claude harnesses. These gate the
# disclosure OFF in claude-surfaces mode, so each must be an identifier the
# harness itself sets — never something a Claude environment could also carry.
_NON_CLAUDE_ENV = (
    "CODEX_SESSION_ID",
    "CODEX_SANDBOX",
    "OPENAI_CODEX_HOME",
    "COPILOT_AGENT_SESSION",
    "COPILOT_CLI_SESSION",
    "CURSOR_SESSION_ID",
    "CURSOR_TRACE_ID",
    "ANTIGRAVITY_SESSION_ID",
    "GEMINI_CLI_SESSION",
)


def classify_surface(env: dict) -> dict:
    """Pure classifier — every input is a plain value, unit-testable."""
    claude_hits = [k for k in _CLAUDE_ENV if env.get(k)]
    non_claude_hits = [k for k in _NON_CLAUDE_ENV if env.get(k)]

    # Cowork sandbox evidence counts as a Claude signal too.
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "plugin_metadata", Path(__file__).resolve().parent / "plugin-metadata.py")
        pm = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(pm)
        env_info = pm.classify_environment(
            env, [p for p in pm._PROBE_PATHS if Path(p).exists()],
            __import__("platform").system(), os.getcwd(),
            str(Path.home()), os.environ.get("USERNAME") or os.environ.get("USER", ""))
        if env_info.get("environment") == "cowork-sandbox":
            claude_hits.append("cowork-sandbox-classification")
    except Exception:
        pass  # detection stays honest on whatever evidence remains

    if claude_hits and not non_claude_hits:
        return {"surface": "claude", "basis": claude_hits}
    if non_claude_hits and not claude_hits:
        return {"surface": "non-claude", "basis": non_claude_hits}
    if claude_hits and non_claude_hits:
        # Conflicting evidence — treat as uncertain (disclosure applies).
        return {"surface": "uncertain", "basis": claude_hits + non_claude_hits}
    return {"surface": "uncertain", "basis": []}


def disclosure_applies(mode: str, surface: str) -> bool:
    """The one decision table, shared by tests and the output manager.

    - "always"          -> apply
    - "off"             -> never
    - "claude-surfaces" -> apply unless a non-Claude surface is AFFIRMATIVELY
                           detected; "uncertain" applies (fail-safe).
    """
    mode = (mode or "claude-surfaces").strip().lower()
    if mode == "always":
        return True
    if mode == "off":
        return False
    return surface != "non-claude"


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Classify the AI harness surface for the disclosure gate")
    parser.add_argument("--mode", default="claude-surfaces",
                        choices=["claude-surfaces", "always", "off"],
                        help="Brand ai_disclosure.mode — the output includes the resulting decision")
    args = parser.parse_args()

    result = classify_surface(dict(os.environ))
    result["mode"] = args.mode
    result["disclosure_applies"] = disclosure_applies(args.mode, result["surface"])
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
