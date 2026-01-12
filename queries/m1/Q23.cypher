// Q23: Failure Impact Analysis
// Status: NATIVE pour M1/M2 (variable-length path)
// Semantic: If this equipment fails, which spaces/equipment are impacted within N hops?
// Paramètres: $equipment_id, $max_hops

MATCH (start:Equipment {id: $equipment_id})
CALL {
    WITH start
    MATCH path = (start)-[r:FEEDS|SERVES|POWERS*1..3]-(node)
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
