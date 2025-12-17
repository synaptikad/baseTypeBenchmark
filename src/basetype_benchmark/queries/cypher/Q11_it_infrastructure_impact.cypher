// Q11: Impact infrastructure IT sur le bâtiment (IT Infrastructure Impact)
// COMPLEXITÉ MAXIMALE: Cross-domain IT × Energy × Spatial × Equipment
// Domaines croisés: IT/Datacenter, Energy, Spatial, Equipment
// Use case: Analyser la topologie IT et ses connexions avec l'infrastructure bâtiment

// 1. Topologie complète du datacenter
MATCH (dc:Node {type: 'Datacenter'})-[:CONTAINS]->(rack:Node {type: 'Rack'})
OPTIONAL MATCH (dc)-[:LOCATED_IN]->(dcSpace:Node {type: 'Space'})

// 2. Serveurs dans les racks
OPTIONAL MATCH (rack)-[:HOSTS]->(server:Node {type: 'Server'})

// 3. Équipements réseau dans les racks
OPTIONAL MATCH (rack)-[:HOSTS]->(netdev:Node {type: 'NetworkDevice'})

// 4. Stockage dans les racks
OPTIONAL MATCH (rack)-[:HOSTS]->(storage:Node {type: 'Storage'})

// 5. Points de mesure IT (CPU, RAM, etc.)
OPTIONAL MATCH (server)-[:HAS_POINT]->(itPoint:Node {type: 'Point'})

// 6. Équipements CVC servant l'espace datacenter
OPTIONAL MATCH (hvacEquip:Node {type: 'Equipment'})-[:SERVES]->(dcSpace)

WITH dc,
     COLLECT(DISTINCT rack.id) AS racks,
     COUNT(DISTINCT server) AS servers_count,
     COUNT(DISTINCT netdev) AS network_devices_count,
     COUNT(DISTINCT storage) AS storage_count,
     COUNT(DISTINCT itPoint) AS it_metrics_points,
     COUNT(DISTINCT hvacEquip) AS cooling_equipment_count,
     dcSpace.name AS datacenter_space,
     dc.tier AS tier,
     dc.pue_target AS pue_target

RETURN dc.name AS datacenter_name,
       tier,
       pue_target,
       datacenter_space,
       SIZE(racks) AS racks_count,
       servers_count,
       network_devices_count,
       storage_count AS storage_units_count,
       it_metrics_points AS it_monitoring_points,
       cooling_equipment_count
ORDER BY servers_count DESC
LIMIT 20;
