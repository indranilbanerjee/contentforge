#!/usr/bin/env python3
"""
generate-docx.py
================
ContentForge Phase 8 — generates a publication-ready .docx file from
Markdown content plus pipeline reports (SEO, quality, production details).

Usage:
    python3 generate-docx.py \
        --content path/to/article.md \
        --output path/to/output.docx \
        --reports path/to/reports.json \
        --brand "Brand Name" \
        --content-type article

If python-docx is not installed, it is auto-installed via pip.

Output structure:
    1. Title page (brand, date, type, score)
    2. Body — full article with H1/H2/H3 hierarchy
    3. Sources/Citations
    4. Appendix A — SEO Scorecard
    5. Appendix B — Quality Scorecard
    6. Appendix C — Production Details (phase timing, loops, metrics)

Reports JSON schema (all sections optional, missing = skipped):
    {
        "seo": {
            "primary_keyword": str,
            "keyword_density_pct": float,
            "meta_title": str,
            "meta_description": str,
            "schema_type": str,
            "internal_links": int,
            "seo_score": float
        },
        "quality": {
            "overall_score": float,
            "grade": str,  # A/B/C/D/F
            "dimensions": {
                "content_quality": float,
                "citation_integrity": float,
                "brand_compliance": float,
                "seo_performance": float,
                "readability": float
            },
            "review_date": str,
            "reviewer_notes": str
        },
        "production": {
            "phases_completed": [str, ...],
            "total_processing_time_seconds": float,
            "loops": int,
            "word_count": int,
            "citation_count": int,
            "source_reliability_avg": float,
            "flesch_kincaid_grade": float,
            "burstiness_score": float,
            "humanizer_patterns_removed": int,
            "em_dash_count": int,
            "ai_signal_score": float,  # 1-10, lower = more human
            "brand_compliance_violations": int,
            "factual_accuracy_pct": float,
            "hallucination_risk": str  # low/medium/high
        }
    }
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def ensure_docx():
    """Install python-docx if not present."""
    try:
        import docx  # noqa: F401
        return
    except ImportError:
        pass
    print("Installing python-docx...", file=sys.stderr)
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "--quiet", "python-docx>=1.1.0"]
    )


def parse_markdown_to_blocks(md_text):
    """
    Parse markdown into ordered blocks: (kind, content) tuples.
    kind in {'h1','h2','h3','para','bullet','ordered','table','hr','quote','code'}
    Strips YAML frontmatter if present.
    Strips ContentForge "completion card" / appendix sections that the agent may
    have inlined — those go in the proper appendix sections instead.
    """
    # Strip YAML frontmatter
    if md_text.lstrip().startswith("---"):
        end = md_text.find("\n---", 3)
        if end > 0:
            md_text = md_text[end + 4:].lstrip()

    # Strip everything from "## CONTENTFORGE — COMPLETION CARD" onwards if present
    # (that content moves into the appendix section).
    cutoff_patterns = [
        r"\n##\s+CONTENTFORGE\s*[—-]+\s*COMPLETION\s+CARD",
        r"\n##\s+Appendix\s+[ABC]:",
        r"\n#\s+Appendix\s+[ABC]:",
    ]
    for pat in cutoff_patterns:
        m = re.search(pat, md_text, re.IGNORECASE)
        if m:
            md_text = md_text[:m.start()].rstrip()

    blocks = []
    lines = md_text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()

        if not line.strip():
            i += 1
            continue

        if line.startswith("# "):
            blocks.append(("h1", line[2:].strip()))
            i += 1
        elif line.startswith("## "):
            blocks.append(("h2", line[3:].strip()))
            i += 1
        elif line.startswith("### "):
            blocks.append(("h3", line[4:].strip()))
            i += 1
        elif line.startswith("---") and len(line.strip()) >= 3 and set(line.strip()) <= {"-"}:
            blocks.append(("hr", ""))
            i += 1
        elif line.startswith("> "):
            quote_lines = []
            while i < len(lines) and lines[i].startswith(">"):
                quote_lines.append(lines[i].lstrip("> ").rstrip())
                i += 1
            blocks.append(("quote", " ".join(quote_lines)))
        elif line.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[-: |]+\|", lines[i + 1]):
            table_lines = []
            while i < len(lines) and lines[i].startswith("|"):
                table_lines.append(lines[i].rstrip())
                i += 1
            blocks.append(("table", table_lines))
        elif line.startswith(("- ", "* ")):
            bullet_lines = []
            while i < len(lines) and lines[i].startswith(("- ", "* ")):
                bullet_lines.append(lines[i][2:].rstrip())
                i += 1
            blocks.append(("bullet", bullet_lines))
        elif re.match(r"^\d+\. ", line):
            ordered_lines = []
            while i < len(lines) and re.match(r"^\d+\. ", lines[i]):
                ordered_lines.append(re.sub(r"^\d+\. ", "", lines[i]).rstrip())
                i += 1
            blocks.append(("ordered", ordered_lines))
        elif line.startswith("```"):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1
            blocks.append(("code", "\n".join(code_lines)))
        else:
            para_lines = [line]
            i += 1
            while i < len(lines) and lines[i].strip() and not lines[i].startswith(
                ("#", ">", "|", "- ", "* ", "```", "---")
            ) and not re.match(r"^\d+\. ", lines[i]):
                para_lines.append(lines[i].rstrip())
                i += 1
            blocks.append(("para", " ".join(para_lines)))

    return blocks


def add_inline_runs(paragraph, text):
    """Render simple **bold**, *italic*, [text](url), `code` markdown inline."""
    from docx.shared import Pt, RGBColor

    pattern = re.compile(
        r"\*\*([^*]+)\*\*|\*([^*]+)\*|`([^`]+)`|\[([^\]]+)\]\(([^)]+)\)"
    )
    pos = 0
    for m in pattern.finditer(text):
        if m.start() > pos:
            paragraph.add_run(text[pos:m.start()])
        bold_t, ital_t, code_t, link_t, link_url = m.groups()
        if bold_t is not None:
            run = paragraph.add_run(bold_t)
            run.bold = True
        elif ital_t is not None:
            run = paragraph.add_run(ital_t)
            run.italic = True
        elif code_t is not None:
            run = paragraph.add_run(code_t)
            run.font.name = "Consolas"
            run.font.size = Pt(10)
        elif link_t is not None:
            run = paragraph.add_run(link_t)
            run.font.color.rgb = RGBColor(0x00, 0x66, 0xCC)
            run.font.underline = True
        pos = m.end()
    if pos < len(text):
        paragraph.add_run(text[pos:])


def render_blocks(doc, blocks):
    """Render parsed markdown blocks into the docx document."""
    from docx.shared import Pt, Inches, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    for kind, content in blocks:
        if kind == "h1":
            p = doc.add_paragraph()
            run = p.add_run(content)
            run.bold = True
            run.font.size = Pt(24)
            p.paragraph_format.space_after = Pt(12)
        elif kind == "h2":
            p = doc.add_paragraph()
            run = p.add_run(content)
            run.bold = True
            run.font.size = Pt(18)
            p.paragraph_format.space_before = Pt(18)
            p.paragraph_format.space_after = Pt(8)
        elif kind == "h3":
            p = doc.add_paragraph()
            run = p.add_run(content)
            run.bold = True
            run.font.size = Pt(14)
            p.paragraph_format.space_before = Pt(12)
            p.paragraph_format.space_after = Pt(6)
        elif kind == "para":
            p = doc.add_paragraph()
            add_inline_runs(p, content)
            p.paragraph_format.space_after = Pt(6)
        elif kind == "bullet":
            for item in content:
                p = doc.add_paragraph(style="List Bullet")
                add_inline_runs(p, item)
        elif kind == "ordered":
            for item in content:
                p = doc.add_paragraph(style="List Number")
                add_inline_runs(p, item)
        elif kind == "quote":
            p = doc.add_paragraph()
            run = p.add_run(content)
            run.italic = True
            p.paragraph_format.left_indent = Inches(0.5)
            p.paragraph_format.space_after = Pt(6)
        elif kind == "code":
            p = doc.add_paragraph()
            run = p.add_run(content)
            run.font.name = "Consolas"
            run.font.size = Pt(10)
            p.paragraph_format.left_indent = Inches(0.5)
        elif kind == "hr":
            p = doc.add_paragraph()
            run = p.add_run("─" * 60)
            run.font.color.rgb = RGBColor(0xCC, 0xCC, 0xCC)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif kind == "table":
            try:
                rows = [
                    [c.strip() for c in line.strip("|").split("|")]
                    for line in content
                    if not re.match(r"^\|[-: |]+\|", line)
                ]
                if not rows:
                    continue
                table = doc.add_table(rows=len(rows), cols=len(rows[0]))
                table.style = "Light Grid Accent 1"
                for r_idx, row in enumerate(rows):
                    for c_idx, cell_text in enumerate(row):
                        if c_idx >= len(rows[0]):
                            continue
                        cell = table.cell(r_idx, c_idx)
                        cell.text = ""
                        p = cell.paragraphs[0]
                        add_inline_runs(p, cell_text)
                        if r_idx == 0:
                            for run in p.runs:
                                run.bold = True
                doc.add_paragraph()
            except Exception as e:
                print(f"Table render error: {e}", file=sys.stderr)


def add_title_page(doc, brand, content_type, title, score, grade):
    from docx.shared import Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(brand.upper())
    run.bold = True
    run.font.size = Pt(14)
    run.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(content_type.replace("_", " ").upper())
    run.font.size = Pt(11)
    run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)

    doc.add_paragraph()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(title)
    run.bold = True
    run.font.size = Pt(20)

    doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(f"Generated by ContentForge — {datetime.now().strftime('%B %d, %Y')}")
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)

    if score is not None:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(f"Quality Score: {score}/10  •  Grade: {grade}")
        run.font.size = Pt(11)
        run.font.color.rgb = RGBColor(0x33, 0x66, 0x33)

    doc.add_page_break()


def add_appendices(doc, reports):
    """Add Appendix A (SEO), B (Quality), C (Production) from reports JSON."""
    from docx.shared import Pt
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    seo = reports.get("seo")
    quality = reports.get("quality")
    production = reports.get("production")

    if not (seo or quality or production):
        return

    doc.add_page_break()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("APPENDICES")
    run.bold = True
    run.font.size = Pt(20)
    doc.add_paragraph()

    if seo:
        p = doc.add_paragraph()
        run = p.add_run("Appendix A — SEO Scorecard")
        run.bold = True
        run.font.size = Pt(16)
        rows = [
            ("Metric", "Value"),
            ("Primary keyword", str(seo.get("primary_keyword", "—"))),
            ("Keyword density", f"{seo.get('keyword_density_pct', 0):.2f}%"),
            ("Meta title", str(seo.get("meta_title", "—"))),
            ("Meta description", str(seo.get("meta_description", "—"))),
            ("Schema type", str(seo.get("schema_type", "—"))),
            ("Internal links", str(seo.get("internal_links", 0))),
            ("SEO score", f"{seo.get('seo_score', 0):.2f}/10"),
        ]
        table = doc.add_table(rows=len(rows), cols=2)
        table.style = "Light Grid Accent 1"
        for r_idx, (k, v) in enumerate(rows):
            table.cell(r_idx, 0).text = k
            table.cell(r_idx, 1).text = v
            if r_idx == 0:
                for cell in [table.cell(r_idx, 0), table.cell(r_idx, 1)]:
                    for run in cell.paragraphs[0].runs:
                        run.bold = True
        doc.add_paragraph()

    if quality:
        p = doc.add_paragraph()
        run = p.add_run("Appendix B — Quality Scorecard")
        run.bold = True
        run.font.size = Pt(16)
        dims = quality.get("dimensions", {})
        rows = [
            ("Dimension", "Score (0-10)", "Weight", "Status"),
            ("Content Quality", f"{dims.get('content_quality', 0):.2f}", "30%",
             "PASS" if dims.get("content_quality", 0) >= 7.0 else "FAIL"),
            ("Citation Integrity", f"{dims.get('citation_integrity', 0):.2f}", "25%",
             "PASS" if dims.get("citation_integrity", 0) >= 7.0 else "FAIL"),
            ("Brand Compliance", f"{dims.get('brand_compliance', 0):.2f}", "20%",
             "PASS" if dims.get("brand_compliance", 0) >= 7.0 else "FAIL"),
            ("SEO Performance", f"{dims.get('seo_performance', 0):.2f}", "15%",
             "PASS" if dims.get("seo_performance", 0) >= 7.0 else "FAIL"),
            ("Readability", f"{dims.get('readability', 0):.2f}", "10%",
             "PASS" if dims.get("readability", 0) >= 7.0 else "FAIL"),
            ("OVERALL", f"{quality.get('overall_score', 0):.2f}", "100%",
             quality.get("grade", "—")),
        ]
        table = doc.add_table(rows=len(rows), cols=4)
        table.style = "Light Grid Accent 1"
        for r_idx, row in enumerate(rows):
            for c_idx, cell_text in enumerate(row):
                cell = table.cell(r_idx, c_idx)
                cell.text = cell_text
                if r_idx == 0 or r_idx == len(rows) - 1:
                    for run in cell.paragraphs[0].runs:
                        run.bold = True
        if quality.get("review_date"):
            p = doc.add_paragraph()
            run = p.add_run(f"Reviewed: {quality['review_date']}")
            run.italic = True
            run.font.size = Pt(10)
        if quality.get("reviewer_notes"):
            p = doc.add_paragraph()
            run = p.add_run(f"Notes: {quality['reviewer_notes']}")
            run.italic = True
            run.font.size = Pt(10)
        doc.add_paragraph()

    if production:
        p = doc.add_paragraph()
        run = p.add_run("Appendix C — Production Details")
        run.bold = True
        run.font.size = Pt(16)

        rows = [
            ("Metric", "Value"),
            ("Phases completed", ", ".join(production.get("phases_completed", []))),
            ("Total processing time", f"{production.get('total_processing_time_seconds', 0):.1f}s"),
            ("Loops (max 5)", str(production.get("loops", 0))),
            ("Word count", str(production.get("word_count", 0))),
            ("Citation count", str(production.get("citation_count", 0))),
            ("Source reliability (avg)", f"{production.get('source_reliability_avg', 0):.2f}/10"),
            ("Flesch-Kincaid grade", f"{production.get('flesch_kincaid_grade', 0):.1f}"),
            ("Burstiness score", f"{production.get('burstiness_score', 0):.2f} (target ≥0.7)"),
            ("Humanizer patterns removed", str(production.get("humanizer_patterns_removed", 0))),
            ("Em dash count", f"{production.get('em_dash_count', 0)} (target ≤1-2 per 500w)"),
            ("AI signal score", f"{production.get('ai_signal_score', 0):.1f}/10 (target ≤3)"),
            ("Brand compliance violations", str(production.get("brand_compliance_violations", 0))),
            ("Factual accuracy", f"{production.get('factual_accuracy_pct', 0):.1f}%"),
            ("Hallucination risk", str(production.get("hallucination_risk", "—"))),
        ]
        table = doc.add_table(rows=len(rows), cols=2)
        table.style = "Light Grid Accent 1"
        for r_idx, (k, v) in enumerate(rows):
            table.cell(r_idx, 0).text = k
            table.cell(r_idx, 1).text = str(v)
            if r_idx == 0:
                for cell in [table.cell(r_idx, 0), table.cell(r_idx, 1)]:
                    for run in cell.paragraphs[0].runs:
                        run.bold = True


def main():
    parser = argparse.ArgumentParser(description="Generate ContentForge .docx output")
    parser.add_argument("--content", required=True, help="Markdown file with article body")
    parser.add_argument("--output", required=True, help="Output .docx path")
    parser.add_argument("--reports", help="Optional reports JSON for appendices")
    parser.add_argument("--brand", default="Brand", help="Brand name for header")
    parser.add_argument("--content-type", default="article", help="article/blog/whitepaper/faq/research_paper")
    parser.add_argument("--title", help="Override title (else extracts from first H1)")
    args = parser.parse_args()

    ensure_docx()
    from docx import Document
    from docx.shared import Pt, Inches

    content_path = Path(args.content)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    md_text = content_path.read_text(encoding="utf-8")
    blocks = parse_markdown_to_blocks(md_text)

    title = args.title
    if not title:
        for kind, content in blocks:
            if kind == "h1":
                title = content
                break
    if not title:
        title = output_path.stem

    reports = {}
    if args.reports and Path(args.reports).exists():
        try:
            reports = json.loads(Path(args.reports).read_text(encoding="utf-8"))
        except Exception as e:
            print(f"Warning: could not parse reports JSON: {e}", file=sys.stderr)

    score = reports.get("quality", {}).get("overall_score")
    grade = reports.get("quality", {}).get("grade", "—")

    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)
    for section in doc.sections:
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)

    add_title_page(doc, args.brand, args.content_type, title, score, grade)
    blocks_no_title = [b for b in blocks if not (b[0] == "h1" and b[1] == title)]
    render_blocks(doc, blocks_no_title)
    add_appendices(doc, reports)

    doc.save(output_path)
    print(json.dumps({
        "status": "success",
        "output": str(output_path),
        "size_bytes": output_path.stat().st_size,
        "title": title,
        "brand": args.brand,
        "content_type": args.content_type,
        "score": score,
        "grade": grade,
        "reports_included": list(reports.keys()),
    }))


if __name__ == "__main__":
    main()
