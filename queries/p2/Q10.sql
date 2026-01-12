-- Q10: Security Access Analysis (P2 JSONB)
-- Paramètres: $1 = BUILDING_ID

SELECT
    s.id AS space_id,
    s.name AS space_name,
    eq.data->>'equipment_type' AS equipment_type,
    COUNT(*) AS equipment_count
FROM nodes s
LEFT JOIN edges e ON e.target_id = s.id AND e.rel_type = 'LOCATED_IN'
LEFT JOIN nodes eq ON eq.id = e.source_id AND eq.node_type = 'Equipment'
    AND eq.data->>'equipment_type' IN ('BadgeReader', 'IPCamera', 'DoorContact', 'PIRDetector')
WHERE s.node_type = 'Space'
  AND s.data->>'building_id' = $1
  AND eq.id IS NOT NULL
GROUP BY s.id, s.name, eq.data->>'equipment_type'
ORDER BY s.id, eq.data->>'equipment_type';
