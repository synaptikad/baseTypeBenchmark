-- Q5: Orphans (P2 JSONB)
-- Pas de paramètre

SELECT
    n.id,
    n.data->>'equipment_type' AS type,
    n.name
FROM nodes n
WHERE n.node_type = 'Equipment'
  AND NOT EXISTS (
      SELECT 1 FROM edges e
      WHERE e.source_id = n.id OR e.target_id = n.id
  )
ORDER BY n.data->>'equipment_type', n.id;
