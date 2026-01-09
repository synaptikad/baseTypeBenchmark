-- Q17: Capability Filter
-- Status: NATIVE pour P2
-- Paramètres: capability (string, ex: 'humidity_control')
-- Démontre: jsonb_array_elements_text() avec EXISTS subquery
-- Note: Plus robuste que @> containment pour paramètres dynamiques

SELECT
    eq.id AS equipment_id,
    eq.name,
    eq.data->>'equipment_type' AS equipment_type,
    eq.data->'capabilities' AS all_capabilities
FROM nodes eq
WHERE eq.node_type = 'Equipment'
  AND eq.data->>'domain' = 'HVAC'
  AND EXISTS (
      SELECT 1 FROM jsonb_array_elements_text(eq.data->'capabilities') AS cap
      WHERE cap = $1
  )
ORDER BY eq.data->>'equipment_type', eq.id;
