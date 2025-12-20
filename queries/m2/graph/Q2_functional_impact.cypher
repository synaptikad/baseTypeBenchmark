// Q2: Functional Impact Analysis
// What spaces are affected if equipment X fails?
// Benchmark: Reverse traversal (graph pattern matching)
// Parameter: $EQUIPMENT_ID - equipment to analyze for impact

MATCH (eq:Node {id: '$EQUIPMENT_ID'})
MATCH path = (affected)-[:CONTAINS|SERVES|FEEDS*1..8]->(eq)
WHERE affected.type IN ['Space', 'Floor', 'Zone']
RETURN affected.type AS type,
       count(DISTINCT affected) AS affected_count,
       avg(length(path)) AS avg_distance
ORDER BY affected_count DESC;
