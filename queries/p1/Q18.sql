-- Q18: Calibration Chain
-- Status: DEGRADED pour P1
-- Raison: P1 peut traverser la chaîne FEEDS mais n'a pas de données calibration.
-- Cette implémentation retourne les points sans info calibration.
-- Paramètres: $1 = METER_ID

WITH RECURSIVE energy_chain AS (
    SELECT id, 1 AS depth FROM equipment WHERE id = $1
    UNION ALL
    SELECT eq.id, ec.depth + 1
    FROM energy_chain ec
    JOIN edges e ON e.source_id = ec.id AND e.rel_type = 'FEEDS'
    JOIN equipment eq ON eq.id = e.target_id
    WHERE ec.depth < 10
)
SELECT
    p.id AS point_id,
    p.name AS point_name,
    ec.id AS equipment_id,
    NULL::date AS last_calibration,
    NULL::date AS next_calibration,
    NULL::integer AS days_overdue
FROM energy_chain ec
JOIN edges e_hp ON e_hp.source_id = ec.id AND e_hp.rel_type = 'HAS_POINT'
JOIN points p ON p.id = e_hp.target_id
ORDER BY ec.depth, p.id;

-- Note: Sans données calibration, impossible de calculer days_overdue
