// Q20: Shortest HVAC Path
// Status: NATIVE pour M1/M2 (shortestPath)
// Paramètres: $equipment_id, $space_id

MATCH (start:Equipment {id: $equipment_id}), (end:Space {id: $space_id})
MATCH path = shortestPath((start)-[:FEEDS|SERVES*..10]->(end))
UNWIND range(0, length(path)) AS idx
WITH nodes(path)[idx] AS node, idx AS path_index
RETURN
    path_index,
    node.id AS node_id,
    CASE WHEN 'Equipment' IN labels(node) THEN 'Equipment'
         WHEN 'Space' IN labels(node) THEN 'Space'
         ELSE labels(node)[0]
    END AS node_type,
    node.name AS node_name
ORDER BY path_index;
