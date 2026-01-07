-- Q10: Security Access Analysis
-- Paramètres: $1 = BUILDING_ID

SELECT
    s.id AS space_id,
    s.name AS space_name,
    eq.equipment_type,
    COUNT(*) AS equipment_count
FROM spaces s
JOIN buildings b ON b.id = s.building_id
LEFT JOIN edges e ON (e.target_id = s.id AND e.rel_type IN ('MONITORS', 'LOCATED_IN', 'SECURES'))
LEFT JOIN equipment eq ON eq.id = e.source_id
    AND eq.equipment_type IN ('BadgeReader', 'IPCamera', 'DoorContact', 'PIRDetector')
WHERE b.id = $1
  AND eq.id IS NOT NULL
GROUP BY s.id, s.name, eq.equipment_type
ORDER BY s.id, eq.equipment_type;
