// Q2: Functional Impact Analysis
// What spaces are affected if equipment X fails?
// Benchmark: Reverse traversal (graph pattern matching)
// Parameter: $EQUIPMENT_ID - equipment to analyze for impact
//
// Note: SERVES direction is Equipment->Space in our dataset.
// We need to traverse CONTAINS/FEEDS backwards AND SERVES forwards.
// Using UNION to handle both directions correctly.

MATCH (eq:Node {id: '$EQUIPMENT_ID'})
OPTIONAL MATCH path1 = (affected)-[:CONTAINS|FEEDS*1..5]->(eq)
WHERE affected.type IN ['Space', 'Floor', 'Zone']
WITH eq, collect(DISTINCT {node: affected, dist: length(path1)}) as via_contains

OPTIONAL MATCH (eq)-[:SERVES]->(served:Node)
WHERE served.type IN ['Space', 'Floor', 'Zone']
WITH via_contains, collect(DISTINCT {node: served, dist: 1}) as via_serves

WITH via_contains + via_serves as all_affected
UNWIND all_affected as item
WITH item.node as affected, item.dist as dist
WHERE affected IS NOT NULL
RETURN affected.type AS type,
       count(DISTINCT affected) AS affected_count,
       avg(dist) AS avg_distance
ORDER BY affected_count DESC;
