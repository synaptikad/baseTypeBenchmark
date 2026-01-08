// QW3: Relation Mutation
// Creates a new edge between two nodes using MERGE
// Parameters: $source_id, $target_id, $rel_type

MATCH (a {id: $source_id}), (b {id: $target_id})
MERGE (a)-[r:FEEDS]->(b)
RETURN count(r) AS rows_inserted;
