import sys
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from validate_and_score import normalise_name, recency_factor, score_relationship, validate_companies  # noqa: E402


class PipelineTests(unittest.TestCase):
    def test_name_normalisation(self):
        self.assertEqual(normalise_name("Northstar Robotics GmbH"), "northstar robotics gmbh")

    def test_parent_and_subsidiary_are_separate_entities(self):
        companies = [
            {"entity_id": "P", "legal_name": "Example Group SE", "domain": "group.example", "country": "DE", "parent_entity_id": "", "entity_type": "parent"},
            {"entity_id": "S", "legal_name": "Example Robotics GmbH", "domain": "robotics.example", "country": "DE", "parent_entity_id": "P", "entity_type": "subsidiary"},
        ]
        by_id, issues = validate_companies(companies)
        self.assertIn("P", by_id)
        self.assertIn("S", by_id)
        self.assertEqual(by_id["S"]["parent_entity_id"], "P")
        self.assertEqual(issues, [])

    def test_parent_cycle_is_detected(self):
        companies = [
            {"entity_id": "A", "legal_name": "A GmbH", "domain": "a.example", "country": "DE", "parent_entity_id": "B", "entity_type": "subsidiary"},
            {"entity_id": "B", "legal_name": "B GmbH", "domain": "b.example", "country": "DE", "parent_entity_id": "A", "entity_type": "subsidiary"},
        ]
        _, issues = validate_companies(companies)
        self.assertTrue(any("cycle" in issue for issue in issues))

    def test_invalid_confidence_is_flagged(self):
        row = {"relationship_id":"R", "company_entity_id":"C1", "technology_provider_entity_id":"C2", "technology_category":"Robotics", "relationship_type":"pilot", "announced_date":"2026-01-01", "source_type":"press_release", "source_reference":"synthetic://source/test", "confidence":"1.5"}
        _, issues = score_relationship(row, as_of=date(2026, 11, 13))
        self.assertIn("confidence must be between 0 and 1", issues)

    def test_missing_source_is_flagged(self):
        row = {"relationship_id":"R", "company_entity_id":"C1", "technology_provider_entity_id":"C2", "technology_category":"Robotics", "relationship_type":"pilot", "announced_date":"2026-01-01", "source_type":"", "source_reference":"synthetic://source/test", "confidence":"0.8"}
        _, issues = score_relationship(row, as_of=date(2026, 11, 13))
        self.assertIn("missing source_type", issues)

    def test_future_date_is_flagged(self):
        row = {"relationship_id":"R", "company_entity_id":"C1", "technology_provider_entity_id":"C2", "technology_category":"Robotics", "relationship_type":"pilot", "announced_date":"2027-01-01", "source_type":"press_release", "source_reference":"synthetic://source/test", "confidence":"0.8"}
        _, issues = score_relationship(row, as_of=date(2026, 11, 13))
        self.assertIn("missing, invalid, or future announced_date", issues)

    def test_recency_factors_are_deterministic(self):
        self.assertEqual(recency_factor("2026-11-01", as_of=date(2026, 11, 13)), 1.0)
        self.assertEqual(recency_factor("2024-01-01", as_of=date(2026, 11, 13)), 0.6)

    def test_invalid_relationship_type_is_flagged(self):
        row = {"relationship_id":"R", "company_entity_id":"C1", "technology_provider_entity_id":"C2", "technology_category":"Robotics", "relationship_type":"rumour", "announced_date":"2026-01-01", "source_type":"press_release", "source_reference":"synthetic://source/test", "confidence":"0.8"}
        _, issues = score_relationship(row, as_of=date(2026, 11, 13))
        self.assertTrue(any("invalid relationship_type" in issue for issue in issues))


if __name__ == "__main__":
    unittest.main()
