#!/usr/bin/env python3
"""Validate and score synthetic company–technology relationship records.

Educational portfolio prototype only. Synthetic input; no scraping, external
API calls, LLM processing, or production database is used.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "output"
COMPANIES_FILE = DATA_DIR / "companies.csv"
RELATIONSHIPS_FILE = DATA_DIR / "relationships.csv"
VALID_TYPES = {"partnership", "pilot", "proof_of_concept", "implementation", "investment", "acquisition"}
SOURCE_WEIGHTS = {
    "regulatory_filing": 1.00,
    "company_announcement": 0.95,
    "case_study": 0.90,
    "press_release": 0.85,
    "partner_announcement": 0.80,
    "news_article": 0.65,
}
REVIEW_THRESHOLD = 70.0
REQUIRED_COMPANY_FIELDS = ("entity_id", "legal_name", "domain", "country", "entity_type")
REQUIRED_RELATIONSHIP_FIELDS = (
    "relationship_id", "company_entity_id", "technology_provider_entity_id",
    "technology_category", "relationship_type", "announced_date", "source_type",
    "source_reference", "confidence",
)


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Required input file not found: {path}")
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def normalise_name(value: str) -> str:
    """Simple text normalisation; not a legal-entity matching algorithm."""
    value = (value or "").casefold().strip()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return " ".join(value.split())


def recency_factor(announced_date: str, as_of: date | None = None) -> float:
    as_of = as_of or date.today()
    try:
        parsed = date.fromisoformat((announced_date or "").strip())
    except (TypeError, ValueError):
        return 0.0
    age_days = (as_of - parsed).days
    if age_days < 0:
        return 0.0
    if age_days <= 365:
        return 1.0
    if age_days <= 730:
        return 0.8
    if age_days <= 1460:
        return 0.6
    return 0.4


def validate_companies(companies: list[dict[str, str]]) -> tuple[dict[str, dict[str, str]], list[str]]:
    by_id: dict[str, dict[str, str]] = {}
    issues: list[str] = []
    for index, row in enumerate(companies, start=2):
        entity_id = (row.get("entity_id") or "").strip()
        if not entity_id:
            issues.append(f"Company CSV row {index}: missing entity_id")
            continue
        if entity_id in by_id:
            issues.append(f"Duplicate company entity_id: {entity_id}")
            continue
        for field in REQUIRED_COMPANY_FIELDS:
            if not (row.get(field) or "").strip():
                issues.append(f"{entity_id}: missing {field}")
        by_id[entity_id] = row

    for entity_id, row in by_id.items():
        parent_id = (row.get("parent_entity_id") or "").strip()
        if parent_id and parent_id not in by_id:
            issues.append(f"{entity_id}: unknown parent_entity_id {parent_id}")
        if parent_id == entity_id:
            issues.append(f"{entity_id}: entity cannot be its own parent")

    # Detect cycles such as A -> B -> A.
    for entity_id in by_id:
        seen: set[str] = set()
        current = entity_id
        while current and current in by_id:
            if current in seen:
                issues.append(f"Parent hierarchy cycle detected from {entity_id}")
                break
            seen.add(current)
            current = (by_id[current].get("parent_entity_id") or "").strip()
    return by_id, sorted(set(issues))


def score_relationship(row: dict[str, str], as_of: date | None = None) -> tuple[float, list[str]]:
    issues: list[str] = []
    completeness = sum(bool((row.get(field) or "").strip()) for field in REQUIRED_RELATIONSHIP_FIELDS) / len(REQUIRED_RELATIONSHIP_FIELDS)

    relationship_type = (row.get("relationship_type") or "").strip()
    if relationship_type not in VALID_TYPES:
        issues.append(f"invalid relationship_type: {relationship_type or 'missing'}")

    source_type = (row.get("source_type") or "").strip()
    if not source_type:
        issues.append("missing source_type")
    source_weight = SOURCE_WEIGHTS.get(source_type, 0.40)
    if source_type and source_type not in SOURCE_WEIGHTS:
        issues.append(f"unrecognised source_type: {source_type}")

    try:
        confidence = float(row.get("confidence", ""))
    except (TypeError, ValueError):
        confidence = -1.0
    if not 0 <= confidence <= 1:
        issues.append("confidence must be between 0 and 1")
        confidence = 0.0

    announced_date = (row.get("announced_date") or "").strip()
    freshness = recency_factor(announced_date, as_of=as_of)
    if freshness == 0.0:
        issues.append("missing, invalid, or future announced_date")

    score = round(100 * (0.25 * completeness + 0.30 * source_weight + 0.25 * confidence + 0.20 * freshness), 1)
    return score, issues


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def run(as_of: date | None = None) -> dict[str, Any]:
    companies = read_csv(COMPANIES_FILE)
    relationships = read_csv(RELATIONSHIPS_FILE)
    company_by_id, company_issues = validate_companies(companies)

    duplicate_ids = [rid for rid, count in Counter((r.get("relationship_id") or "").strip() for r in relationships).items() if rid and count > 1]
    relationship_id_issues = [f"Duplicate relationship_id: {rid}" for rid in duplicate_ids]

    output_rows: list[dict[str, str]] = []
    issue_count = len(company_issues) + len(relationship_id_issues)
    review_count = 0
    scores: list[float] = []
    category_counts: Counter[str] = Counter()
    company_activity: dict[str, list[dict[str, str]]] = defaultdict(list)

    for row in relationships:
        issues: list[str] = []
        left = (row.get("company_entity_id") or "").strip()
        right = (row.get("technology_provider_entity_id") or "").strip()
        if left not in company_by_id:
            issues.append(f"unknown company_entity_id: {left}")
        if right not in company_by_id:
            issues.append(f"unknown technology_provider_entity_id: {right}")
        score, scoring_issues = score_relationship(row, as_of=as_of)
        issues.extend(scoring_issues)
        rid = (row.get("relationship_id") or "").strip()
        if rid in duplicate_ids:
            issues.append(f"duplicate relationship_id: {rid}")
        review = bool(issues) or score < REVIEW_THRESHOLD
        review_count += int(review)
        issue_count += len(issues)
        scores.append(score)
        category_counts[row.get("technology_category", "Unknown")] += 1
        if left in company_by_id and right in company_by_id:
            company_activity[left].append(row)
        output_rows.append({
            **row,
            "quality_score": f"{score:.1f}",
            "review_status": "human_review" if review else "ready_for_human_approval",
            "quality_issues": "; ".join(issues),
        })

    OUTPUT_DIR.mkdir(exist_ok=True)
    write_csv(OUTPUT_DIR / "validated_relationships.csv", output_rows)

    company_summary = []
    for entity_id, company in company_by_id.items():
        rels = company_activity.get(entity_id, [])
        company_summary.append({
            "entity_id": entity_id,
            "legal_name": company.get("legal_name", ""),
            "country": company.get("country", ""),
            "relationship_count": str(len(rels)),
            "technology_categories": "; ".join(sorted({r.get("technology_category", "") for r in rels if r.get("technology_category")})),
        })
    write_csv(OUTPUT_DIR / "company_technology_summary.csv", company_summary)

    summary = {
        "demo_notice": "Synthetic data only; quality scores are illustrative heuristics, not probabilities.",
        "as_of_date": (as_of or date.today()).isoformat(),
        "companies_processed": len(companies),
        "relationships_processed": len(relationships),
        "relationships_flagged_for_human_review": review_count,
        "relationships_ready_for_human_approval": len(relationships) - review_count,
        "total_quality_issues": issue_count,
        "average_quality_score": round(sum(scores) / len(scores), 1) if scores else 0,
        "review_threshold": REVIEW_THRESHOLD,
        "relationship_counts_by_category": dict(sorted(category_counts.items())),
        "company_issues": company_issues,
        "relationship_id_issues": relationship_id_issues,
    }
    (OUTPUT_DIR / "quality_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate synthetic company–technology relationship data.")
    parser.add_argument("--as-of", help="ISO date for reproducible freshness scoring (YYYY-MM-DD).")
    args = parser.parse_args()
    as_of = date.fromisoformat(args.as_of) if args.as_of else None
    print(json.dumps(run(as_of=as_of), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
