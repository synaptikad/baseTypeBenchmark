-- Q7: Drift Top-20 (P2 JSONB)
-- Paramètres: $1 = BUILDING_ID, $2 = DATE_START, $3 = DATE_END

SELECT
    p.id AS point_id,
    p.name AS point_name,
    VAR_SAMP(ts.value) AS variance,
    AVG(ts.value) AS avg_value,
    COUNT(*) AS sample_count
FROM nodes p
JOIN timeseries ts ON ts.point_id = p.id
WHERE p.node_type = 'Point'
  AND p.data->>'building_id' = $1
  AND ts.time >= $2::timestamptz
  AND ts.time <= $3::timestamptz
GROUP BY p.id, p.name
ORDER BY variance DESC NULLS LAST
LIMIT 20;
