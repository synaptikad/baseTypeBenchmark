-- Q34: Materialized Energy Summary (P2 JSONB)
-- Status: NATIVE pour P2 (inline computation, same as materialized view would provide)
-- Semantic: Compute daily energy aggregates per building
-- Parametres: $1 = BUILDING_ID, $2 = DATE_START, $3 = DATE_END

WITH building_energy AS (
    SELECT
        p.data->>'building_id' AS building_id,
        time_bucket('1 day', ts.time)::date AS day,
        SUM(ts.value) AS total_energy_kwh,
        MAX(ts.value) AS peak_power_kw,
        COUNT(DISTINCT p.id) AS meter_count
    FROM ts.timeseries ts
    JOIN nodes p ON p.id = ts.point_id
        AND p.node_type = 'Point'
        AND p.data->>'quantity' = 'energy'
    WHERE p.data->>'building_id' = $1
      AND ts.time >= $2
      AND ts.time <= $3
    GROUP BY p.data->>'building_id', time_bucket('1 day', ts.time)::date
)
SELECT
    building_id,
    day,
    total_energy_kwh,
    peak_power_kw,
    meter_count
FROM building_energy
ORDER BY day;
