-- Q11: Impact infrastructure IT sur le bâtiment (IT Infrastructure Impact)
-- COMPLEXITÉ MAXIMALE: Cross-domain IT × Energy × Spatial × Equipment × Timeseries
-- Domaines croisés: IT/Datacenter, Energy, Spatial, Equipment, Timeseries
-- Use case: Analyser la corrélation entre charge IT (CPU/RAM) et consommation
-- énergétique du datacenter, avec impact sur le refroidissement des espaces adjacents

WITH
-- 1. Topologie du datacenter
datacenter_topology AS (
    SELECT
        dc.id AS datacenter_id,
        dc.name AS datacenter_name,
        dc.properties->>'tier' AS tier,
        dc.properties->>'pue_target' AS pue_target,
        r.id AS rack_id,
        r.name AS rack_name,
        (r.properties->>'power_capacity_kw')::float AS rack_power_capacity_kw,
        s.id AS space_id,
        s.name AS space_name
    FROM nodes dc
    JOIN edges cont ON cont.src_id = dc.id AND cont.rel_type = 'CONTAINS'
    JOIN nodes r ON r.id = cont.dst_id AND r.type = 'Rack'
    JOIN edges loc ON loc.src_id = dc.id AND loc.rel_type = 'LOCATED_IN'
    JOIN nodes s ON s.id = loc.dst_id AND s.type = 'Space'
    WHERE dc.type = 'Datacenter'
),

-- 2. Serveurs et leurs métriques
server_metrics AS (
    SELECT
        dt.datacenter_id,
        dt.rack_id,
        dt.space_id,
        srv.id AS server_id,
        srv.name AS server_name,
        (srv.properties->>'cpu_cores')::int AS cpu_cores,
        (srv.properties->>'ram_gb')::int AS ram_gb,
        pt.id AS point_id,
        pt.properties->>'quantity' AS metric_type
    FROM datacenter_topology dt
    JOIN edges hosts ON hosts.src_id = dt.rack_id AND hosts.rel_type = 'HOSTS'
    JOIN nodes srv ON srv.id = hosts.dst_id AND srv.type = 'Server'
    JOIN edges hp ON hp.src_id = srv.id AND hp.rel_type = 'HAS_POINT'
    JOIN nodes pt ON pt.id = hp.dst_id AND pt.type = 'Point'
    WHERE pt.properties->>'quantity' IN ('cpu_usage', 'memory_usage')
),

-- 3. Timeseries CPU/Memory (dernière semaine, agrégé par heure)
it_load_hourly AS (
    SELECT
        sm.datacenter_id,
        sm.space_id,
        date_trunc('hour', ts.time) AS hour_bucket,
        AVG(CASE WHEN sm.metric_type = 'cpu_usage' THEN ts.value END) AS avg_cpu_usage,
        AVG(CASE WHEN sm.metric_type = 'memory_usage' THEN ts.value END) AS avg_memory_usage,
        COUNT(DISTINCT sm.server_id) AS active_servers
    FROM server_metrics sm
    JOIN timeseries ts ON ts.point_id = sm.point_id
    WHERE ts.time >= NOW() - INTERVAL '7 days'
    GROUP BY sm.datacenter_id, sm.space_id, date_trunc('hour', ts.time)
),

-- 4. Compteurs alimentant le datacenter (via l'espace)
datacenter_meters AS (
    SELECT DISTINCT
        dt.datacenter_id,
        dt.space_id,
        m.id AS meter_id,
        pt.id AS power_point_id
    FROM datacenter_topology dt
    JOIN edges loc ON loc.dst_id = dt.space_id AND loc.rel_type = 'LOCATED_IN'
    JOIN nodes eq ON eq.id = loc.src_id AND eq.type = 'Equipment'
    JOIN edges feeds ON feeds.dst_id = eq.id AND feeds.rel_type = 'FEEDS'
    JOIN nodes m ON m.id = feeds.src_id AND m.type = 'Meter'
    JOIN edges hp ON hp.src_id = m.id AND hp.rel_type = 'HAS_POINT'
    JOIN nodes pt ON pt.id = hp.dst_id
    WHERE pt.properties->>'quantity' = 'power'
),

-- 5. Consommation énergétique horaire du datacenter
energy_hourly AS (
    SELECT
        dm.datacenter_id,
        dm.space_id,
        date_trunc('hour', ts.time) AS hour_bucket,
        SUM(ts.value) AS total_power_kw
    FROM datacenter_meters dm
    JOIN timeseries ts ON ts.point_id = dm.power_point_id
    WHERE ts.time >= NOW() - INTERVAL '7 days'
    GROUP BY dm.datacenter_id, dm.space_id, date_trunc('hour', ts.time)
),

-- 6. Équipements HVAC refroidissant l'espace datacenter
cooling_equipment AS (
    SELECT
        dt.datacenter_id,
        dt.space_id,
        eq.id AS cooling_equip_id,
        eq.name AS cooling_equip_name,
        pt.id AS temp_point_id
    FROM datacenter_topology dt
    JOIN edges serves ON serves.dst_id = dt.space_id AND serves.rel_type = 'SERVES'
    JOIN nodes eq ON eq.id = serves.src_id AND eq.type = 'Equipment'
    JOIN edges hp ON hp.src_id = eq.id AND hp.rel_type = 'HAS_POINT'
    JOIN nodes pt ON pt.id = hp.dst_id
    WHERE eq.properties->>'equipment_type' IN ('AHU', 'Chiller', 'Fan')
    AND pt.properties->>'quantity' = 'temperature'
),

-- 7. Température horaire de l'espace datacenter
temp_hourly AS (
    SELECT
        ce.datacenter_id,
        ce.space_id,
        date_trunc('hour', ts.time) AS hour_bucket,
        AVG(ts.value) AS avg_temperature
    FROM cooling_equipment ce
    JOIN timeseries ts ON ts.point_id = ce.temp_point_id
    WHERE ts.time >= NOW() - INTERVAL '7 days'
    GROUP BY ce.datacenter_id, ce.space_id, date_trunc('hour', ts.time)
)

-- Résultat: corrélation IT load vs Energy vs Temperature
SELECT
    dt.datacenter_name,
    dt.tier,
    il.hour_bucket,
    ROUND(il.avg_cpu_usage::numeric, 2) AS avg_cpu_pct,
    ROUND(il.avg_memory_usage::numeric, 2) AS avg_memory_pct,
    il.active_servers,
    COALESCE(eh.total_power_kw, 0)::int AS power_kw,
    ROUND(COALESCE(th.avg_temperature, 0)::numeric, 1) AS space_temp_c,
    -- Calcul du PUE réel (simplifié)
    CASE
        WHEN il.avg_cpu_usage > 0 THEN
            ROUND((eh.total_power_kw / NULLIF(il.active_servers * 0.5, 0))::numeric, 2)
        ELSE NULL
    END AS estimated_pue
FROM datacenter_topology dt
JOIN it_load_hourly il ON il.datacenter_id = dt.datacenter_id
LEFT JOIN energy_hourly eh ON eh.datacenter_id = dt.datacenter_id
    AND eh.hour_bucket = il.hour_bucket
LEFT JOIN temp_hourly th ON th.datacenter_id = dt.datacenter_id
    AND th.hour_bucket = il.hour_bucket
ORDER BY dt.datacenter_name, il.hour_bucket
LIMIT 168;  -- 1 semaine d'heures
