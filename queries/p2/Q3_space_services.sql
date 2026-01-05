-- Q3: Space Services - What equipment serves/monitors this space?
-- Benchmark: Lookup relationship pattern (multi-relation)
-- Parameter: $SPACE_ID - space to query for serving/monitoring equipment
-- Relations: SERVES (HVAC), LOCATED_IN (equipment in space), CONTAINS (space contains), MONITORS (sensors)
-- P2: JSONB schema - structural queries are identical to P1

SELECT DISTINCT
    s.id as space_id,
    s.name as space_name,
    s.properties->>'building_id' as building_id,
    eq.id as equipment_id,
    eq.name as equipment_name,
    eq.type as equipment_type,
    e1.rel_type as relation
FROM nodes s
JOIN edges e1 ON e1.src_id = s.id OR e1.dst_id = s.id
JOIN nodes eq ON (eq.id = e1.src_id OR eq.id = e1.dst_id) AND eq.id != s.id
WHERE s.id = '$SPACE_ID'
  AND eq.type = 'Equipment'
  AND e1.rel_type IN ('CONTAINS', 'SERVES', 'LOCATED_IN', 'MONITORS')
ORDER BY e1.rel_type, eq.name;
