-- Q17: Capability Filter
-- Status: NATIVE pour P2
-- Paramètres: $1 = CAPABILITY (string, ex: 'humidity_control')

SELECT
    eq.id AS equipment_id,
    eq.name,
    eq.data->>'equipment_type' AS equipment_type,
    eq.data->'capabilities' AS all_capabilities
FROM nodes eq
WHERE eq.node_type = 'Equipment'
  AND eq.data->>'domain' = 'HVAC'
  AND eq.data->'capabilities' @> to_jsonb($1::text)
ORDER BY eq.data->>'equipment_type', eq.id;
