// Q11: IT Infrastructure Impact Analysis
// Server room and IT equipment dependencies

MATCH (sp:Node {type: 'Space'})-[:CONTAINS]->(eq:Node {type: 'Equipment'})
WHERE eq.name =~ '(?i).*(server|network|switch|router|ups).*'
RETURN sp.id AS space_id,
       sp.name AS space_name,
       sp.building_id AS building_id,
       count(DISTINCT eq) AS it_equipment_count,
       collect(DISTINCT eq.name) AS equipment_names
ORDER BY it_equipment_count DESC
LIMIT 20;
