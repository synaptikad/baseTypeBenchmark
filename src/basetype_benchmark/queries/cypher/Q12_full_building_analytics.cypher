// Q12: Analytique bâtiment complète (Full Building Analytics Dashboard)
// COMPLEXITÉ ULTIME: Croise TOUS les 9 domaines en une seule requête
// Domaines: Spatial, Equipment, Energy, IT, AV, Parking, Security, Organization, Contractual
// Use case: Dashboard exécutif avec KPIs cross-domain

// Note: Cette requête pousse Cypher à ses limites car elle doit agréger
// des données de 9 domaines différents sans support natif de sous-requêtes complexes

// ============================================================================
// DOMAINE SPATIAL
// ============================================================================
MATCH (building:Node {type: 'Building'})
OPTIONAL MATCH (building)-[:CONTAINS]->(floor:Node {type: 'Floor'})
OPTIONAL MATCH (floor)-[:CONTAINS]->(space:Node {type: 'Space'})

WITH building,
     COLLECT(DISTINCT floor.id) AS floors,
     COLLECT(DISTINCT space) AS spaces

// Calculer métriques spatiales
WITH building,
     SIZE(floors) AS floors_count,
     SIZE(spaces) AS spaces_count,
     REDUCE(area = 0, s IN spaces | area + COALESCE(toInteger(s.properties.area_sqm), 0)) AS total_area_sqm,
     REDUCE(cap = 0, s IN spaces | cap + COALESCE(toInteger(s.properties.capacity), 0)) AS total_capacity

// ============================================================================
// DOMAINE ÉQUIPEMENT
// ============================================================================
OPTIONAL MATCH (equip:Node {type: 'Equipment'})
WITH building, floors_count, spaces_count, total_area_sqm, total_capacity,
     COUNT(DISTINCT equip) AS equipments_count

// ============================================================================
// DOMAINE ÉNERGIE
// ============================================================================
OPTIONAL MATCH (meter:Node {type: 'Meter'})
WITH building, floors_count, spaces_count, total_area_sqm, total_capacity, equipments_count,
     COUNT(DISTINCT meter) AS meters_count

// ============================================================================
// DOMAINE IT
// ============================================================================
OPTIONAL MATCH (dc:Node {type: 'Datacenter'})-[:CONTAINS]->(rack:Node {type: 'Rack'})
OPTIONAL MATCH (rack)-[:HOSTS]->(server:Node {type: 'Server'})
WITH building, floors_count, spaces_count, total_area_sqm, total_capacity,
     equipments_count, meters_count,
     COUNT(DISTINCT dc) AS datacenters_count,
     COUNT(DISTINCT rack) AS racks_count,
     COUNT(DISTINCT server) AS servers_count

// ============================================================================
// DOMAINE AV
// ============================================================================
OPTIONAL MATCH (av:Node {type: 'AVSystem'})-[:HAS_PART]->(display:Node {type: 'Display'})
WITH building, floors_count, spaces_count, total_area_sqm, total_capacity,
     equipments_count, meters_count, datacenters_count, racks_count, servers_count,
     COUNT(DISTINCT av) AS av_systems_count,
     COUNT(DISTINCT display) AS displays_count

// ============================================================================
// DOMAINE PARKING
// ============================================================================
OPTIONAL MATCH (pz:Node {type: 'ParkingZone'})-[:CONTAINS]->(:Node {type: 'ParkingLevel'})-[:CONTAINS]->(ps:Node {type: 'ParkingSpot'})
OPTIONAL MATCH (vehicle:Node {type: 'Vehicle'})-[:PARKED_AT]->(ps)
WITH building, floors_count, spaces_count, total_area_sqm, total_capacity,
     equipments_count, meters_count, datacenters_count, racks_count, servers_count,
     av_systems_count, displays_count,
     COUNT(DISTINCT ps) AS parking_spots_count,
     COUNT(DISTINCT vehicle) AS vehicles_present

// ============================================================================
// DOMAINE SÉCURITÉ
// ============================================================================
OPTIONAL MATCH (sz:Node {type: 'SecurityZone'})-[:CONTAINS]->(ap:Node {type: 'AccessPoint'})
OPTIONAL MATCH (sz)-[:CONTAINS]->(cam:Node {type: 'Camera'})
WITH building, floors_count, spaces_count, total_area_sqm, total_capacity,
     equipments_count, meters_count, datacenters_count, racks_count, servers_count,
     av_systems_count, displays_count, parking_spots_count, vehicles_present,
     COUNT(DISTINCT sz) AS security_zones_count,
     COUNT(DISTINCT ap) AS access_points_count,
     COUNT(DISTINCT cam) AS cameras_count

// ============================================================================
// DOMAINE ORGANISATION
// ============================================================================
OPTIONAL MATCH (org:Node {type: 'Organization'})-[:CONTAINS]->(dept:Node {type: 'Department'})-[:CONTAINS]->(team:Node {type: 'Team'})
OPTIONAL MATCH (person:Node {type: 'Person'})-[:BELONGS_TO]->(team)
WITH building, floors_count, spaces_count, total_area_sqm, total_capacity,
     equipments_count, meters_count, datacenters_count, racks_count, servers_count,
     av_systems_count, displays_count, parking_spots_count, vehicles_present,
     security_zones_count, access_points_count, cameras_count,
     COUNT(DISTINCT dept) AS departments_count,
     COUNT(DISTINCT team) AS teams_count,
     COUNT(DISTINCT person) AS persons_count

// ============================================================================
// DOMAINE TENANTS
// ============================================================================
OPTIONAL MATCH (tenant:Node {type: 'Tenant'})-[:OCCUPIES]->(occupied:Node {type: 'Space'})
WITH building, floors_count, spaces_count, total_area_sqm, total_capacity,
     equipments_count, meters_count, datacenters_count, racks_count, servers_count,
     av_systems_count, displays_count, parking_spots_count, vehicles_present,
     security_zones_count, access_points_count, cameras_count,
     departments_count, teams_count, persons_count,
     COUNT(DISTINCT tenant) AS tenants_count,
     COUNT(DISTINCT occupied) AS occupied_spaces_count

// ============================================================================
// DOMAINE CONTRACTUEL
// ============================================================================
OPTIONAL MATCH (contract:Node {type: 'Contract'})-[:PROVIDED_BY]->(provider:Node {type: 'Provider'})
OPTIONAL MATCH (wo:Node {type: 'WorkOrder'})
WHERE wo.properties.status = 'open'

// ============================================================================
// RÉSULTAT FINAL
// ============================================================================
RETURN building.name AS building_name,
       // Spatial
       floors_count,
       spaces_count,
       total_area_sqm,
       total_capacity,
       // Equipment
       equipments_count,
       // Energy
       meters_count,
       // IT
       datacenters_count,
       racks_count,
       servers_count,
       // AV
       av_systems_count,
       displays_count,
       // Parking
       parking_spots_count,
       vehicles_present,
       CASE WHEN parking_spots_count > 0
            THEN round(100.0 * vehicles_present / parking_spots_count)
            ELSE 0 END AS parking_occupancy_pct,
       // Security
       security_zones_count,
       access_points_count,
       cameras_count,
       // Organization
       departments_count,
       teams_count,
       persons_count,
       // Tenants
       tenants_count,
       occupied_spaces_count,
       CASE WHEN spaces_count > 0
            THEN round(100.0 * occupied_spaces_count / spaces_count)
            ELSE 0 END AS space_occupancy_pct,
       // Contracts
       COUNT(DISTINCT contract) AS contracts_count,
       COUNT(DISTINCT wo) AS work_orders_open,
       // Note sur les limites
       'TIMESERIES_AGGREGATIONS_REQUIRE_EXTERNAL_SYSTEM' AS timeseries_note;
