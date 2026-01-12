-- Q33: Latest Value per Space (P2 JSONB)
-- Status: NATIVE pour P2 (LATERAL JOIN optimise)
-- Semantic: Get latest value for each point per space
-- Parametres: $1 = BUILDING_ID

SELECT
    s.id AS space_id,
    s.name AS space_name,
    latest.point_id,
    p.data->>'quantity' AS quantity,
    latest.last_value,
    latest.last_time
FROM nodes f
JOIN nodes s ON s.data->>'floor_id' = f.id AND s.node_type = 'Space'
JOIN edges e ON e.target_id = s.id AND e.rel_type = 'SERVES'
JOIN nodes eq ON eq.id = e.source_id AND eq.node_type = 'Equipment'
JOIN nodes p ON p.data->>'equipment_id' = eq.id AND p.node_type = 'Point'
CROSS JOIN LATERAL (
    SELECT
        ts.point_id,
        ts.value AS last_value,
        ts.time AS last_time
    FROM ts.timeseries ts
    WHERE ts.point_id = p.id
    ORDER BY ts.time DESC
    LIMIT 1
) latest
WHERE f.node_type = 'Floor' AND f.data->>'building_id' = $1
ORDER BY space_id, latest.point_id;
