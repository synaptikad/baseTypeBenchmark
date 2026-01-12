// Q10: Security Access Analysis
// Parametre: $building_id

MATCH (s:Space {building_id: $building_id})
OPTIONAL MATCH (eq:Equipment)-[r:LOCATED_IN]->(s)
WHERE eq.equipment_type IN ['BadgeReader', 'IPCamera', 'DoorContact', 'PIRDetector']
WITH s, eq.equipment_type AS equipment_type
WHERE equipment_type IS NOT NULL
RETURN
    s.id AS space_id,
    s.name AS space_name,
    equipment_type,
    count(*) AS equipment_count
ORDER BY space_id, equipment_type;
