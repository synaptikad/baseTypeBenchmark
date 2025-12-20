// Q3: Space Services - What equipment serves this space?
// Benchmark: Lookup relationship pattern
// Parameter: $SPACE_ID - space to query for serving equipment

MATCH (s:Node {id: '$SPACE_ID'})-[r:CONTAINS|SERVES|LOCATED_IN]-(eq:Node {type: 'Equipment'})
RETURN s.id AS space_id,
       s.name AS space_name,
       s.building_id AS building_id,
       eq.id AS equipment_id,
       eq.name AS equipment_name,
       eq.type AS equipment_type,
       type(r) AS relationship
ORDER BY eq.name;
