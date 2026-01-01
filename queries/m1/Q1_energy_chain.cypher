// Q1: Energy Chain - Traverse from meter through FEEDS chain
// Benchmark: Native graph traversal (where graph DBs shine)
// Parameter: $METER_ID - starting meter for energy chain traversal

MATCH path = (meter:Node {id: '$METER_ID'})-[:FEEDS*1..10]->(target)
WITH DISTINCT target, min(length(path)) AS depth
RETURN target.id AS id,
       target.type AS type,
       target.name AS name,
       depth
ORDER BY depth, type;
