// Q2: Functional Impact Analysis
// What spaces are affected if equipment X fails?
// Benchmark: Reverse traversal (graph pattern matching)

MATCH (eq:Node {type: 'Equipment'})
WITH eq LIMIT 1
MATCH path = (affected)-[:CONTAINS|SERVES|FEEDS*1..5]->(eq)
WHERE affected.type IN ['Space', 'Floor', 'Zone']
RETURN affected.type AS type,
       count(DISTINCT affected) AS affected_count,
       avg(length(path)) AS avg_distance
ORDER BY affected_count DESC;
