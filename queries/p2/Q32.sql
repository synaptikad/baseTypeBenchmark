-- Q32: JSON Schema Validation (P2 JSONB)
-- Status: NATIVE pour P2 (Operateurs JSONB)
-- Semantic: Validate JSONB structure of HVAC equipment
-- Parametres: $1 = DOMAIN

SELECT
    n.id AS equipment_id,
    n.name AS name,
    CASE
        WHEN n.data ? 'protocol'
             AND jsonb_typeof(n.data->'protocol') = 'object'
             AND n.data ? 'metadata'
             AND jsonb_typeof(n.data->'metadata') = 'object'
        THEN 'valid'
        ELSE 'invalid'
    END AS schema_status,
    ARRAY_REMOVE(ARRAY[
        CASE WHEN NOT n.data ? 'protocol' THEN 'protocol'::text END,
        CASE WHEN NOT n.data ? 'metadata' THEN 'metadata'::text END,
        CASE WHEN n.data ? 'protocol' AND jsonb_typeof(n.data->'protocol') != 'object'
             THEN 'protocol_type'::text END,
        CASE WHEN n.data ? 'metadata' AND jsonb_typeof(n.data->'metadata') != 'object'
             THEN 'metadata_type'::text END
    ], NULL::text) AS missing_fields
FROM nodes n
WHERE n.node_type = 'Equipment'
  AND n.data @> jsonb_build_object('domain', $1::text)
ORDER BY
    CASE
        WHEN n.data ? 'protocol' AND n.data ? 'metadata' THEN 'valid'
        ELSE 'invalid'
    END,
    n.id;
