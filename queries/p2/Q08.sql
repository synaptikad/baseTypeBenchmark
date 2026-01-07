-- Q8: Tenant Energy (P2 JSONB)
-- Paramètres: $1 = TENANT_ID, $2 = DATE_START, $3 = DATE_END

SELECT
    $1 AS tenant_id,
    SUM(ts.value) AS total_energy_kwh,
    COUNT(DISTINCT eq.id) AS meter_count,
    COUNT(DISTINCT p.id) AS point_count
FROM nodes t
JOIN edges e_mt ON e_mt.target_id = t.id AND e_mt.rel_type = 'METERS_TENANT'
JOIN nodes eq ON eq.id = e_mt.source_id AND eq.node_type = 'Equipment'
JOIN edges e_hp ON e_hp.source_id = eq.id AND e_hp.rel_type = 'HAS_POINT'
JOIN nodes p ON p.id = e_hp.target_id AND p.node_type = 'Point' AND p.data->>'quantity' = 'energy'
JOIN timeseries ts ON ts.point_id = p.id
WHERE t.id = $1 AND t.node_type = 'Tenant'
  AND ts.time >= $2::timestamptz
  AND ts.time <= $3::timestamptz;
