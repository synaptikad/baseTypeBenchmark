-- Q10: Security Access Analysis (M2/O2 TimescaleDB part)
-- Benchmark: Access event aggregation for security zone
-- Parameters: $POINT_IDS (array from graph), $DATE_START, $DATE_END
-- Note: Graph returns access control point IDs for zone

SELECT
    point_id,
    COUNT(*) as event_count,
    MIN(time) as first_event,
    MAX(time) as last_event
FROM timeseries
WHERE point_id = ANY($POINT_IDS)
  AND time >= '$DATE_START'::timestamptz
  AND time < '$DATE_END'::timestamptz
GROUP BY point_id
ORDER BY event_count DESC;
