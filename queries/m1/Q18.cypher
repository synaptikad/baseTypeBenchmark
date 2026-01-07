// Q18: Calibration Chain
// Status: DEGRADED pour M1/M2
// Paramètres: $meter_id, $reference_date

MATCH path = (meter:Equipment {id: $meter_id})-[:FEEDS*0..10]->(eq:Equipment)
MATCH (eq)-[:HAS_POINT]->(p:Point)
WHERE p.calibration_next_date IS NOT NULL
  AND date(p.calibration_next_date) < date($reference_date)
RETURN
    p.id AS point_id,
    p.name AS point_name,
    eq.id AS equipment_id,
    p.calibration_last_date AS last_calibration,
    p.calibration_next_date AS next_calibration,
    duration.inDays(date(p.calibration_next_date), date($reference_date)).days AS days_overdue
ORDER BY days_overdue DESC, point_id;
