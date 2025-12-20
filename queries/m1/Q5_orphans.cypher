// Q5: Orphan Detection - Nodes without relationships
// Benchmark: Pattern negation

MATCH (n:Node)
WHERE NOT (n)-[]-()
RETURN n.type AS type,
       count(*) AS orphan_count
ORDER BY orphan_count DESC;
