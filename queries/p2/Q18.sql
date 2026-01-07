-- Q18: Calibration Chain
-- Status: NATIVE pour P2
-- Paramètres: $1 = METER_ID, $2 = REFERENCE_DATE

WITH RECURSIVE energy_chain AS (
    SELECT n.id, 1 AS depth
    FROM nodes n
    WHERE n.id = $1 AND n.node_type = 'Equipment'

    UNION ALL

    SELECT n.id, ec.depth + 1
    FROM energy_chain ec
    JOIN edges e ON e.source_id = ec.id AND e.rel_type = 'FEEDS'
    JOIN nodes n ON n.id = e.target_id AND n.node_type = 'Equipment'
    WHERE ec.depth < 10
)
SELECT
    p.id AS point_id,
    p.name AS point_name,
    ec.id AS equipment_id,
    (p.data->'calibration'->>'last_date')::date AS last_calibration,
    (p.data->'calibration'->>'next_date')::date AS next_calibration,
    ($2::date - (p.data->'calibration'->>'next_date')::date) AS days_overdue
FROM energy_chain ec
JOIN edges e_hp ON e_hp.source_id = ec.id AND e_hp.rel_type = 'HAS_POINT'
JOIN nodes p ON p.id = e_hp.target_id AND p.node_type = 'Point'
WHERE p.data->'calibration'->>'next_date' IS NOT NULL
  AND (p.data->'calibration'->>'next_date')::date < $2::date
ORDER BY days_overdue DESC, p.id;
