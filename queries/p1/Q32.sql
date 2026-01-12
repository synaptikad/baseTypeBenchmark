-- Q32: JSON Schema Validation
-- Status: IMPOSSIBLE pour P1 (pas de colonne JSONB)
-- Semantic: Validate JSONB structure of HVAC equipment
-- Parametres: $1 = DOMAIN

SELECT
    'IMPOSSIBLE' AS equipment_id,
    'P1 does not have JSONB columns for schema validation' AS name,
    'impossible' AS schema_status,
    ARRAY[]::text[] AS missing_fields;
