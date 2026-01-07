-- Q4: Floor Temperature Inventory
-- Paramètre: $1 = FLOOR_ID

SELECT
    $1 AS floor_id,
    p.id AS point_id,
    p.name AS point_name,
    eq.id AS equipment_id,
    eq.name AS equipment_name
FROM points p
JOIN equipment eq ON eq.id = p.equipment_id
WHERE p.quantity = 'temperature'
  AND (
      -- Équipement directement sur l'étage
      eq.floor_id = $1
      OR
      -- Équipement dans un espace de l'étage
      eq.space_id IN (SELECT id FROM spaces WHERE floor_id = $1)
      OR
      -- Équipement qui SERVES un espace de l'étage
      EXISTS (
          SELECT 1 FROM edges e
          JOIN spaces s ON s.id = e.target_id
          WHERE e.source_id = eq.id
            AND e.rel_type = 'SERVES'
            AND s.floor_id = $1
      )
  )
ORDER BY eq.id, p.id;
