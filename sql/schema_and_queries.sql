-- Illustrative PostgreSQL schema for the Corporate Technology Intelligence demo.
-- All input data is synthetic. Review licensing, privacy and provenance before production use.

CREATE TABLE company_entity (
    entity_id TEXT PRIMARY KEY,
    legal_name TEXT NOT NULL,
    domain TEXT,
    country CHAR(2) NOT NULL,
    parent_entity_id TEXT REFERENCES company_entity(entity_id),
    entity_type TEXT NOT NULL CHECK (entity_type IN ('parent','subsidiary','independent')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE technology_relationship (
    relationship_id TEXT PRIMARY KEY,
    company_entity_id TEXT NOT NULL REFERENCES company_entity(entity_id),
    technology_provider_entity_id TEXT NOT NULL REFERENCES company_entity(entity_id),
    technology_category TEXT NOT NULL,
    relationship_type TEXT NOT NULL CHECK (relationship_type IN ('partnership','pilot','proof_of_concept','implementation','investment','acquisition')),
    announced_date DATE,
    source_type TEXT,
    source_reference TEXT,
    confidence NUMERIC(4,3) CHECK (confidence >= 0 AND confidence <= 1),
    notes TEXT,
    review_status TEXT NOT NULL DEFAULT 'human_review',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_relationship_company ON technology_relationship(company_entity_id);
CREATE INDEX idx_relationship_provider ON technology_relationship(technology_provider_entity_id);
CREATE INDEX idx_relationship_category_date ON technology_relationship(technology_category, announced_date DESC);
CREATE INDEX idx_relationship_review ON technology_relationship(review_status);

-- Query 1: recent relationships by technology category.
SELECT technology_category, relationship_type, COUNT(*) AS relationship_count
FROM technology_relationship
WHERE announced_date >= CURRENT_DATE - INTERVAL '12 months'
GROUP BY technology_category, relationship_type
ORDER BY relationship_count DESC;

-- Query 2: a company's technology ecosystem, preserving separate legal entities.
SELECT c.legal_name AS company_name,
       p.legal_name AS technology_provider,
       r.technology_category,
       r.relationship_type,
       r.announced_date,
       r.source_reference,
       r.confidence,
       r.review_status
FROM technology_relationship r
JOIN company_entity c ON c.entity_id = r.company_entity_id
JOIN company_entity p ON p.entity_id = r.technology_provider_entity_id
WHERE c.entity_id = 'C001'
ORDER BY r.announced_date DESC NULLS LAST;

-- Query 3: records requiring human review.
SELECT relationship_id, source_type, source_reference, confidence, announced_date
FROM technology_relationship
WHERE review_status = 'human_review'
   OR source_reference IS NULL
   OR confidence IS NULL
   OR confidence < 0.70
ORDER BY confidence NULLS FIRST;

-- Query 4: vendor coverage for a selected technology category.
SELECT p.legal_name AS technology_provider,
       COUNT(*) AS relationship_count,
       MAX(r.announced_date) AS latest_relationship
FROM technology_relationship r
JOIN company_entity p ON p.entity_id = r.technology_provider_entity_id
WHERE r.technology_category = 'Robotics'
  AND r.review_status = 'ready_for_human_approval'
GROUP BY p.legal_name
ORDER BY relationship_count DESC, latest_relationship DESC;
