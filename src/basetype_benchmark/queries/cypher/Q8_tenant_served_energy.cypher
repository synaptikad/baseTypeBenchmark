// Q8: Énergie consommée par locataire (Tenant Energy Consumption)
// Complexité: Cross-domain Tenant → Space → Equipment → Meter → Point
// Domaines: Tenant, Spatial, Equipment, Meter
// Use case: Sélection des points de puissance pour les espaces occupés par les locataires
// Note: L'agrégation timeseries se fait dans TimescaleDB

// Sélection graphe: tous les points power liés aux tenants
MATCH (t:Node {type: "Tenant"})-[:OCCUPIES]->(sp:Node {type: "Space"})
OPTIONAL MATCH (eq:Node {type: "Equipment"})-[:LOCATED_IN]->(sp)
OPTIONAL MATCH (m:Node {type: "Meter"})-[:FEEDS]->(eq)
OPTIONAL MATCH (m)-[:HAS_POINT]->(pt:Node {type: "Point"})
WHERE pt.quantity = "power"
WITH t.id AS tenant_id, t.name AS tenant_name,
     COLLECT(DISTINCT sp.id) AS spaces,
     SUM(COALESCE(sp.area_sqm, 0)) AS total_area_sqm,
     COLLECT(DISTINCT pt.id) AS power_point_ids
RETURN tenant_id, tenant_name,
       SIZE(spaces) AS spaces_count,
       total_area_sqm,
       SIZE(power_point_ids) AS power_points_count,
       power_point_ids
ORDER BY SIZE(power_point_ids) DESC
LIMIT 50;
