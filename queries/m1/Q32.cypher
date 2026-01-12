// Q32: JSON Schema Validation
// Status: DEGRADED pour M1 (pas d'operateurs JSON natifs)
// Semantic: Validate JSONB structure of HVAC equipment
// Parametres: $domain
// Note: Cypher n'a pas d'opérateurs ? / @> / jsonb_typeof

MATCH (eq:Equipment)
WHERE eq.domain = $domain
WITH eq,
     CASE WHEN eq.protocol IS NOT NULL THEN true ELSE false END AS has_protocol,
     CASE WHEN eq.metadata IS NOT NULL THEN true ELSE false END AS has_metadata
RETURN
    eq.id AS equipment_id,
    eq.name AS name,
    CASE WHEN has_protocol AND has_metadata THEN 'valid' ELSE 'invalid' END AS schema_status,
    CASE
        WHEN NOT has_protocol AND NOT has_metadata THEN ['protocol', 'metadata']
        WHEN NOT has_protocol THEN ['protocol']
        WHEN NOT has_metadata THEN ['metadata']
        ELSE []
    END AS missing_fields
ORDER BY schema_status, equipment_id;
