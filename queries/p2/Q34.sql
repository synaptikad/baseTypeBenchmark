-- Q34: Materialized Energy Summary (P2 JSONB)
-- Status: NATIVE pour P2 (PostgreSQL Materialized Views)
-- Semantic: Read from pre-computed materialized view
-- Parametres: $1 = BUILDING_ID, $2 = DATE_START, $3 = DATE_END
-- Note: Assumes building_daily_energy_p2 materialized view exists

-- First ensure the materialized view exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT FROM pg_matviews WHERE matviewname = 'building_daily_energy_p2'
    ) THEN
        EXECUTE '
            CREATE MATERIALIZED VIEW IF NOT EXISTS building_daily_energy_p2 AS
            SELECT
                f.data->>''building_id'' AS building_id,
                time_bucket(''1 day'', ts.time)::date AS day,
                SUM(ts.value) AS total_energy_kwh,
                MAX(ts.value) AS peak_power_kw,
                COUNT(DISTINCT p.id) AS meter_count
            FROM ts.timeseries ts
            JOIN nodes p ON p.id = ts.point_id
                AND p.node_type = ''Point''
                AND p.data->>''quantity'' = ''energy''
            JOIN nodes eq ON eq.id = p.data->>''equipment_id'' AND eq.node_type = ''Equipment''
            JOIN edges e ON e.source_id = eq.id AND e.rel_type = ''SERVES''
            JOIN nodes s ON s.id = e.target_id AND s.node_type = ''Space''
            JOIN nodes f ON f.id = s.data->>''floor_id'' AND f.node_type = ''Floor''
            GROUP BY f.data->>''building_id'', time_bucket(''1 day'', ts.time)::date
        ';
    END IF;
END $$;

SELECT
    building_id,
    day,
    total_energy_kwh,
    peak_power_kw,
    meter_count
FROM building_daily_energy_p2
WHERE building_id = $1
  AND day >= $2
  AND day <= $3
ORDER BY day;
