// Q29: All Power Paths
// Status: NATIVE pour M1/M2 (enumerate all paths)
// Semantic: Enumerate all electrical paths from transformer to critical equipment
// Parametres: $transformer_id

MATCH (source:Equipment {id: $transformer_id})
WHERE source.equipment_type = 'Transformer'
MATCH path = (source)-[:FEEDS*1..10]->(target:Equipment)
WHERE COALESCE(target.critical, false) = true
WITH path,
     [n IN nodes(path) | n.id] AS path_nodes,
     target
WITH path_nodes,
     size(path_nodes) AS path_length,
     target.id AS target_equipment,
     path_nodes[0] AS first_node
ORDER BY path_length, path_nodes
WITH collect({
    path_nodes: path_nodes,
    path_length: path_length,
    target_equipment: target_equipment
}) AS all_paths
UNWIND range(0, size(all_paths) - 1) AS path_id
WITH path_id + 1 AS path_id, all_paths[path_id] AS p
RETURN
    path_id,
    p.path_nodes AS path_nodes,
    p.path_length AS path_length,
    p.target_equipment AS target_equipment
ORDER BY path_length, path_id
LIMIT 100;
