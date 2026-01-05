// Q3: Space Services - What equipment serves/monitors this space?
// Benchmark: Lookup relationship pattern (multi-relation)
// Parameter: $SPACE_ID - space to query for serving/monitoring equipment
// Relations: SERVES (HVAC), LOCATED_IN (equipment in space), CONTAINS (space contains), MONITORS (sensors)

MATCH (s:Node {id: '$SPACE_ID'})-[r:CONTAINS|SERVES|LOCATED_IN|MONITORS]-(eq:Node {type: 'Equipment'})
WITH DISTINCT s, eq, collect(type(r)) AS relationships
RETURN s.id AS space_id,
       s.name AS space_name,
       s.building_id AS building_id,
       eq.id AS equipment_id,
       eq.name AS equipment_name,
       eq.type AS equipment_type,
       relationships
ORDER BY eq.name;
