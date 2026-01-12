-- Q34: Materialized Energy Summary
-- Status: NATIVE pour P1 (PostgreSQL Materialized Views)
-- Semantic: Read from pre-computed materialized view or compute inline
-- Parametres: $1 = BUILDING_ID, $2 = DATE_START, $3 = DATE_END
-- Note: Uses inline computation since materialized view may not exist

WITH building_energy AS (
    SELECT
        f.building_id,
        time_bucket('1 day', ts.time)::date AS day,
        SUM(ts.value) AS total_energy_kwh,
        MAX(ts.value) AS peak_power_kw,
        COUNT(DISTINCT p.id) AS meter_count
    FROM ts.timeseries ts
    JOIN points p ON p.id = ts.point_id AND p.quantity = 'energy'
    JOIN equipment eq ON eq.id = p.equipment_id
    JOIN edges e ON e.source_id = eq.id AND e.rel_type = 'SERVES'
    JOIN spaces s ON s.id = e.target_id
    JOIN floors f ON f.id = s.floor_id
    WHERE f.building_id = $1
      AND ts.time >= $2
      AND ts.time <= $3
    GROUP BY f.building_id, time_bucket('1 day', ts.time)::date
)
SELECT
    building_id,
    day,
    total_energy_kwh,
    peak_power_kw,
    meter_count
FROM building_energy
ORDER BY day;
