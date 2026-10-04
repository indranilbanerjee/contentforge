"""docs/QUALITY-CONTRACT.md must say exactly what the config and the auditor say.

The quality contract is a public promise, and a promise with a stale number in it
is worse than no promise: a reader quotes the 7.0, the config says 7.5, and the
document has quietly become marketing copy. So the document is parsed here and
every number in it is resolved against the files that actually enforce it:

  * config/pipeline-graph.json       -> gate list, loop targets, loop budgets
  * config/scoring-thresholds.json   -> approve line, weights, minimums, gate thresholds
  * config/humanization-patterns.json-> the humanizer catalog size and its buckets
  * scripts/run-audit.py             -> the checks the auditor actually runs, and the
                                        two numbers it hard-codes (7.0 and +/-10%)

The document is written so a machine can read it: each table that carries numbers
either states the config key it came from (the test resolves it) or has fixed row
labels the test maps to config. Free prose is guarded too: the handful of
sentences that repeat a number (`43-pattern`, `default approve line is 7.0`,
`2 loops per edge`) are matched and compared.

Every guard is proven to fire: TestGuardFires plants a wrong number, a missing
gate, a missing auditor check, a renamed script and a drifted hard-coded constant
into an in-memory copy of the document or the auditor source and asserts that the
checker rejects each one. A guard that cannot fail is decoration.

Stdlib only.
"""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DOC_PATH = REPO / "docs" / "QUALITY-CONTRACT.md"
RUN_AUDIT_PATH = REPO / "scripts" / "run-audit.py"


def _json(rel: str):
    return json.loads((REPO / rel).read_text(encoding="utf-8"))


GRAPH = _json("config/pipeline-graph.json")
SCORING = _json("config/scoring-thresholds.json")
HUMAN = _json("config/humanization-patterns.json")

# Gate key in scoring-thresholds.json for each numbered phase.
PHASE_KEY = {
    "1": "phase_1_research", "2": "phase_2_fact_check", "3": "phase_3_draft",
    "3.5": "phase_3_5_visual_assets", "4": "phase_4_validation",
    "5": "phase_5_structure", "6": "phase_6_seo", "6.5": "phase_6_5_humanizer",
    "7": "phase_7_review", "8": "phase_8_output",
}

DIM_SHORT = {"content": "content_quality", "citation": "citation_integrity",
             "brand": "brand_compliance", "seo": "seo_performance",
             "readability": "readability"}

REQUIRED_HEADINGS = (
    r"^## The promise\s*$",
    r"^## The numbers at a glance\s*$",
    r"^## The \d+ gates, in order\s*$",
    r"^## The approve line and the five dimensions\s*$",
    r"^## Loop budgets\s*$",
    r"^## Key thresholds, exactly\s*$",
    r"^## What the run auditor re-checks",
    r"^## Advisory signals that never gate\s*$",
    r"^## What this contract does not promise\s*$",
    r"^## Verify it yourself\s*$",
)


# --------------------------------------------------------------------------
# markdown + config helpers
# --------------------------------------------------------------------------

def _cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def parse_tables(text: str) -> list[dict]:
    """Every pipe table in the document: {'header': [...], 'rows': [[...], ...]}."""
    lines = text.splitlines()
    tables, i = [], 0
    sep = re.compile(r"^\|[\s:|-]+\|\s*$")
    while i < len(lines) - 1:
        if lines[i].lstrip().startswith("|") and sep.match(lines[i + 1].strip()):
            header = _cells(lines[i])
            rows, j = [], i + 2
            while j < len(lines) and lines[j].lstrip().startswith("|"):
                rows.append(_cells(lines[j]))
                j += 1
            tables.append({"header": header, "rows": rows})
            i = j
        else:
            i += 1
    return tables


def find_table(tables: list[dict], *first_headers: str):
    want = [h.casefold() for h in first_headers]
    for t in tables:
        got = [h.casefold() for h in t["header"][:len(want)]]
        if got == want:
            return t
    return None


def code(cell: str) -> str:
    """Contents of the first backtick span, else the cell itself."""
    m = re.search(r"`([^`]+)`", cell)
    return (m.group(1) if m else cell).strip()


def to_float(s: str):
    s = s.strip().replace("−", "-")
    return float(s) if re.fullmatch(r"-?\d+(?:\.\d+)?", s) else None


def same_number(a, b) -> bool:
    return a is not None and b is not None and abs(float(a) - float(b)) < 1e-9


def resolve(path: str):
    """Dotted config key; a 'graph:' prefix reads pipeline-graph.json."""
    if path.startswith("graph:"):
        node, keys = GRAPH, path[len("graph:"):]
    else:
        node, keys = SCORING, path
    for k in keys.split("."):
        node = node[k]
    return node


def values_match(doc_cell: str, cfg) -> bool:
    doc_cell = doc_cell.strip()
    if isinstance(cfg, bool):
        return doc_cell.casefold() == str(cfg).casefold()
    if isinstance(cfg, list):
        want = "-".join(f"{x:g}" for x in cfg)
        got = doc_cell.replace("–", "-").replace(" ", "")
        return got == want
    return same_number(to_float(doc_cell), cfg)


def numbers_in(obj) -> set:
    out = set()
    if isinstance(obj, bool):
        return out
    if isinstance(obj, (int, float)):
        out.add(round(float(obj), 6))
    elif isinstance(obj, dict):
        for v in obj.values():
            out |= numbers_in(v)
    elif isinstance(obj, list):
        for v in obj:
            out |= numbers_in(v)
    return out


def gate_nodes() -> list[tuple[str, dict]]:
    return [(p, n) for p, n in GRAPH["nodes"].items()
            if str(n.get("gate", "")).startswith("Gate ")]


def pattern_counts() -> dict:
    cat = HUMAN["signs_of_ai_writing_catalog"]
    out = {}
    for name, bucket in cat.items():
        if name.startswith("_") or not isinstance(bucket, dict):
            continue
        out[name] = sum(1 for k in bucket if re.match(r"^\d{2}_", k))
    return out


def provenance(phase: str) -> set:
    """Every number the config (or the graph's own gate sentence) can justify for
    this gate: default values, every content-type / industry override of the same
    gate, and the numbers written in the graph's gate string."""
    key = PHASE_KEY[phase]
    nums = numbers_in(SCORING["default"]["quality_gates"].get(key, {}))
    for group in ("content_type_overrides", "industry_overrides"):
        for entry in SCORING.get(group, {}).values():
            if isinstance(entry, dict):
                nums |= numbers_in(entry.get("quality_gates", {}).get(key, {}))
    nums |= {round(float(x), 6)
             for x in re.findall(r"\d+(?:\.\d+)?", GRAPH["nodes"][phase]["gate"])}
    if phase == "7":
        d = SCORING["default"]
        nums |= {round(d["minimum_pass_score"], 6), round(d["human_review_threshold"], 6)}
        nums |= numbers_in(d["dimension_weights"])
    return nums


def prose_numbers(cell: str) -> list[float]:
    """Numbers a gate cell asserts: code spans, 'Phase N' and 'Gate N' references
    are file names and cross-references, not claims."""
    s = re.sub(r"`[^`]*`", " ", cell)
    s = re.sub(r"\b(?:Phase|Gate)\s+\d+(?:\.\d+)?", " ", s)
    return [float(x) for x in re.findall(r"\d+(?:\.\d+)?", s)]


# --------------------------------------------------------------------------
# the checks (each returns a list of problem strings; empty list = clean)
# --------------------------------------------------------------------------

def check_headings(text: str) -> list[str]:
    return [f"missing section matching {pat!r}" for pat in REQUIRED_HEADINGS
            if not re.search(pat, text, re.M)]


def check_glance(tables) -> list[str]:
    t = find_table(tables, "Contract term", "Value")
    if t is None:
        return ["'numbers at a glance' table (Contract term | Value) not found"]
    d = SCORING["default"]
    counts = pattern_counts()
    total = sum(counts.values())
    high = HUMAN["ai_signal_scoring"]["weights"]["high_signal_x2"]
    expected = {
        "Approve line (default)": d["minimum_pass_score"],
        "Human-review line": d["human_review_threshold"],
        "Numbered quality gates": len(gate_nodes()),
        "Loop budget per edge": GRAPH["loop_budgets"]["per_edge"],
        "Loop budget per run": GRAPH["loop_budgets"]["total_per_run"],
        "Humanizer catalog patterns": total,
        "Core patterns": total - counts["structure_and_framing_patterns"]
                         - counts["detector_signal_patterns"],
        "Structure and framing patterns": counts["structure_and_framing_patterns"],
        "Detector-signal patterns": counts["detector_signal_patterns"],
        "High-signal patterns (weight x2)": len(high),
        "Weighted checks in the signal score": 2 * len(high) + (total - len(high)),
        "Remaining-AI-signal ceiling":
            d["quality_gates"]["phase_6_5_humanizer"]["max_ai_signal_score"],
    }
    rows = {r[0]: r[1] for r in t["rows"] if len(r) >= 2}
    problems = []
    for label, want in expected.items():
        if label not in rows:
            problems.append(f"glance table lost the row {label!r}")
        elif not same_number(to_float(rows[label]), want):
            problems.append(f"glance: {label} is {rows[label]!r} but config says {want}")
    return problems


def check_gate_table(tables) -> list[str]:
    t = find_table(tables, "Gate", "Phase", "What it checks", "On failure", "Enforced by")
    if t is None:
        return ["gate table (Gate | Phase | What it checks | On failure | Enforced by) not found"]
    problems = []
    gates = gate_nodes()
    doc_ids = [r[0] for r in t["rows"]]
    want_ids = [p for p, _ in gates]
    if doc_ids != want_ids:
        problems.append(f"gate rows {doc_ids} do not match the graph's gates {want_ids}")
    by_id = {r[0]: r for r in t["rows"] if len(r) >= 5}
    for phase, node in gates:
        row = by_id.get(phase)
        if row is None:
            continue
        _, label, checks, failure, enforced = row[:5]
        if label.casefold() != node["label"].casefold():
            problems.append(f"gate {phase}: phase name {label!r} but the graph calls it "
                            f"{node['label']!r}")
        target = node["loop_target"]
        if target == "responsible-phase":
            ok = "responsible phase" in failure.casefold()
        else:
            ok = re.search(rf"Phase {re.escape(target)}(?!\.\d)", failure) is not None
        if not ok:
            problems.append(f"gate {phase}: 'On failure' says {failure!r} but the graph's "
                            f"loop target is {target!r}")
        if not any(w in enforced.casefold() for w in ("script", "orchestrator", "agent")):
            problems.append(f"gate {phase}: 'Enforced by' names no enforcement tag")
        allowed = provenance(phase)
        for n in prose_numbers(checks):
            if round(n, 6) not in allowed:
                problems.append(f"gate {phase}: the doc asserts {n:g} but no config value or "
                                f"graph gate sentence for that gate contains it")
    return problems


def check_thresholds(tables) -> list[str]:
    t = find_table(tables, "Gate", "Threshold", "Value", "Config key")
    if t is None:
        return ["thresholds table (Gate | Threshold | Value | Config key) not found"]
    problems, seen = [], set()
    for r in t["rows"]:
        if len(r) < 4:
            problems.append(f"malformed thresholds row: {r}")
            continue
        path = code(r[3])
        seen.add(path)
        try:
            cfg = resolve(path)
        except (KeyError, TypeError):
            problems.append(f"thresholds: config key {path!r} does not exist")
            continue
        if not values_match(r[2], cfg):
            problems.append(f"thresholds: gate {r[0]} '{r[1]}' says {r[2]!r} but "
                            f"{path} is {cfg!r}")
    required = [
        "default.minimum_pass_score", "default.human_review_threshold",
        "default.quality_gates.phase_2_fact_check.min_verified_percentage",
        "default.quality_gates.phase_3_draft.word_count_tolerance_percent",
        "default.quality_gates.phase_4_validation.min_accuracy_confidence",
        "default.quality_gates.phase_6_5_humanizer.max_ai_signal_score",
        "default.quality_gates.phase_8_output.appendices_present",
    ]
    for path in required:
        if path not in seen:
            problems.append(f"thresholds table no longer states {path}")
    return problems


def check_dimensions(tables) -> list[str]:
    t = find_table(tables, "Dimension", "Weight", "Minimum score")
    if t is None:
        return ["dimension table (Dimension | Weight | Minimum score) not found"]
    d = SCORING["default"]
    weights = d["dimension_weights"]
    minimums = d["quality_gates"]["phase_7_review"]
    problems, seen = [], []
    for r in t["rows"]:
        key = r[0].strip().casefold().replace(" ", "_")
        seen.append(key)
        if key not in weights:
            problems.append(f"dimension {r[0]!r} is not a config dimension")
            continue
        if not same_number(to_float(r[1]), weights[key]):
            problems.append(f"dimension {r[0]}: weight {r[1]!r} but config says {weights[key]}")
        if not same_number(to_float(r[2]), minimums[f"min_{key}"]):
            problems.append(f"dimension {r[0]}: minimum {r[2]!r} but config says "
                            f"{minimums['min_' + key]}")
        if len(r) < 4 or not r[3].strip():
            problems.append(f"dimension {r[0]}: no 'loops back to' phase")
    if sorted(seen) != sorted(weights):
        problems.append(f"dimension rows {sorted(seen)} differ from config {sorted(weights)}")
    total = sum(to_float(r[1]) or 0 for r in t["rows"])
    if abs(total - 1.0) > 1e-6:
        problems.append(f"dimension weights sum to {total}, not 1.0")
    return problems


def check_industries(tables) -> list[str]:
    t = find_table(tables, "Industry", "Approve line")
    if t is None:
        return ["industry table (Industry | Approve line | ...) not found"]
    d = SCORING["default"]
    order = list(d["dimension_weights"])  # config order == column order in the doc
    overrides = SCORING["industry_overrides"]
    problems, seen = [], set()
    for r in t["rows"]:
        if len(r) < 4:
            problems.append(f"malformed industry row: {r}")
            continue
        label = r[0]
        key = "default" if label.casefold().startswith("default") \
            else label.strip().casefold().replace(" ", "_")
        seen.add(key)
        if key == "default":
            approve, weights, mins = d["minimum_pass_score"], d["dimension_weights"], {}
        elif key in overrides:
            o = overrides[key]
            approve = o["minimum_pass_score"]
            weights = o.get("dimension_weights", d["dimension_weights"])
            mins = o.get("quality_gates", {}).get("phase_7_review", {})
        else:
            problems.append(f"industry {label!r} has no config override")
            continue
        if not same_number(to_float(r[1]), approve):
            problems.append(f"industry {label}: approve line {r[1]!r} but config says {approve}")
        doc_w = [to_float(x) for x in r[2].split("/")]
        want_w = [weights[k] for k in order]
        if len(doc_w) != len(want_w) or not all(same_number(a, b)
                                                for a, b in zip(doc_w, want_w)):
            problems.append(f"industry {label}: weights {r[2]!r} but config says {want_w}")
        doc_m = {f"min_{DIM_SHORT[k]}": float(v)
                 for k, v in re.findall(
                     r"(content|citation|brand|seo|readability)\s+(\d+(?:\.\d+)?)", r[3])}
        if {k: round(v, 6) for k, v in doc_m.items()} != \
                {k: round(float(v), 6) for k, v in mins.items()}:
            problems.append(f"industry {label}: raised minimums {r[3]!r} but config says {mins}")
    want_keys = {"default"} | set(overrides)
    if seen != want_keys:
        problems.append(f"industry rows {sorted(seen)} differ from config {sorted(want_keys)}")
    return problems


def check_loops(tables) -> list[str]:
    t = find_table(tables, "Loop edge", "Budget", "Config key")
    if t is None:
        return ["loop budget table (Loop edge | Budget | Config key) not found"]
    problems, seen = [], set()
    for r in t["rows"]:
        path = code(r[2])
        seen.add(path)
        try:
            cfg = resolve(path)
        except (KeyError, TypeError):
            problems.append(f"loops: config key {path!r} does not exist")
            continue
        if not values_match(r[1], cfg):
            problems.append(f"loops: {r[0]} says {r[1]!r} but {path} is {cfg!r}")
    required = {"graph:loop_budgets.per_edge", "graph:loop_budgets.total_per_run",
                "default.quality_gates.phase_4_validation.max_validation_loops",
                "default.quality_gates.phase_6_seo.max_seo_loops"}
    required |= {f"default.feedback_loop_limits.{k}"
                 for k in SCORING["default"]["feedback_loop_limits"]
                 if not k.startswith("_")}
    for path in sorted(required - seen):
        problems.append(f"loop table no longer states {path}")
    return problems


def check_prose(text: str) -> list[str]:
    """Sentences that repeat a number outside the tables."""
    d = SCORING["default"]
    gates = d["quality_gates"]
    total = sum(pattern_counts().values())
    problems = []

    def each(pattern, want, what, cast=float):
        for m in re.finditer(pattern, text):
            if not same_number(cast(m.group(1)), want):
                problems.append(f"prose says {m.group(0)!r} but {what} is {want}")

    each(r"(\d+)-pattern", total, "the catalog size", int)
    each(r"\b(\d+) (?:numbered )?(?:quality )?gates?\b", len(gate_nodes()),
         "the numbered gate count", int)
    each(r"(\d+) loops? per edge", GRAPH["loop_budgets"]["per_edge"], "the per-edge budget", int)
    each(r"(\d+) loops? per run", GRAPH["loop_budgets"]["total_per_run"],
         "the per-run budget", int)
    each(r"default approve line (?:is|of) (\d+\.\d+)", d["minimum_pass_score"],
         "the default approve line")
    each(r"\((\d+\.\d+) by default", d["minimum_pass_score"], "the default approve line")
    each(r"[Uu]p to (\d+) unverified", gates["phase_2_fact_check"]["max_unverified_tolerated"],
         "the unverified-claim tolerance", int)
    each(r"signal score \(at most (\d+\.\d+)\)", gates["phase_6_5_humanizer"]["max_ai_signal_score"],
         "the remaining-AI-signal ceiling")
    each(r"±(\d+)%", gates["phase_3_draft"]["word_count_tolerance_percent"],
         "the word-count tolerance", int)
    each(r"±(\d+\.\d+) grade", gates["phase_5_structure"]["readability_grade_tolerance"],
         "the grade tolerance")
    lo, hi = gates["phase_6_seo"]["density_advisory_pct"]
    for m in re.finditer(r"band of ([\d.]+)–([\d.]+) percent", text):
        if not (same_number(float(m.group(1)), lo) and same_number(float(m.group(2)), hi)):
            problems.append(f"prose says {m.group(0)!r} but the density band is {lo}-{hi}")
    return problems


def _normalize_check_name(name: str) -> str:
    """f-string names carry a '({lo}-{hi})' tail and N/A-style names carry a
    parenthetical reason; both are decoration, not identity."""
    return re.sub(r"\s*\(.*$", "", name).strip()


def script_check_names(src: str) -> set:
    """(section, name) for every a.check(...) in run-audit.py. N/A reports are
    excluded: they are the 'input missing' path, described in prose."""
    pat = re.compile(r'a\.check\(\s*"([A-G] [a-z]+)",\s*f?"([^"]+)"')
    return {(sec, _normalize_check_name(name)) for sec, name in pat.findall(src)}


def check_auditor_table(tables, src: str) -> list[str]:
    t = find_table(tables, "Section", "Check (as the script names it)", "Fails when")
    if t is None:
        return ["auditor table (Section | Check | Fails when) not found"]
    doc = {(r[0], _normalize_check_name(r[1])) for r in t["rows"] if len(r) >= 3}
    real = script_check_names(src)
    problems = []
    for sec, name in sorted(real - doc):
        problems.append(f"run-audit.py runs '{sec}: {name}' but the contract does not list it")
    for sec, name in sorted(doc - real):
        problems.append(f"the contract lists '{sec}: {name}' but run-audit.py has no such check")
    if not real:
        problems.append("could not read any a.check(...) names from run-audit.py (guard is blind)")
    return problems


def check_references(text: str) -> list[str]:
    """Scripts, commands and config files the document names must exist."""
    problems = []
    spans = re.findall(r"`([^`]+)`", text)
    for span in spans:
        for tok in re.findall(r"(?<![\w/.-])((?:[\w.-]+/)*[\w-]+\.py)\b", span):
            path = REPO / tok if "/" in tok else REPO / "scripts" / tok
            if not path.is_file():
                problems.append(f"names a script that does not exist: {tok}")
    for name in set(re.findall(r"/contentforge:([\w-]+)", text)):
        if not ((REPO / "skills" / name / "SKILL.md").is_file()
                or (REPO / "commands" / f"{name}.md").is_file()):
            problems.append(f"names /contentforge:{name}, which is neither a skill nor a command")
    for rel in set(re.findall(r"\bconfig/[\w.-]+\.json\b", text)):
        if not (REPO / rel).is_file():
            problems.append(f"names a config file that does not exist: {rel}")
    return problems


def check_run_audit_constants(src: str) -> list[str]:
    """The auditor resolves the approve line from config (it no longer carries one),
    and still hard-codes the +/-10% word-count band; config owns both numbers."""
    d = SCORING["default"]
    problems = []
    if re.search(r"score >= \d", src):
        problems.append("run-audit.py carries a literal approve line again ('score >= N'); "
                        "it must resolve the line from config/scoring-thresholds.json")
    if "resolve_policy" not in src or "scoring-thresholds.json" not in src:
        problems.append("run-audit.py no longer resolves its policy from scoring-thresholds.json")
    tol = d["quality_gates"]["phase_3_draft"]["word_count_tolerance_percent"] / 100.0
    lo = re.findall(r"target \* (\d+(?:\.\d+)?)\)", src)
    if len(lo) < 2:
        problems.append("run-audit.py no longer contains the word-count band (target * a, target * b)")
    else:
        if not same_number(float(lo[0]), 1 - tol):
            problems.append(f"run-audit.py word-count floor is target*{lo[0]} but config "
                            f"tolerance implies {1 - tol:g}")
        if not same_number(float(lo[1]), 1 + tol):
            problems.append(f"run-audit.py word-count ceiling is target*{lo[1]} but config "
                            f"tolerance implies {1 + tol:g}")
    return problems


def check_precedence_rule(text: str) -> list[str]:
    """The loop-cap precedence rule is stated once in config and once here."""
    problems = []
    note = SCORING["default"]["feedback_loop_limits"].get("_precedence", "")
    if "SMALLER cap governs" not in note:
        problems.append("config lost its _precedence note on feedback_loop_limits "
                        "(the 'SMALLER cap governs' rule)")
    m = re.search(r"^## Loop budgets\s*\n(.*?)(?=^## )", text, re.M | re.S)
    if not m or "smaller cap governs" not in m.group(1):
        problems.append("the contract's 'Loop budgets' section no longer states that "
                        "the smaller cap governs")
    return problems


def check_gate1_wording(researcher: str) -> list[str]:
    """Gate 1's definition of a citable source: the graph's and the config's, not a
    private reliability floor in the researcher's checklist."""
    cfg = SCORING["default"]["quality_gates"]["phase_1_research"]
    problems = []
    if re.search(r"Reliability(?: Score)? ?≥ ?7\b", researcher):
        problems.append("agents/01-researcher.md still defines citable with a Reliability >=7 floor "
                        "the graph and config do not have")
    graph_gate = GRAPH["nodes"]["1"]["gate"]
    gate_nums = {float(x) for x in re.findall(r"\d+(?:\.\d+)?", graph_gate)}
    if float(cfg["min_high_reliability"]) not in gate_nums or 8.0 not in gate_nums:
        problems.append("the graph's Gate 1 sentence no longer carries the 5 / 8 reliability rule")
    for needle in (f"At least {cfg['min_verified_sources']} citable sources",
                   f"At least {cfg['min_high_reliability']} of them with Reliability Score ≥8"):
        if needle not in researcher:
            problems.append(f"agents/01-researcher.md no longer says {needle!r}")
    return problems


def check_reviewer_records_what_the_auditor_reads(reviewer: str, audit_src: str) -> list[str]:
    """The auditor re-derives from fields the reviewer must record. A field the
    auditor reads but the reviewer's schema never mentions is a check that can only
    ever report N/A; and the reviewer must be told to apply industry MINIMUMS, not
    just the approve line and weights."""
    problems = []
    for field in ("industry", "minimum_pass_score_applied", "weights_applied", "dimensions"):
        if f'"{field}"' not in reviewer:
            problems.append(f"agents/07-reviewer.md's review JSON never records {field!r}")
        if f'get("{field}")' not in audit_src:
            problems.append(f"run-audit.py no longer reads review[{field!r}]")
    for needle in ("Threshold resolution", "content_type_overrides.{content_type}",
                   "industry_overrides.{industry}", "dimension minimums",
                   "quality_gates.phase_7_review"):
        if needle not in reviewer:
            problems.append(f"agents/07-reviewer.md no longer says {needle!r}")
    return problems


def check_composite_tolerance(text: str, src: str) -> list[str]:
    """The contract names the composite rounding tolerance; the auditor owns it."""
    m = re.search(r"COMPOSITE_TOLERANCE = (\d+\.\d+)", src)
    if not m:
        return ["run-audit.py no longer defines COMPOSITE_TOLERANCE"]
    want = float(m.group(1))
    problems = []
    found = re.findall(r"more than (\d+\.\d+) away", text) \
        + re.findall(r"rounding tolerance of (\d+\.\d+)", text)
    if not found:
        problems.append("the contract no longer states the composite rounding tolerance")
    for n in found:
        if not same_number(float(n), want):
            problems.append(f"the contract says the composite tolerance is {n} but run-audit.py "
                            f"uses {want}")
    return problems


def check_contract(text: str, run_audit_src: str) -> list[str]:
    tables = parse_tables(text)
    problems = []
    problems += check_headings(text)
    problems += check_glance(tables)
    problems += check_gate_table(tables)
    problems += check_thresholds(tables)
    problems += check_dimensions(tables)
    problems += check_industries(tables)
    problems += check_loops(tables)
    problems += check_precedence_rule(text)
    problems += check_prose(text)
    problems += check_auditor_table(tables, run_audit_src)
    problems += check_references(text)
    problems += check_run_audit_constants(run_audit_src)
    problems += check_composite_tolerance(text, run_audit_src)
    return problems


# --------------------------------------------------------------------------
# tests
# --------------------------------------------------------------------------

DOC = DOC_PATH.read_text(encoding="utf-8") if DOC_PATH.is_file() else ""
SRC = RUN_AUDIT_PATH.read_text(encoding="utf-8")
RESEARCHER = (REPO / "agents" / "01-researcher.md").read_text(encoding="utf-8")
REVIEWER = (REPO / "agents" / "07-reviewer.md").read_text(encoding="utf-8")


class TestQualityContractMatchesConfig(unittest.TestCase):
    def test_document_exists(self):
        self.assertTrue(DOC_PATH.is_file(), "docs/QUALITY-CONTRACT.md is missing")

    def test_every_number_in_the_contract_matches_the_config(self):
        problems = check_contract(DOC, SRC)
        self.assertEqual(problems, [],
                         "docs/QUALITY-CONTRACT.md disagrees with the config / auditor:\n  "
                         + "\n  ".join(problems))

    def test_the_guards_are_not_vacuous(self):
        """A parser that finds no rows would pass every comparison."""
        tables = parse_tables(DOC)
        self.assertEqual(len(gate_nodes()), 10, "the pipeline no longer has 10 numbered gates")
        gate_t = find_table(tables, "Gate", "Phase", "What it checks")
        self.assertEqual(len(gate_t["rows"]), len(gate_nodes()))
        self.assertGreaterEqual(len(find_table(tables, "Gate", "Threshold")["rows"]), 20)
        self.assertEqual(len(find_table(tables, "Dimension", "Weight")["rows"]), 5)
        self.assertEqual(len(find_table(tables, "Industry", "Approve line")["rows"]),
                         1 + len(SCORING["industry_overrides"]))
        self.assertGreaterEqual(len(script_check_names(SRC)), 20)

    def test_auditor_table_covers_every_check_in_both_directions(self):
        problems = check_auditor_table(parse_tables(DOC), SRC)
        self.assertEqual(problems, [], "\n  ".join(problems))

    def test_run_audit_hardcoded_constants_match_config(self):
        problems = check_run_audit_constants(SRC)
        self.assertEqual(problems, [], "\n  ".join(problems))


class TestGuardFires(unittest.TestCase):
    """Plant a wrong value; the checker must notice. Each plant is applied to an
    in-memory copy so the shipped document is never touched."""

    @classmethod
    def setUpClass(cls):
        cls.baseline = check_contract(DOC, SRC)
        assert cls.baseline == [], "plant tests need a clean baseline: " + str(cls.baseline)

    def plant(self, old: str, new: str, *, src: bool = False, msg: str = ""):
        text, source = DOC, SRC
        target = source if src else text
        self.assertIn(old, target, f"plant anchor {old!r} not found — the doc/script moved; "
                                   f"update this plant")
        mutated = target.replace(old, new, 1)
        problems = check_contract(text, mutated) if src else check_contract(mutated, source)
        self.assertTrue(problems, f"planted drift went unnoticed: {msg or old!r} -> {new!r}")
        return problems

    # -- the four numbers the brief names -------------------------------
    def test_wrong_approve_threshold_is_caught(self):
        self.plant("| Approve line (default) | 7.0 |", "| Approve line (default) | 6.5 |")

    def test_wrong_approve_threshold_in_prose_is_caught(self):
        self.plant("The default approve line is 7.0.", "The default approve line is 7.5.")

    def test_wrong_gate_count_is_caught(self):
        self.plant("| Numbered quality gates | 10 |", "| Numbered quality gates | 11 |")

    def test_missing_gate_row_is_caught(self):
        row = next(l for l in DOC.splitlines() if l.startswith("| 6.5 | Humanizer |"))
        self.plant(row + "\n", "")

    def test_wrong_loop_budget_per_edge_is_caught(self):
        self.plant("| Loop budget per edge | 2 |", "| Loop budget per edge | 3 |")

    def test_wrong_loop_budget_per_run_in_prose_is_caught(self):
        self.plant("5 loops per run", "6 loops per run")

    def test_wrong_named_loop_cap_is_caught(self):
        self.plant("| Phase 7 → any phase | 2 |", "| Phase 7 → any phase | 3 |")

    def test_wrong_pattern_count_is_caught(self):
        self.plant("| Humanizer catalog patterns | 43 |", "| Humanizer catalog patterns | 41 |")

    def test_wrong_pattern_count_in_prose_is_caught(self):
        self.plant("43-pattern", "41-pattern")

    # -- weights, minimums, industries ----------------------------------
    def test_wrong_dimension_minimum_is_caught(self):
        self.plant("| Citation integrity | 0.25 | 7.0 |", "| Citation integrity | 0.25 | 6.0 |")

    def test_wrong_dimension_weight_is_caught(self):
        self.plant("| Content quality | 0.30 |", "| Content quality | 0.35 |")

    def test_wrong_industry_approve_line_is_caught(self):
        self.plant("| Pharma | 8.0 |", "| Pharma | 7.0 |")

    def test_wrong_industry_raised_minimum_is_caught(self):
        self.plant("citation 8.5, brand 8.0", "citation 7.5, brand 8.0")

    # -- gate table + thresholds ----------------------------------------
    def test_wrong_threshold_value_is_caught(self):
        self.plant("| Claims verified (minimum %) | 80 |", "| Claims verified (minimum %) | 85 |")

    def test_unjustified_number_in_a_gate_cell_is_caught(self):
        self.plant("At least 80% of claims verified", "At least 85% of claims verified")

    def test_wrong_loop_target_is_caught(self):
        self.plant("Loop to Phase 3 with the exact claims", "Loop to Phase 5 with the exact claims")

    def test_renamed_gate_is_caught(self):
        self.plant("| 5 | Structure & Proofread |", "| 5 | Copy Edit |")

    def test_nonexistent_config_key_is_caught(self):
        self.plant("phase_2_fact_check.min_verified_percentage`",
                   "phase_2_fact_check.min_verified_pct`")

    # -- auditor ---------------------------------------------------------
    def test_unlisted_auditor_check_is_caught(self):
        row = next(l for l in DOC.splitlines() if "| G honesty | 'blocked' names" in l)
        self.plant(row + "\n", "")

    def test_invented_auditor_check_is_caught(self):
        self.plant("| G honesty | 'blocked' names at least one open blocker |",
                   "| G honesty | every run is perfect |")

    def test_a_literal_approve_line_in_the_auditor_is_caught(self):
        self.plant("score >= line", "score >= 7.0", src=True)

    def test_drifted_audit_word_count_band_is_caught(self):
        self.plant("target * 0.9", "target * 0.8", src=True)

    # -- references + structure -----------------------------------------
    def test_renamed_script_is_caught(self):
        self.plant("`run-audit.py`", "`run-auditt.py`")

    def test_unknown_slash_command_is_caught(self):
        self.plant("/contentforge:cf-aeo-check", "/contentforge:cf-aeo-chek")

    def test_deleted_section_is_caught(self):
        self.plant("## What this contract does not promise", "## Notes")

    # -- precedence rule, researcher wording, reviewer schema -------------
    def test_wrong_composite_tolerance_in_the_contract_is_caught(self):
        self.plant("is more than 0.15 away", "is more than 0.25 away")

    def test_drifted_composite_tolerance_in_the_auditor_is_caught(self):
        self.plant("COMPOSITE_TOLERANCE = 0.15", "COMPOSITE_TOLERANCE = 0.5", src=True)

    def test_dropped_precedence_statement_is_caught(self):
        self.plant("the smaller cap governs", "the larger cap governs")

    def test_researcher_with_a_private_reliability_floor_is_caught(self):
        mutated = RESEARCHER.replace("At least 10 citable sources — citable means",
                                     "At least 10 citable sources (Reliability Score ≥7) — citable means", 1)
        self.assertNotEqual(mutated, RESEARCHER, "plant anchor not found in the researcher")
        self.assertTrue(check_gate1_wording(mutated))

    def test_researcher_dropping_the_high_reliability_rule_is_caught(self):
        mutated = RESEARCHER.replace("At least 5 of them with Reliability Score ≥8",
                                     "At least 3 of them with Reliability Score ≥8", 1)
        self.assertNotEqual(mutated, RESEARCHER)
        self.assertTrue(check_gate1_wording(mutated))

    def test_reviewer_that_stops_recording_the_applied_line_is_caught(self):
        mutated = REVIEWER.replace('"minimum_pass_score_applied": 7.0,', "", 1)
        self.assertNotEqual(mutated, REVIEWER)
        self.assertTrue(check_reviewer_records_what_the_auditor_reads(mutated, SRC))

    def test_reviewer_that_stops_resolving_industry_minimums_is_caught(self):
        mutated = REVIEWER.replace("Threshold resolution", "Threshold note", 1)
        self.assertNotEqual(mutated, REVIEWER)
        self.assertTrue(check_reviewer_records_what_the_auditor_reads(mutated, SRC))

    def test_auditor_that_stops_reading_a_recorded_field_is_caught(self):
        mutated = SRC.replace('review.get("minimum_pass_score_applied")', 'review.get("minimum_pass")')
        self.assertNotEqual(mutated, SRC)
        self.assertTrue(check_reviewer_records_what_the_auditor_reads(REVIEWER, mutated))


if __name__ == "__main__":
    unittest.main()
