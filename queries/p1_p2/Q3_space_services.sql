-- Q3: Space Services - What equipment serves this space?
-- Benchmark: Lookup relationship pattern
-- Parameter: $SPACE_ID - space to query for serving equipment

SELECT
    s.id as space_id,
    s.name as space_name,
    s.building_id,
    eq.id as equipment_id,
    eq.name as equipment_name,
    eq.type as equipment_type,
    e1.rel_type as relationship
FROM nodes s
JOIN edges e1 ON e1.src_id = s.id OR e1.dst_id = s.id
JOIN nodes eq ON (eq.id = e1.src_id OR eq.id = e1.dst_id) AND eq.id != s.id
WHERE s.id = '$SPACE_ID'
  AND eq.type = 'Equipment'
  AND e1.rel_type IN ('CONTAINS', 'SERVES', 'LOCATED_IN')
ORDER BY eq.name;
