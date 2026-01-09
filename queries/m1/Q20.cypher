// Q20: Shortest HVAC Path
// Status: NATIVE pour M1/M2 (BFS traversal)
// Paramètres: $equipment_id, $space_id
// Memgraph: utilise *BFS au lieu de shortestPath()

MATCH (start:Equipment {id: $equipment_id}), (end:Space {id: $space_id})
MATCH path = (start)-[:FEEDS|:SERVES *BFS ..10]->(end)
UNWIND range(0, size(nodes(path)) - 1) AS idx
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
