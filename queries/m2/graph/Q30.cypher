// Q30: Cycle Detection
// Status: NATIVE pour M1/M2 (cycle pattern)
// Semantic: Detect cycles in FEEDS relationships (configuration error)
// Parametres: none

MATCH (n:Equipment)-[:FEEDS*2..10]->(n)
WITH DISTINCT n,
     size([(n)-[:FEEDS*2..10]->(n) | 1]) AS cycle_count
RETURN
    n.id AS node_id,
    n.equipment_type AS node_type,
    n.name AS node_name,
    cycle_count AS cycle_length
ORDER BY cycle_length, node_id;
