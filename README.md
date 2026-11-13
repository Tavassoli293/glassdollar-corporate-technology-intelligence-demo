# Corporate Technology Intelligence — Portfolio Prototype

**Independent portfolio project by Keyvan Tavassoli | Prepared for the GlassDollar Entrepreneur in Residence (Data) application**

A small, reproducible prototype showing how company–technology relationship data can be structured, validated, quality-scored, reviewed and presented as a commercial intelligence product.

> **Data and honesty notice:** All company names, domains, relationships, dates, source references and confidence values in this repository are fictional and synthetic. They do not describe real companies or partnerships. This is a self-initiated portfolio prototype; it is not GlassDollar data, not a production system, and not evidence of a previously deployed scraper or LLM pipeline.

## Product hypothesis

Enterprise strategy, innovation and procurement teams need more than lists of startups. They need traceable answers to questions such as:

- Which enterprises are connected to which technology providers?
- Is the relationship a partnership, pilot, proof of concept, implementation, investment or acquisition?
- What evidence supports the relationship, how reliable is it, and when was it last checked?
- Which records are safe to show to a customer, and which require a human reviewer?

The prototype treats **legal entities**, **relationships**, **evidence provenance**, **freshness** and **human review** as first-class concepts.

## What is included

- **Python pipeline:** validates input records, checks company references and parent-child entities, flags suspicious records, and calculates an explainable quality heuristic.
- **Output files:** validated relationship CSV, company-level technology summary CSV, JSON quality summary and a simple HTML report.
- **PostgreSQL schema and queries:** example relational model and commercial/product queries.
- **Unit tests:** deterministic tests using Python's standard library.
- **GitHub Actions:** automatically runs the test suite on pushes and pull requests.

## Repository structure

```text
.
├── data/
│   ├── companies.csv
│   └── relationships.csv
├── docs/
│   ├── PRODUCT_BRIEF.md
│   └── GITHUB_PUBLISH_STEPS_FA.md
├── output/
├── sql/
│   └── schema_and_queries.sql
├── src/
│   ├── validate_and_score.py
│   └── build_dashboard.py
├── tests/
│   └── test_pipeline.py
├── .github/workflows/tests.yml
├── .gitignore
├── LICENSE
├── pyproject.toml
└── README.md
```

## Quick start

Requirements: Python 3.10 or newer. No third-party Python packages are required.

### Windows (PowerShell)

```powershell
py -3 --version
py -3 src/validate_and_score.py --as-of 2026-11-13
py -3 src/build_dashboard.py
py -3 -m unittest discover -s tests -v
```

### macOS / Linux

```bash
python3 --version
python3 src/validate_and_score.py --as-of 2026-11-13
python3 src/build_dashboard.py
python3 -m unittest discover -s tests -v
```

Open `output/report.html` in a browser to see the demo report. The `--as-of` date makes recency scoring reproducible; omit it to use the current date.

## How the quality score works

The score is an **explainable demo heuristic**, not a probability, certification, or statistically validated prediction. It combines:

| Dimension | Weight |
|---|---:|
| Required-field completeness | 25% |
| Source-type weight | 30% |
| Supplied confidence value | 25% |
| Recency | 20% |

The score is used only as a triage aid. Invalid references, missing evidence, malformed dates, invalid confidence values and duplicate identifiers trigger human review even when a numerical score appears high. In production, weights and thresholds should be calibrated on a manually labelled dataset and agreed with domain experts.

## Legal-entity handling

The demo deliberately keeps a parent company and subsidiaries as separate entities linked by `parent_entity_id`. Similar names are not enough to merge records. A production entity-resolution workflow should use authoritative registration identifiers, jurisdiction, legal name, registered address, official domain, ownership disclosures, effective dates and source evidence. Ambiguous matches should remain separate and be routed to human review.

## Product extensions this prototype could support

1. **Corporate Technology Intelligence:** searchable, evidence-backed enterprise–technology relationships.
2. **Competitor Innovation Radar:** recurring alerts when competitors start partnerships, pilots or implementations.
3. **Technology Vendor Intelligence:** shortlist and compare providers based on independently verifiable evidence.
4. **API/MCP distribution:** expose appropriately licensed and approved records to customer tools and AI agents while retaining provenance.

These are product hypotheses for discussion, not existing live features.

## Data governance and production considerations

A real commercial product would require source-licensing review, lawful-basis and GDPR assessment where personal data is present, retention rules, correction and appeal workflows, access controls, audit logs, provenance, customer-specific usage rights and documented human-review procedures. This sample deliberately contains no personal data and uses synthetic records only.

## Current limitations

- No live web scraping or external API ingestion.
- No LLM extraction or classification.
- No production Postgres deployment or hosted API.
- No real company/partnership data; all records are synthetic.
- Quality weights are illustrative and require calibration before commercial use.

The next sensible increment would be to agree a labelled reference sample, measure precision/recall and entity-resolution error rates, then test one narrowly defined paid pilot with existing customers before investing in broader ingestion infrastructure.

## Author

**Keyvan Tavassoli** — Electrical Engineering, MBA, technical project delivery, B2B infrastructure, supplier and contractor coordination, integration & commissioning, and QA/QC.
