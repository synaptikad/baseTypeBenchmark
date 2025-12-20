// Q10: Security Access Analysis
// Parameters: $ZONE_ID - zone to analyze, $DATE_START/$DATE_END (for event TS)
// Zone access points and security equipment

MATCH (z:Node {id: '$ZONE_ID'})
OPTIONAL MATCH (z)-[:CONTAINS]->(ap:Node {type: 'AccessPoint'})
OPTIONAL MATCH (z)-[]->(eq:Node {type: 'Equipment'})
RETURN z.id AS zone_id,
       z.name AS zone_name,
       z.building_id AS building_id,
       collect(DISTINCT {id: ap.id, name: ap.name}) AS access_points,
       collect(DISTINCT {id: eq.id, name: eq.name}) AS equipment;
