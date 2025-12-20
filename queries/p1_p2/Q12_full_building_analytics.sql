-- Q12: Full Building Analytics Dashboard
-- Benchmark: Complex multi-dimensional aggregation (dashboard pattern)
-- Parameters: $BUILDING_ID - building to analyze, $DATE_START/$DATE_END - time range
-- Pattern: Building-level KPIs

WITH building_stats AS (
    SELECT
        n.building_id,
        n.type,
        COUNT(*) as count
    FROM nodes n
    WHERE n.building_id = '$BUILDING_ID'
    GROUP BY n.building_id, n.type
),
building_pivot AS (
    SELECT
        building_id,
        SUM(CASE WHEN type = 'Floor' THEN count ELSE 0 END) as floor_count,
        SUM(CASE WHEN type = 'Space' THEN count ELSE 0 END) as space_count,
        SUM(CASE WHEN type = 'Equipment' THEN count ELSE 0 END) as equipment_count,
        SUM(CASE WHEN type = 'Point' THEN count ELSE 0 END) as point_count,
        SUM(CASE WHEN type = 'Tenant' THEN count ELSE 0 END) as tenant_count,
        SUM(count) as total_nodes
    FROM building_stats
    GROUP BY building_id
),
building_ts_stats AS (
    SELECT
        n.building_id,
        COUNT(DISTINCT ts.point_id) as active_points,
        AVG(ts.value) as avg_value,
        COUNT(*) as sample_count
    FROM timeseries ts
    JOIN nodes n ON n.id = ts.point_id
    WHERE n.building_id = '$BUILDING_ID'
      AND ts.time >= '$DATE_START'::timestamptz
      AND ts.time < '$DATE_END'::timestamptz
    GROUP BY n.building_id
)
SELECT
    bp.building_id,
    bp.floor_count,
    bp.space_count,
    bp.equipment_count,
    bp.point_count,
    bp.tenant_count,
    bp.total_nodes,
    COALESCE(bts.active_points, 0) as active_points,
    COALESCE(bts.sample_count, 0) as samples,
    ROUND(COALESCE(bts.avg_value, 0)::numeric, 2) as avg_value
FROM building_pivot bp
LEFT JOIN building_ts_stats bts ON bts.building_id = bp.building_id;
