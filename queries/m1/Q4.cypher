// Q4: Floor Temperature Inventory
// Parametre: $floor_id
// Intention: Pour un etage, lister les points temperature.

MATCH (f:Floor {id: $floor_id})
OPTIONAL MATCH (f)<-[:CONTAINS]-(b:Building)

// Points via equipements sur cet etage
MATCH (eq:Equipment)-[:HAS_POINT]->(p:Point)
WHERE p.quantity = 'temperature'
  AND (
      eq.floor_id = $floor_id
      OR EXISTS {
          MATCH (eq)-[:LOCATED_IN|SERVES]->(sp:Space {floor_id: $floor_id})
      }
  )
RETURN
    $floor_id AS floor_id,
    p.id AS point_id,
    p.name AS point_name,
    eq.id AS equipment_id,
    eq.name AS equipment_name
ORDER BY equipment_id, point_id;
