-- Q11: IT Infrastructure Impact (P2 JSONB)
-- Paramètres: $1 = UPS_ID

WITH RECURSIVE downstream AS (
    SELECT n.id, n.name, n.data->>'equipment_type' AS equipment_type, 1 AS depth
    FROM nodes n
    JOIN edges e ON e.target_id = n.id AND e.rel_type = 'FEEDS'
    WHERE e.source_id = $1 AND n.node_type = 'Equipment'

    UNION ALL

    SELECT n.id, n.name, n.data->>'equipment_type', d.depth + 1
    FROM downstream d
    JOIN edges e ON e.source_id = d.id AND e.rel_type = 'FEEDS'
    JOIN nodes n ON n.id = e.target_id AND n.node_type = 'Equipment'
    WHERE d.depth < 5
)
SELECT id AS equipment_id, name AS equipment_name, equipment_type, depth
FROM downstream
WHERE equipment_type IN ('RackServer', 'NetworkSwitch', 'StorageArray')
ORDER BY depth, equipment_type, id;
