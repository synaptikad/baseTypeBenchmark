// Q1: Energy Chain - Traverse equipment → meter → point → timeseries
// Benchmark: Native graph traversal (where graph DBs shine)

MATCH path = (eq:Node {type: 'Equipment'})-[:FEEDS|HAS_POINT|MEASURES*1..4]->(target)
WITH eq.building_id AS building_id,
     labels(target)[0] AS target_type,
     length(path) AS depth
RETURN building_id,
       target_type AS type,
       count(*) AS node_count,
       max(depth) AS max_depth
ORDER BY building_id, node_count DESC;
