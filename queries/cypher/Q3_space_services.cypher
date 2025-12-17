// Q3: Space Services - What equipment serves each space?
// Benchmark: Bidirectional relationship matching

MATCH (s:Node {type: 'Space'})-[:CONTAINS|SERVES|LOCATED_IN]-(eq:Node {type: 'Equipment'})
RETURN s.id AS space_id,
       s.name AS space_name,
       s.building_id AS building_id,
       count(DISTINCT eq) AS equipment_count,
       collect(DISTINCT eq.type) AS equipment_types
ORDER BY equipment_count DESC
LIMIT 100;
