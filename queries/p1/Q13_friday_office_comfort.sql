-- Q13 (P1): Friday Office Comfort - Stress-test for dechunking
-- Benchmark: DOW filtering + occupancy correlation (optimal on TimescaleDB)
-- Parameters: $SPACE_TYPE - space type pattern (e.g. 'office_%'), $DATE_START/$DATE_END

WITH office_setpoints AS (
    -- Find temperature setpoint points in spaces of given type
    SELECT DISTINCT
        p.id AS point_id,
        sp.id AS space_id
    FROM nodes p
    JOIN edges e1 ON e1.dst_id = p.id AND e1.rel_type = 'HAS_POINT'
    JOIN nodes eq ON eq.id = e1.src_id AND eq.type = 'Equipment'
    JOIN edges e2 ON e2.src_id = eq.id AND e2.rel_type = 'LOCATED_IN'
    JOIN nodes sp ON sp.id = e2.dst_id AND sp.type = 'Space'
    WHERE p.type = 'Point'
      AND p.name ILIKE '%setpoint%'
      AND p.name ILIKE '%temp%'
      AND sp.space_type LIKE '$SPACE_TYPE'
),
office_occupancy AS (
    -- Find PeopleCounter points in offices
    SELECT DISTINCT
        p.id AS point_id,
        sp.id AS space_id
    FROM nodes p
    JOIN edges e1 ON e1.dst_id = p.id AND e1.rel_type = 'HAS_POINT'
    JOIN nodes eq ON eq.id = e1.src_id AND eq.type = 'Equipment'
    JOIN edges e2 ON e2.src_id = eq.id AND e2.rel_type = 'LOCATED_IN'
    JOIN nodes sp ON sp.id = e2.dst_id AND sp.type = 'Space'
    WHERE p.type = 'Point'
      AND eq.equipment_type = 'PeopleCounter'
      AND sp.space_type LIKE '$SPACE_TYPE'
),
friday_setpoints AS (
    -- Get setpoint values on Fridays only in date range
    SELECT
        os.space_id,
        ts.time,
        ts.value AS setpoint
    FROM timeseries ts
    JOIN office_setpoints os ON ts.point_id = os.point_id
    WHERE ts.time >= '$DATE_START'::timestamptz
      AND ts.time < '$DATE_END'::timestamptz
      AND EXTRACT(DOW FROM ts.time) = 5  -- Friday (0=Sunday, 5=Friday)
),
friday_with_occupancy AS (
    -- Join with occupancy data at same timestamp
    SELECT
        fs.space_id,
        fs.time,
        fs.setpoint,
        occ_ts.value AS occupancy
    FROM friday_setpoints fs
    LEFT JOIN office_occupancy oo ON oo.space_id = fs.space_id
    LEFT JOIN timeseries occ_ts ON occ_ts.point_id = oo.point_id
        AND occ_ts.time = fs.time
)
SELECT
    CASE
        WHEN occupancy IS NULL THEN 'unknown'
        WHEN occupancy < 5 THEN 'low (0-4)'
        WHEN occupancy < 15 THEN 'medium (5-14)'
        ELSE 'high (15+)'
    END AS occupancy_level,
    AVG(setpoint) AS avg_setpoint,
    MIN(setpoint) AS min_setpoint,
    MAX(setpoint) AS max_setpoint,
    COUNT(*) AS sample_count
FROM friday_with_occupancy
GROUP BY 1
ORDER BY 1;
