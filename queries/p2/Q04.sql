-- Q4: Floor Temperature Inventory (P2 JSONB)
-- Paramètre: $1 = FLOOR_ID

SELECT
    $1 AS floor_id,
    p.id AS point_id,
    p.name AS point_name,
    eq.id AS equipment_id,
    eq.name AS equipment_name
FROM nodes p
JOIN nodes eq ON eq.id = p.data->>'equipment_id' AND eq.node_type = 'Equipment'
WHERE p.node_type = 'Point'
  AND p.data->>'quantity' = 'temperature'
  AND (
      -- Équipement sur l'étage
      eq.data->>'floor_id' = $1
      OR
      -- Équipement dans un espace de l'étage
      EXISTS (
          SELECT 1 FROM nodes sp
          WHERE sp.node_type = 'Space'
            AND sp.id = eq.data->>'space_id'
            AND sp.data->>'floor_id' = $1
      )
      OR
      -- Équipement qui SERVES un espace de l'étage
      EXISTS (
          SELECT 1 FROM edges e
          JOIN nodes sp ON sp.id = e.target_id AND sp.node_type = 'Space'
          WHERE e.source_id = eq.id
            AND e.rel_type = 'SERVES'
            AND sp.data->>'floor_id' = $1
      )
  )
ORDER BY eq.id, p.id;
