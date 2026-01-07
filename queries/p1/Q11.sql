-- Q11: IT Infrastructure Impact
-- Paramètres: $1 = UPS_ID

WITH RECURSIVE downstream AS (
    SELECT eq.id, eq.name, eq.equipment_type, 1 AS depth
    FROM equipment eq
    JOIN edges e ON e.target_id = eq.id AND e.rel_type = 'FEEDS'
    WHERE e.source_id = $1

    UNION ALL

    SELECT eq.id, eq.name, eq.equipment_type, d.depth + 1
    FROM downstream d
    JOIN edges e ON e.source_id = d.id AND e.rel_type = 'FEEDS'
    JOIN equipment eq ON eq.id = e.target_id
    WHERE d.depth < 5
)
SELECT id AS equipment_id, name AS equipment_name, equipment_type, depth
FROM downstream
WHERE equipment_type IN ('RackServer', 'NetworkSwitch', 'StorageArray')
ORDER BY depth, equipment_type, id;
