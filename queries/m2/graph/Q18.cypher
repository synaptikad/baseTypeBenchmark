// Q18: Calibration Chain
// Status: DEGRADED pour M1/M2
// Parametres: $meter_id, $reference_date (date string YYYY-MM-DD)
// Note: Memgraph ne supporte pas date() comme Neo4j, comparaison string lexicographique

MATCH path = (meter:Equipment {id: $meter_id})-[:FEEDS*0..10]->(eq:Equipment)
MATCH (eq)-[:HAS_POINT]->(p:Point)
WHERE p.calibration_next_date IS NOT NULL
  AND p.calibration_next_date < $reference_date
RETURN
    p.id AS point_id,
    p.name AS point_name,
    eq.id AS equipment_id,
    p.calibration_last_date AS last_calibration,
    p.calibration_next_date AS next_calibration,
    $reference_date AS reference_date
ORDER BY p.calibration_next_date ASC, point_id;
