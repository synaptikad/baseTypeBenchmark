-- Q4: Inventory - Temperature points for a specific floor
-- Benchmark: Filtering + aggregation (typical BMS inventory query)
-- Parameter: $FLOOR_ID - floor to inventory temperature points
-- Canonical: uses properties->>'quantity' = 'temperature' (lowercase)

SELECT DISTINCT
    f.id as floor_id,
    f.name as floor_name,
    f.building_id,
    p.id as point_id,
    p.name as point_name,
    eq.id as equipment_id,
    eq.name as equipment_name
FROM nodes f
JOIN edges e1 ON e1.src_id = f.id AND e1.rel_type = 'CONTAINS'
JOIN nodes sp ON sp.id = e1.dst_id AND sp.type = 'Space'
-- Equipment either CONTAINED by Space or SERVES the Space
JOIN edges e2 ON (e2.src_id = sp.id AND e2.rel_type = 'CONTAINS')
              OR (e2.dst_id = sp.id AND e2.rel_type = 'SERVES')
JOIN nodes eq ON eq.id = CASE WHEN e2.rel_type = 'CONTAINS' THEN e2.dst_id ELSE e2.src_id END
             AND eq.type = 'Equipment'
JOIN edges e3 ON e3.src_id = eq.id AND e3.rel_type = 'HAS_POINT'
JOIN nodes p ON p.id = e3.dst_id AND p.type = 'Point'
WHERE f.id = '$FLOOR_ID'
  AND p.properties->>'quantity' = 'temperature'
ORDER BY p.name;
