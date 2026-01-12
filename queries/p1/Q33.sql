-- Q33: Latest Value per Space
-- Status: NATIVE pour P1 (LATERAL JOIN optimise)
-- Semantic: Get latest value for each point per space
-- Parametres: $1 = BUILDING_ID

SELECT
    s.id AS space_id,
    s.name AS space_name,
    latest.point_id,
    p.quantity,
    latest.last_value,
    latest.last_time
FROM floors f
JOIN spaces s ON s.floor_id = f.id
JOIN edges e ON e.target_id = s.id AND e.rel_type = 'SERVES'
JOIN equipment eq ON eq.id = e.source_id
JOIN points p ON p.equipment_id = eq.id
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
WHERE f.building_id = $1
ORDER BY space_id, latest.point_id;
