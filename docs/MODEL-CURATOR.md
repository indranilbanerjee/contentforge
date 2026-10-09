# Model Curator

`scripts/model_registry.json` is the curated catalog of AI model ids for the suite, and `scripts/resolve_model.py` is the resolver that reads it. Together they answer three questions:

1. "What's the current best model for X?" → `resolve("latest-fast-anthropic")` returns the concrete id.
2. "Is this model id still good?" → `check("gemini-2.0-flash")` returns `("retired", "gemini-3.5-flash")`.
3. "What's available?" → `list_models(vendor="google", modality="image-gen")` returns the matching catalog.

A single edit to `model_registry.json` propagates to everything that reads it — no grep-and-replace when a provider deprecates a model.

---

## What this is (and isn't) in ContentForge

**ContentForge does not call provider SDKs.** No script in `scripts/` imports the Anthropic or OpenAI SDK, and none takes a `--model`, `--anthropic-model`, `--openai-model`, or `--list-models` flag. Content is produced by the agent runtime — the orchestrator dispatches each pipeline phase to a subagent via the `Task` tool, and the runtime picks the model. There is nowhere in ContentForge to hand a model id to a provider API.

So the registry and resolver are **curation and reference tooling**, shared across the suite. Here they are used for:

- **Documentation truth** — one place to check whether a model id named in a doc, agent file, or example is still current.
- **Deprecation awareness** — `--check` tells you whether an id you're about to write down is `current`, `supported`, `preview`, `deprecated`, or `retired`, and what replaced it.
- **Staleness tracking** — `--registry-age` and `refresh_models.py` flag when the catalog needs a curation pass.
- **Parameter safety linting** — `--check-params` scans a Python file for `temperature` / `top_p` / `top_k` set alongside a Claude Opus 4.7+ target (see below).

The one script that talks to a provider is `scripts/refresh_models.py`, and it only reads the public `/v1/models` catalog endpoints to report drift. It never generates content.

---

## Why it exists

Hardcoding model strings like `claude-sonnet-4-5-20250929`, `gemini-2.0-flash`, or `veo-2.0-generate-001` across dozens of files means that when a provider retires a model, the string rots silently — a doc tells a user to run something that 404s, and the maintainer has to grep three repos to find every copy. The curator removes that failure mode by keeping every id in one file with a status and a replacement.

---

## Using the resolver

```bash
# Resolve an alias to a concrete id
python scripts/resolve_model.py --alias latest-text-anthropic
# -> the id the registry names for that alias today

# Check the status of a specific id (exit code 1 if deprecated/retired)
python scripts/resolve_model.py --check gemini-2.0-flash
# -> gemini-2.0-flash: retired (use gemini-3.5-flash)

# List the catalog, filtered
python scripts/resolve_model.py --list --vendor anthropic --status current

# How stale is the registry?
python scripts/resolve_model.py --registry-age

# Poll the provider catalogs and report drift (no writes)
python scripts/refresh_models.py
```

Behaviour when resolving:

- **Current id** → returned unchanged.
- **Deprecated / retired id** → the registered `replacement_id` is returned instead (pass `--allow-deprecated` to get the original back).
- **Unknown id** → reported as `unknown`; you lose the deprecation safety net.

Other flags: `--aliases` (list every alias and its resolution), `--registry-path` (where the loaded registry lives), `--json` (machine-readable output), and the `--vendor` / `--modality` / `--status` / `--tier` filters for `--list`.

---

## Aliases (the public API for "give me the latest X")

An alias names a capability kind, never a model id: `latest-<kind>-<vendor>`. Kinds in the registry today: `text`, `balanced`, `fast`, `vision`, `multimodal`, `image`, `image-balanced`, `image-edit`, `image-photoreal`, `image-character` and `video`, each under the vendors that offer one. Which id an alias resolves to changes every few weeks, so this page does not list the ids (a table of them was stale within a month). Run:

```bash
python scripts/resolve_model.py --aliases      # every alias and the id it resolves to now
python scripts/resolve_model.py --registry-age # days since the registry was reviewed
```

That command is the source of truth; nothing in the docs or skills should name the id.

---

## ⚠ Parameter compatibility — Claude Opus 4.7 and later

**Claude Opus 4.7 and later reject `temperature`, `top_p`, and `top_k` with HTTP 400** when set to a non-default value. The Anthropic SDK still accepts these parameters in its request types (for type-check compatibility), but the runtime returns a 400.

If a script calls Opus 4.7+ via the SDK, **omit** these parameters entirely — let the system default apply. Use prompting to guide model behavior instead.

`latest-text-anthropic` resolves to a model in that range, so any code path going through that alias is in scope. Scan a file before shipping it:

```bash
python scripts/resolve_model.py --check-params scripts/some_script.py
```

The scan is textual, not AST-based: it triggers when a file references `claude-opus-4-7` / `claude-opus-4-8` literally or uses the `latest-text-anthropic` alias, then flags every `temperature` / `top_p` / `top_k` assignment in that file. It exits 1 on any finding, so it drops straight into a pre-commit check. Expect occasional false positives when the model target is computed dynamically — that's deliberate, one extra review beats a 400 in production.

Source: [Claude model deprecations — API parameter deprecations](https://platform.claude.com/docs/en/about-claude/model-deprecations).

---

## Keeping the registry fresh

The frontier model landscape shifts roughly every 6 weeks. Treat any entry older than 3 months as suspect.

```bash
# Check how stale the registry is
python scripts/resolve_model.py --registry-age
# -> last_updated: <date> (<N> days ago). next_review_due: <date>

# Poll the provider catalogs and report drift (no writes)
ANTHROPIC_API_KEY=... OPENAI_API_KEY=... GEMINI_API_KEY=... python scripts/refresh_models.py

# After a manual curation pass, bump the timestamp
python scripts/refresh_models.py --bump-timestamp
```

The drift report shows:
- **NEW** — model ids the provider lists that are not in your registry (triage and add).
- **STALE** — model ids in your registry marked `current` that the provider no longer lists.

The script never auto-rewrites entries; curation is a human decision.

---

## Adding a new model

Edit `scripts/model_registry.json`. Minimum fields:

```json
{
  "id": "claude-opus-5",
  "vendor": "anthropic",
  "family": "claude",
  "display_name": "Claude Opus 5",
  "tier": "frontier",
  "modality": ["text", "vision"],
  "status": "current",
  "released": "2026-07",
  "best_for": ["complex reasoning", "agentic workflows"]
}
```

Then either point the relevant alias at the new id, or leave the alias alone and let callers opt in by naming the id directly.

## Deprecating a model

Change `status` to `"deprecated"` (or `"retired"` once the endpoint is gone) and add `replacement_id`. The resolver will auto-fall-forward for anything that resolves through an alias or validates an explicit id.

```json
{
  "id": "claude-opus-4-1-20250805",
  "vendor": "anthropic",
  "status": "deprecated",
  "replacement_id": "claude-opus-5"
}
```

Verify the result:

```bash
python scripts/resolve_model.py --check claude-opus-4-1-20250805
# -> claude-opus-4-1-20250805: deprecated (use the replacement_id you set)
```
