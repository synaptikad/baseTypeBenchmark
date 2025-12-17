// Q10: Security Access Analysis
// Zone access points and security equipment

MATCH (z:Node {type: 'Zone'})
OPTIONAL MATCH (z)-[:CONTAINS]->(ap:Node {type: 'AccessPoint'})
OPTIONAL MATCH (z)-[]->(eq:Node {type: 'Equipment'})
RETURN z.id AS zone_id,
       z.name AS zone_name,
       z.building_id AS building_id,
       count(DISTINCT ap) AS access_point_count,
       count(DISTINCT eq) AS security_equipment_count
ORDER BY access_point_count DESC, security_equipment_count DESC
LIMIT 50;
