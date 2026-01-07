// Q23: Adjacency Propagation
// Status: NATIVE pour M1/M2 (variable-length path)
// Paramètres: $space_id, $max_hops

MATCH (start:Space {id: $space_id})
CALL {
    WITH start
    MATCH path = (start)-[r:ADJACENT_TO|CONTAINS|MONITORS|SERVES*1..3]-(node)
    WHERE length(path) <= $max_hops
    WITH node, length(path) AS hop_distance, type(last(relationships(path))) AS via_relation
    RETURN DISTINCT node, hop_distance, via_relation
}
RETURN
    node.id AS node_id,
    CASE WHEN 'Space' IN labels(node) THEN 'Space'
         WHEN 'Equipment' IN labels(node) THEN 'Equipment'
         ELSE labels(node)[0]
    END AS node_type,
    node.name AS node_name,
    hop_distance,
    via_relation
ORDER BY hop_distance, node_type, node_id;
