// Q27: Evacuation Path
// Status: NATIVE pour M1/M2 (shortestPath avec distances)
// Semantic: Find shortest evacuation path from space to emergency exit
// Parametres: $space_id

MATCH (start:Space {id: $space_id})
WHERE NOT COALESCE(start.is_exit, false)
MATCH (exit:Space {is_exit: true})
MATCH path = (start)-[:EMERGENCY_EXIT|ACCESSIBLE_FROM *BFS ..15]->(exit)
WITH path,
     nodes(path) AS path_nodes,
     relationships(path) AS path_rels
WITH path_nodes, path_rels,
     reduce(total = 0.0, r IN path_rels | total + COALESCE(r.distance, 1.0)) AS total_distance
ORDER BY total_distance
LIMIT 1  // Ne garder qu'un seul chemin (le plus court)
UNWIND range(0, size(path_nodes) - 1) AS idx
RETURN
    idx AS path_index,
    path_nodes[idx].id AS node_id,
    path_nodes[idx].name AS node_name,
    CASE WHEN idx = 0 THEN 0.0
         ELSE reduce(d = 0.0, i IN range(0, idx - 1) | d + COALESCE(path_rels[i].distance, 1.0))
    END AS total_distance
ORDER BY path_index
LIMIT 50;
