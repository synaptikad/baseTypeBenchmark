-- Q12: Full Building Analytics (P2 JSONB)
-- Paramètres: $1 = BUILDING_ID, $2 = DATE_START, $3 = DATE_END

SELECT
    $1 AS building_id,
    SUM(CASE WHEN p.data->>'quantity' = 'energy' THEN ts.value ELSE 0 END) AS total_energy_kwh,
    AVG(CASE WHEN p.data->>'quantity' = 'temperature' THEN ts.value END) AS avg_temperature_c,
    SUM(CASE WHEN p.data->>'quantity' = 'occupancy' THEN ts.value ELSE 0 END)::integer AS total_occupancy
FROM nodes p
JOIN timeseries ts ON ts.point_id = p.id
WHERE p.node_type = 'Point'
  AND p.data->>'building_id' = $1
  AND ts.time >= $2::timestamptz
  AND ts.time <= $3::timestamptz
  AND p.data->>'quantity' IN ('energy', 'temperature', 'occupancy');
