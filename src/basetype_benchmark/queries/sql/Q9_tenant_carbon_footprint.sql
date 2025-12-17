-- Q9: Empreinte carbone par locataire (Tenant Carbon Footprint)
-- COMPLEXITÉ MAXIMALE: Cross-domain query traversant 6 domaines
-- Domaines croisés: Organization, Spatial, Equipment, Energy, Contractual, Timeseries
-- Use case: Calculer l'empreinte carbone de chaque locataire sur 6 mois
-- en suivant: Tenant → Spaces occupés → Equipements → Compteurs → Timeseries énergie → Contrat fournisseur

WITH RECURSIVE
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
    SELECT
        ts.tenant_id,
        ts.tenant_name,
        ts.space_id,
        eq.id AS equip_id,
        eq.properties->>'equipment_type' AS equip_type,
        COALESCE((eq.properties->>'nominal_power_kw')::float, 1.0) AS nominal_power_kw
    FROM tenant_spaces ts
    JOIN edges loc ON loc.dst_id = ts.space_id AND loc.rel_type = 'LOCATED_IN'
    JOIN nodes eq ON eq.id = loc.src_id AND eq.type = 'Equipment'
),

-- 3. Traversée de l'arbre de compteurs (FEEDS) - récursif jusqu'à 8 niveaux
meter_chain AS (
    -- Base: compteurs feuilles alimentant les équipements
    SELECT
        se.tenant_id,
        se.equip_id,
        m.id AS meter_id,
        1 AS meter_depth,
        ARRAY[m.id] AS meter_path
    FROM space_equipment se
    JOIN edges feeds ON feeds.dst_id = se.equip_id AND feeds.rel_type = 'FEEDS'
    JOIN nodes m ON m.id = feeds.src_id AND m.type = 'Meter'

    UNION ALL

    -- Récursion: remonter vers les compteurs parents
    SELECT
        mc.tenant_id,
        mc.equip_id,
        parent.id,
        mc.meter_depth + 1,
        mc.meter_path || parent.id
    FROM meter_chain mc
    JOIN edges feeds ON feeds.dst_id = mc.meter_id AND feeds.rel_type = 'FEEDS'
    JOIN nodes parent ON parent.id = feeds.src_id AND parent.type = 'Meter'
    WHERE mc.meter_depth < 8
    AND NOT (parent.id = ANY(mc.meter_path))
),

-- 4. Points de mesure power sur les compteurs
meter_power_points AS (
    SELECT DISTINCT
        mc.tenant_id,
        mc.meter_id,
        p.id AS point_id
    FROM meter_chain mc
    JOIN edges hp ON hp.src_id = mc.meter_id AND hp.rel_type = 'HAS_POINT'
    JOIN nodes p ON p.id = hp.dst_id AND p.type = 'Point'
    WHERE p.properties->>'quantity' = 'power'
),

-- 5. Agrégation timeseries sur 6 mois
energy_consumption AS (
    SELECT
        mpp.tenant_id,
        SUM(ts.value) * 0.25 AS total_kwh  -- 15min intervals → kWh
    FROM meter_power_points mpp
    JOIN timeseries ts ON ts.point_id = mpp.point_id
    WHERE ts.time >= NOW() - INTERVAL '6 months'
    GROUP BY mpp.tenant_id
),

-- 6. Facteur carbone du fournisseur via les contrats
tenant_carbon_factor AS (
    SELECT
        t.id AS tenant_id,
        COALESCE(AVG(
            CASE
                WHEN prov.name ILIKE '%edf%' THEN 0.05  -- Nucléaire FR
                WHEN prov.name ILIKE '%engie%' THEN 0.35  -- Mix gaz
                ELSE 0.45  -- Default grid mix
            END
        ), 0.40) AS carbon_factor_kg_kwh
    FROM nodes t
    LEFT JOIN edges cov ON cov.src_id = t.id  -- Simplification
    LEFT JOIN nodes c ON c.id = cov.dst_id AND c.type = 'Contract'
    LEFT JOIN edges prov_rel ON prov_rel.src_id = c.id AND prov_rel.rel_type = 'PROVIDED_BY'
    LEFT JOIN nodes prov ON prov.id = prov_rel.dst_id AND prov.type = 'Provider'
    WHERE t.type = 'Tenant'
    GROUP BY t.id
)

-- Résultat final: empreinte carbone par tenant
SELECT
    t.name AS tenant_name,
    ts_agg.total_spaces,
    ts_agg.total_area_sqm,
    COALESCE(ec.total_kwh, 0)::int AS energy_kwh_6m,
    ROUND(COALESCE(ec.total_kwh * tcf.carbon_factor_kg_kwh, 0)::numeric, 2) AS carbon_kg_6m,
    ROUND(COALESCE(ec.total_kwh * tcf.carbon_factor_kg_kwh / NULLIF(ts_agg.total_area_sqm, 0), 0)::numeric, 4) AS carbon_kg_per_sqm
FROM nodes t
JOIN (
    SELECT tenant_id, COUNT(DISTINCT space_id) AS total_spaces, SUM(area_sqm) AS total_area_sqm
    FROM tenant_spaces
    GROUP BY tenant_id
) ts_agg ON ts_agg.tenant_id = t.id
LEFT JOIN energy_consumption ec ON ec.tenant_id = t.id
LEFT JOIN tenant_carbon_factor tcf ON tcf.tenant_id = t.id
WHERE t.type = 'Tenant'
ORDER BY carbon_kg_6m DESC
LIMIT 20;
