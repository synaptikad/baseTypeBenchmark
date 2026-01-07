// Q13: Office Hours Comfort - Points temperature/CO2 des bureaux
// Parametre: $building_id

MATCH (s:Space {building_id: $building_id})
WHERE s.space_type STARTS WITH 'office'
MATCH (eq:Equipment)-[:SERVES|MONITORS|LOCATED_IN]->(s)
MATCH (eq)-[:HAS_POINT]->(p:Point)
WHERE p.quantity IN ['temperature', 'co2']
RETURN s.id AS space_id, s.name AS space_name, collect({point_id: p.id, quantity: p.quantity}) AS points;
