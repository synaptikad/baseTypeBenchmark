-- Q8: Énergie consommée par locataire (Tenant Energy Consumption)
-- Complexité: Cross-domain Organization × Spatial × Equipment × Energy × Timeseries
-- Domaines: Tenant, Spatial, Equipment, Meter, Timeseries
-- Use case: Calculer la consommation énergétique de chaque locataire pour facturation

WITH
-- 1. Espaces occupés par chaque tenant
tenant_spaces AS (
    SELECT
        t.id AS tenant_id,
        t.name AS tenant_name,
        s.id AS space_id,
        s.name AS space_name,
        COALESCE((s.properties->>'area_sqm')::int, 0) AS area_sqm
    FROM nodes t
    JOIN edges occ ON occ.src_id = t.id AND occ.rel_type = 'OCCUPIES'
    JOIN nodes s ON s.id = occ.dst_id AND s.type = 'Space'
    WHERE t.type = 'Tenant'
),

-- 2. Équipements dans ces espaces
space_equipment AS (
    SELECT DISTINCT
        ts.tenant_id,
        ts.tenant_name,
        ts.space_id,
        eq.id AS equip_id
    FROM tenant_spaces ts
    JOIN edges loc ON loc.dst_id = ts.space_id AND loc.rel_type = 'LOCATED_IN'
    JOIN nodes eq ON eq.id = loc.src_id AND eq.type = 'Equipment'
),

-- 3. Compteurs alimentant ces équipements
equipment_meters AS (
    SELECT DISTINCT
        se.tenant_id,
        se.tenant_name,
        m.id AS meter_id
    FROM space_equipment se
    JOIN edges feeds ON feeds.dst_id = se.equip_id AND feeds.rel_type = 'FEEDS'
    JOIN nodes m ON m.id = feeds.src_id AND m.type = 'Meter'
),

-- 4. Points de puissance sur les compteurs
meter_power_points AS (
    SELECT DISTINCT
        em.tenant_id,
        em.tenant_name,
        pt.id AS point_id
    FROM equipment_meters em
    JOIN edges hp ON hp.src_id = em.meter_id AND hp.rel_type = 'HAS_POINT'
    JOIN nodes pt ON pt.id = hp.dst_id AND pt.type = 'Point'
    WHERE pt.properties->>'quantity' = 'power'
),

-- 5. Agrégation timeseries sur 30 jours
energy_30d AS (
    SELECT
        mpp.tenant_id,
        mpp.tenant_name,
        SUM(ts.value) * 0.25 AS total_kwh  -- 15min intervals → kWh
    FROM meter_power_points mpp
    JOIN timeseries ts ON ts.point_id = mpp.point_id
    WHERE ts.time >= NOW() - INTERVAL '30 days'
    GROUP BY mpp.tenant_id, mpp.tenant_name
)

-- Résultat final
SELECT
    ts_summary.tenant_name,
    ts_summary.spaces_count,
    ts_summary.total_area_sqm,
    COALESCE(e.total_kwh, 0)::int AS energy_kwh_30d,
    ROUND(COALESCE(e.total_kwh / NULLIF(ts_summary.total_area_sqm, 0), 0)::numeric, 2) AS kwh_per_sqm,
    -- Estimation coût (0.15€/kWh)
    ROUND((COALESCE(e.total_kwh, 0) * 0.15)::numeric, 2) AS estimated_cost_eur
FROM (
    SELECT
        tenant_id,
        tenant_name,
        COUNT(DISTINCT space_id) AS spaces_count,
        SUM(area_sqm) AS total_area_sqm
    FROM tenant_spaces
    GROUP BY tenant_id, tenant_name
) ts_summary
LEFT JOIN energy_30d e ON e.tenant_id = ts_summary.tenant_id
ORDER BY energy_kwh_30d DESC
LIMIT 50;
