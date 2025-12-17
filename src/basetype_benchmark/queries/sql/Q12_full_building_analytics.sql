-- Q12: Analytique bâtiment complète (Full Building Analytics Dashboard)
-- COMPLEXITÉ ULTIME: Croise TOUS les 9 domaines en une seule requête
-- Domaines: Spatial, Equipment, Energy, IT, AV, Parking, Security, Organization, Contractual
-- Use case: Dashboard exécutif avec KPIs cross-domain pour le facility manager
-- Cette requête représente le cas le plus complexe possible dans un smart building

WITH
-- ============================================================================
-- DOMAINE SPATIAL: Métriques d'occupation et surface
-- ============================================================================
spatial_metrics AS (
    SELECT
        b.id AS building_id,
        b.name AS building_name,
        COUNT(DISTINCT f.id) AS floors_count,
        COUNT(DISTINCT s.id) AS spaces_count,
        SUM(COALESCE((s.properties->>'area_sqm')::int, 0)) AS total_area_sqm,
        SUM(COALESCE((s.properties->>'capacity')::int, 0)) AS total_capacity
    FROM nodes b
    JOIN edges e1 ON e1.src_id = b.id AND e1.rel_type = 'CONTAINS'
    JOIN nodes f ON f.id = e1.dst_id AND f.type = 'Floor'
    JOIN edges e2 ON e2.src_id = f.id AND e2.rel_type = 'CONTAINS'
    JOIN nodes s ON s.id = e2.dst_id AND s.type = 'Space'
    WHERE b.type = 'Building'
    GROUP BY b.id, b.name
),

-- ============================================================================
-- DOMAINE ÉQUIPEMENT: Inventaire et santé
-- ============================================================================
equipment_metrics AS (
    SELECT
        COUNT(DISTINCT eq.id) AS total_equipments,
        COUNT(DISTINCT CASE WHEN eq.properties->>'equipment_type' = 'AHU' THEN eq.id END) AS ahu_count,
        COUNT(DISTINCT CASE WHEN eq.properties->>'equipment_type' = 'VAV' THEN eq.id END) AS vav_count,
        COUNT(DISTINCT CASE WHEN eq.properties->>'equipment_type' = 'Chiller' THEN eq.id END) AS chiller_count,
        AVG(COALESCE((eq.properties->>'efficiency')::float, 0.85)) AS avg_efficiency
    FROM nodes eq
    WHERE eq.type = 'Equipment'
),

-- ============================================================================
-- DOMAINE ÉNERGIE: Consommation et distribution
-- ============================================================================
energy_metrics AS (
    SELECT
        COUNT(DISTINCT m.id) AS meters_count,
        COUNT(DISTINCT CASE WHEN m.properties->>'meter_type' = 'electricity' THEN m.id END) AS elec_meters,
        COUNT(DISTINCT CASE WHEN m.properties->>'meter_type' = 'water' THEN m.id END) AS water_meters,
        COUNT(DISTINCT CASE WHEN m.properties->>'meter_type' = 'gas' THEN m.id END) AS gas_meters
    FROM nodes m
    WHERE m.type = 'Meter'
),

energy_consumption_24h AS (
    SELECT
        COALESCE(SUM(ts.value) * 0.25, 0) AS total_kwh_24h  -- 15min intervals
    FROM nodes pt
    JOIN edges hp ON hp.dst_id = pt.id AND hp.rel_type = 'HAS_POINT'
    JOIN nodes m ON m.id = hp.src_id AND m.type = 'Meter'
    JOIN timeseries ts ON ts.point_id = pt.id
    WHERE pt.properties->>'quantity' = 'power'
    AND ts.time >= NOW() - INTERVAL '24 hours'
),

-- ============================================================================
-- DOMAINE IT: Infrastructure datacenter
-- ============================================================================
it_metrics AS (
    SELECT
        COUNT(DISTINCT dc.id) AS datacenters_count,
        COUNT(DISTINCT r.id) AS racks_count,
        COUNT(DISTINCT srv.id) AS servers_count,
        COUNT(DISTINCT nd.id) AS network_devices_count,
        SUM(COALESCE((srv.properties->>'cpu_cores')::int, 0)) AS total_cpu_cores,
        SUM(COALESCE((srv.properties->>'ram_gb')::int, 0)) AS total_ram_gb
    FROM nodes dc
    LEFT JOIN edges e1 ON e1.src_id = dc.id AND e1.rel_type = 'CONTAINS'
    LEFT JOIN nodes r ON r.id = e1.dst_id AND r.type = 'Rack'
    LEFT JOIN edges e2 ON e2.src_id = r.id AND e2.rel_type = 'HOSTS'
    LEFT JOIN nodes srv ON srv.id = e2.dst_id AND srv.type = 'Server'
    LEFT JOIN nodes nd ON nd.id = e2.dst_id AND nd.type = 'NetworkDevice'
    WHERE dc.type = 'Datacenter'
),

-- ============================================================================
-- DOMAINE AV: Systèmes audiovisuels
-- ============================================================================
av_metrics AS (
    SELECT
        COUNT(DISTINCT av.id) AS av_systems_count,
        COUNT(DISTINCT d.id) AS displays_count,
        COUNT(DISTINCT p.id) AS projectors_count,
        COUNT(DISTINCT cu.id) AS conference_units_count
    FROM nodes av
    LEFT JOIN edges e ON e.src_id = av.id AND e.rel_type = 'HAS_PART'
    LEFT JOIN nodes d ON d.id = e.dst_id AND d.type = 'Display'
    LEFT JOIN nodes p ON p.id = e.dst_id AND p.type = 'Projector'
    LEFT JOIN nodes cu ON cu.id = e.dst_id AND cu.type = 'ConferenceUnit'
    WHERE av.type = 'AVSystem'
),

-- ============================================================================
-- DOMAINE PARKING: Occupation et recharge
-- ============================================================================
parking_metrics AS (
    SELECT
        COUNT(DISTINCT pz.id) AS parking_zones_count,
        COUNT(DISTINCT ps.id) AS parking_spots_total,
        COUNT(DISTINCT CASE WHEN ps.properties->>'spot_type' = 'ev_charging' THEN ps.id END) AS ev_spots,
        COUNT(DISTINCT cs.id) AS charging_stations_count,
        COUNT(DISTINCT v.id) AS vehicles_present
    FROM nodes pz
    LEFT JOIN edges e1 ON e1.src_id = pz.id AND e1.rel_type = 'CONTAINS'
    LEFT JOIN nodes pl ON pl.id = e1.dst_id AND pl.type = 'ParkingLevel'
    LEFT JOIN edges e2 ON e2.src_id = pl.id AND e2.rel_type = 'CONTAINS'
    LEFT JOIN nodes ps ON ps.id = e2.dst_id AND ps.type = 'ParkingSpot'
    LEFT JOIN edges e3 ON e3.dst_id = ps.id AND e3.rel_type = 'LOCATED_IN'
    LEFT JOIN nodes cs ON cs.id = e3.src_id AND cs.type = 'ChargingStation'
    LEFT JOIN edges e4 ON e4.dst_id = ps.id AND e4.rel_type = 'PARKED_AT'
    LEFT JOIN nodes v ON v.id = e4.src_id AND v.type = 'Vehicle'
    WHERE pz.type = 'ParkingZone'
),

-- ============================================================================
-- DOMAINE SÉCURITÉ: Dispositifs et zones
-- ============================================================================
security_metrics AS (
    SELECT
        COUNT(DISTINCT sz.id) AS security_zones_count,
        COUNT(DISTINCT ap.id) AS access_points_count,
        COUNT(DISTINCT cam.id) AS cameras_count,
        COUNT(DISTINCT alm.id) AS alarms_count,
        COUNT(DISTINCT CASE WHEN sz.properties->>'security_level' = 'restricted' THEN sz.id END) AS restricted_zones
    FROM nodes sz
    LEFT JOIN edges e ON e.src_id = sz.id AND e.rel_type = 'CONTAINS'
    LEFT JOIN nodes ap ON ap.id = e.dst_id AND ap.type = 'AccessPoint'
    LEFT JOIN nodes cam ON cam.id = e.dst_id AND cam.type = 'Camera'
    LEFT JOIN nodes alm ON alm.id = e.dst_id AND alm.type = 'Alarm'
    WHERE sz.type = 'SecurityZone'
),

-- ============================================================================
-- DOMAINE ORGANISATION: Effectifs et structure
-- ============================================================================
organization_metrics AS (
    SELECT
        COUNT(DISTINCT o.id) AS organizations_count,
        COUNT(DISTINCT d.id) AS departments_count,
        COUNT(DISTINCT t.id) AS teams_count,
        COUNT(DISTINCT p.id) AS persons_count,
        COUNT(DISTINCT CASE WHEN p.properties->>'role' = 'manager' THEN p.id END) AS managers_count
    FROM nodes o
    LEFT JOIN edges e1 ON e1.src_id = o.id AND e1.rel_type = 'CONTAINS'
    LEFT JOIN nodes d ON d.id = e1.dst_id AND d.type = 'Department'
    LEFT JOIN edges e2 ON e2.src_id = d.id AND e2.rel_type = 'CONTAINS'
    LEFT JOIN nodes t ON t.id = e2.dst_id AND t.type = 'Team'
    LEFT JOIN edges e3 ON e3.dst_id = t.id AND e3.rel_type = 'BELONGS_TO'
    LEFT JOIN nodes p ON p.id = e3.src_id AND p.type = 'Person'
    WHERE o.type = 'Organization'
),

-- ============================================================================
-- DOMAINE TENANTS: Locataires
-- ============================================================================
tenant_metrics AS (
    SELECT
        COUNT(DISTINCT tn.id) AS tenants_count,
        COUNT(DISTINCT occ.dst_id) AS occupied_spaces_count
    FROM nodes tn
    LEFT JOIN edges occ ON occ.src_id = tn.id AND occ.rel_type = 'OCCUPIES'
    WHERE tn.type = 'Tenant'
),

-- ============================================================================
-- DOMAINE CONTRACTUEL: Contrats et maintenance
-- ============================================================================
contract_metrics AS (
    SELECT
        COUNT(DISTINCT c.id) AS contracts_count,
        COUNT(DISTINCT prov.id) AS providers_count,
        COUNT(DISTINCT l.id) AS active_leases,
        COUNT(DISTINCT wo.id) AS work_orders_total,
        COUNT(DISTINCT CASE WHEN wo.properties->>'status' = 'open' THEN wo.id END) AS work_orders_open,
        SUM(COALESCE((c.properties->>'annual_value')::int, 0)) AS total_contract_value
    FROM nodes c
    LEFT JOIN edges e ON e.src_id = c.id AND e.rel_type = 'PROVIDED_BY'
    LEFT JOIN nodes prov ON prov.id = e.dst_id AND prov.type = 'Provider'
    LEFT JOIN nodes l ON l.type = 'Lease'
    LEFT JOIN nodes wo ON wo.type = 'WorkOrder'
    WHERE c.type = 'Contract'
)

-- ============================================================================
-- RÉSULTAT FINAL: Dashboard KPIs cross-domain
-- ============================================================================
SELECT
    -- Identité bâtiment
    sm.building_name,
    sm.floors_count,
    sm.spaces_count,
    sm.total_area_sqm,
    sm.total_capacity,

    -- Équipements
    em.total_equipments,
    ROUND(em.avg_efficiency::numeric * 100, 1) AS avg_efficiency_pct,

    -- Énergie
    enm.meters_count,
    ROUND(ec.total_kwh_24h::numeric, 0) AS energy_kwh_24h,
    ROUND((ec.total_kwh_24h / NULLIF(sm.total_area_sqm, 0))::numeric, 2) AS kwh_per_sqm_24h,

    -- IT
    it.datacenters_count,
    it.servers_count,
    it.total_cpu_cores,
    it.total_ram_gb,

    -- AV
    av.av_systems_count,
    av.displays_count,

    -- Parking
    pm.parking_spots_total,
    pm.ev_spots,
    pm.vehicles_present,
    ROUND(100.0 * pm.vehicles_present / NULLIF(pm.parking_spots_total, 0), 1) AS parking_occupancy_pct,

    -- Sécurité
    sec.security_zones_count,
    sec.access_points_count,
    sec.cameras_count,
    sec.restricted_zones,

    -- Organisation
    org.departments_count,
    org.teams_count,
    org.persons_count,

    -- Tenants
    tn.tenants_count,
    tn.occupied_spaces_count,
    ROUND(100.0 * tn.occupied_spaces_count / NULLIF(sm.spaces_count, 0), 1) AS space_occupancy_pct,

    -- Contracts
    cm.contracts_count,
    cm.work_orders_open,
    cm.total_contract_value

FROM spatial_metrics sm
CROSS JOIN equipment_metrics em
CROSS JOIN energy_metrics enm
CROSS JOIN energy_consumption_24h ec
CROSS JOIN it_metrics it
CROSS JOIN av_metrics av
CROSS JOIN parking_metrics pm
CROSS JOIN security_metrics sec
CROSS JOIN organization_metrics org
CROSS JOIN tenant_metrics tn
CROSS JOIN contract_metrics cm;
