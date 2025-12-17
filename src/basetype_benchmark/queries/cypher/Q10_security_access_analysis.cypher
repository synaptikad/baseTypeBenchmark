// Q10: Analyse d'accès sécurité cross-domain (Security Access Analysis)
// COMPLEXITÉ MAXIMALE: Croisement Sécurité × Organisation × Spatial
// Domaines croisés: Security, Organization, Spatial
// Use case: Pour chaque zone de sécurité, analyser les accès par département

// 1. Zones de sécurité et leurs points d'accès
MATCH (secZone:Node {type: 'SecurityZone'})-[:CONTAINS]->(accessPoint:Node {type: 'AccessPoint'})
OPTIONAL MATCH (accessPoint)-[:LOCATED_IN]->(apSpace:Node {type: 'Space'})
OPTIONAL MATCH (accessPoint)-[:SECURES]->(securedSpace:Node {type: 'Space'})
OPTIONAL MATCH (accessPoint)-[:HAS_POINT]->(point:Node {type: 'Point'})

// Agrégation par zone de sécurité
WITH secZone,
     COLLECT(DISTINCT accessPoint.id) AS access_points,
     COLLECT(DISTINCT apSpace.id) AS spaces,
     COLLECT(DISTINCT securedSpace.id) AS secured_spaces,
     COLLECT(DISTINCT point.id) AS event_points,
     secZone.security_level AS security_level

// Cross avec les personnes travaillant dans ces espaces
OPTIONAL MATCH (person:Node {type: 'Person'})-[:WORKS_IN]->(ws:Node {type: 'Space'})
WHERE ws.id IN spaces
OPTIONAL MATCH (person)-[:BELONGS_TO]->(team:Node {type: 'Team'})-[:BELONGS_TO]->(dept:Node {type: 'Department'})

RETURN secZone.name AS zone_name,
       security_level,
       SIZE(access_points) AS access_points_count,
       SIZE(spaces) AS unique_spaces,
       SIZE(event_points) AS event_monitoring_points,
       COLLECT(DISTINCT dept.name) AS departments_with_access,
       SIZE(COLLECT(DISTINCT dept.name)) AS departments_count
ORDER BY access_points_count DESC
LIMIT 50;
