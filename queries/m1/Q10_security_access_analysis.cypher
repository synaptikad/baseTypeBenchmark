// Q10: Floor Security & Equipment Analysis
// Parameters: $FLOOR_ID - floor to analyze
// Pattern: Floor → Spaces → Equipment

MATCH (f:Node {id: '$FLOOR_ID'})-[:CONTAINS]->(sp:Node {type: 'Space'})
OPTIONAL MATCH (sp)-[:CONTAINS]->(eq:Node {type: 'Equipment'})
RETURN f.id AS floor_id,
       f.name AS floor_name,
       f.building_id AS building_id,
       sp.id AS space_id,
       sp.name AS space_name,
       collect(DISTINCT {id: eq.id, name: eq.name, type: eq.equipment_type}) AS equipment;
