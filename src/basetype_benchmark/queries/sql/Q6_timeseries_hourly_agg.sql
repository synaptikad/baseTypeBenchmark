-- Q6: Agrégation horaire des timeseries (Hourly Timeseries Aggregation)
-- Complexité: Agrégation temporelle avec time_bucket (TimescaleDB)
-- Domaines: Timeseries, Point, Equipment
-- Use case: Agrégation horaire des mesures de puissance pour reporting énergétique

SELECT
    time_bucket('1 hour', ts.time) AS hour_bucket,
    pt.properties->>'quantity' AS quantity,
    eq.properties->>'equipment_type' AS equipment_type,
    COUNT(*) AS sample_count,
    ROUND(AVG(ts.value)::numeric, 2) AS avg_value,
    ROUND(MIN(ts.value)::numeric, 2) AS min_value,
    ROUND(MAX(ts.value)::numeric, 2) AS max_value,
    ROUND(STDDEV(ts.value)::numeric, 4) AS stddev_value,
    -- Énergie cumulée (pour power → kWh)
    CASE
        WHEN pt.properties->>'quantity' = 'power'
        THEN ROUND((SUM(ts.value) * 0.25)::numeric, 2)  -- 15min intervals → kWh
        ELSE NULL
    END AS energy_kwh
FROM timeseries ts
JOIN nodes pt ON pt.id = ts.point_id AND pt.type = 'Point'
LEFT JOIN edges hp ON hp.dst_id = pt.id AND hp.rel_type = 'HAS_POINT'
LEFT JOIN nodes eq ON eq.id = hp.src_id AND eq.type = 'Equipment'
WHERE ts.time >= NOW() - INTERVAL '7 days'
AND pt.properties->>'quantity' IN ('power', 'temperature', 'humidity', 'co2')
GROUP BY
    time_bucket('1 hour', ts.time),
    pt.properties->>'quantity',
    eq.properties->>'equipment_type'
ORDER BY hour_bucket DESC, quantity, equipment_type
LIMIT 500;
