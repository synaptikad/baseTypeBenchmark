-- Q3: Space Services (P2 JSONB)
-- Paramètre: $1 = SPACE_ID

SELECT
    n.id AS equipment_id,
    n.name AS equipment_name,
    n.data->>'equipment_type' AS equipment_type,
    ed.rel_type AS relation_type
FROM edges ed
JOIN nodes n ON n.id = ed.source_id AND n.node_type = 'Equipment'
WHERE ed.target_id = $1
  AND ed.rel_type = 'SERVES'
ORDER BY ed.rel_type, n.id;
