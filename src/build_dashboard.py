#!/usr/bin/env python3
"""Build a static HTML report from the demo pipeline outputs."""
from __future__ import annotations
import csv
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"


def main() -> None:
    summary_path = OUT / "quality_summary.json"
    records_path = OUT / "validated_relationships.csv"
    if not summary_path.exists() or not records_path.exists():
        raise SystemExit("Run `python src/validate_and_score.py` first.")

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    with records_path.open("r", encoding="utf-8", newline="") as handle:
        records = list(csv.DictReader(handle))

    rows = []
    for record in records:
        status = record.get("review_status", "")
        badge_class = "review" if status == "human_review" else "ready"
        cells = [
            record.get("relationship_id", ""),
            f"{record.get('company_entity_id', '')} → {record.get('technology_provider_entity_id', '')}",
            record.get("technology_category", ""),
            record.get("relationship_type", ""),
            record.get("quality_score", ""),
        ]
        cells_html = "".join(f"<td>{html.escape(str(value))}</td>" for value in cells)
        rows.append(
            f"<tr>{cells_html}<td><span class='badge {badge_class}'>{html.escape(status)}</span></td>"
            f"<td>{html.escape(record.get('quality_issues', '') or '—')}</td></tr>"
        )

    category_items = "".join(
        f"<li><span>{html.escape(category)}</span><strong>{count}</strong></li>"
        for category, count in summary.get("relationship_counts_by_category", {}).items()
    )

    page = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Corporate Technology Intelligence — Demo Report</title>
<style>
:root{--ink:#17243a;--muted:#65738a;--line:#e1e7ef;--bg:#f4f7fb;--card:#fff}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 Arial,sans-serif}
main{max-width:1200px;margin:36px auto;padding:0 22px}header{margin-bottom:24px}h1{margin:0 0 6px;font-size:30px}.sub{color:var(--muted)}
.notice{background:#fff8e7;border:1px solid #f1d58d;padding:13px 16px;border-radius:10px;margin:18px 0}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px;margin:18px 0}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px}.label{color:var(--muted);font-size:13px}.value{font-size:28px;font-weight:700;margin-top:4px}
section{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px;margin:16px 0}h2{font-size:18px;margin:0 0 14px}
ul{margin:0;padding:0;list-style:none;display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:8px}li{display:flex;justify-content:space-between;border-bottom:1px solid var(--line);padding:8px 4px}
.table-wrap{overflow:auto}table{border-collapse:collapse;width:100%;min-width:950px;font-size:13px}th,td{border-bottom:1px solid var(--line);padding:10px;text-align:left;vertical-align:top}th{background:#f8fafc;color:#48566b}
.badge{display:inline-block;padding:3px 8px;border-radius:20px;font-size:11px;white-space:nowrap}.review{background:#fff0d8;color:#8b4d00}.ready{background:#e6f6ee;color:#17633e}
footer{color:var(--muted);font-size:12px;margin:20px 0 40px}
</style></head><body><main>
<header><h1>Corporate Technology Intelligence</h1><div class="sub">Synthetic portfolio prototype · Data quality and relationship review</div></header>
<div class="notice"><strong>Demo data notice:</strong> All entities and relationships shown here are fictional and synthetic. The score is an illustrative heuristic, not a probability or verified fact.</div>
<div class="cards">
<div class="card"><div class="label">Companies processed</div><div class="value">__COMPANIES__</div></div>
<div class="card"><div class="label">Relationships processed</div><div class="value">__RELATIONSHIPS__</div></div>
<div class="card"><div class="label">Flagged for human review</div><div class="value">__FLAGGED__</div></div>
<div class="card"><div class="label">Average quality score</div><div class="value">__AVERAGE__</div></div>
</div>
<section><h2>Relationship volume by technology category</h2><ul>__CATEGORIES__</ul></section>
<section><h2>Relationship records</h2><div class="table-wrap"><table><thead><tr><th>ID</th><th>Entities</th><th>Technology</th><th>Relationship</th><th>Score</th><th>Status</th><th>Issues</th></tr></thead><tbody>__ROWS__</tbody></table></div></section>
<footer>As-of date: __AS_OF__ · Review threshold: __THRESHOLD__ · Generated locally from CSV input. No external services are called.</footer>
</main></body></html>"""

    replacements = {
        "__COMPANIES__": str(summary["companies_processed"]),
        "__RELATIONSHIPS__": str(summary["relationships_processed"]),
        "__FLAGGED__": str(summary["relationships_flagged_for_human_review"]),
        "__AVERAGE__": str(summary["average_quality_score"]),
        "__CATEGORIES__": category_items,
        "__ROWS__": "".join(rows),
        "__AS_OF__": html.escape(summary["as_of_date"]),
        "__THRESHOLD__": str(summary["review_threshold"]),
    }
    for marker, value in replacements.items():
        page = page.replace(marker, value)

    report_path = OUT / "report.html"
    report_path.write_text(page, encoding="utf-8")
    print(f"Created {report_path}")


if __name__ == "__main__":
    main()
