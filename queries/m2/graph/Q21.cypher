// Q21: Electrical Resilience (SPOF Detection)
// Status: NATIVE pour M1/M2 (allShortestPaths)
// Paramètres: $equipment_id, $source_type

MATCH (target:Equipment {id: $equipment_id})
MATCH (source:Equipment {equipment_type: $source_type})
MATCH paths = allShortestPaths((source)-[:FEEDS*..10]->(target))
WITH collect(paths) AS all_paths, collect([n IN nodes(paths) | n.id]) AS all_node_lists

// Trouver les SPOF (nœuds présents dans TOUS les chemins)
UNWIND all_node_lists AS node_list
UNWIND node_list AS node_id
WITH all_paths, all_node_lists, node_id, count(*) AS occurrences
WHERE occurrences = size(all_node_lists)
WITH all_paths, collect(DISTINCT node_id) AS spof_nodes

UNWIND range(0, size(all_paths) - 1) AS path_idx
WITH all_paths[path_idx] AS path, path_idx + 1 AS path_id, spof_nodes
RETURN
    path_id,
    [n IN nodes(path) | n.id] AS path_nodes,
    length(path) AS path_length,
    spof_nodes
ORDER BY path_length, path_id;
