-- Q22: Equipment Siblings (P2 JSONB)
-- Status: NATIVE pour P2 (self-join efficace)
-- Parametres: $1 = EQUIPMENT_ID

SELECT
    sibling.id AS sibling_id,
    sibling.name AS sibling_name,
    sibling.data->>'equipment_type' AS sibling_type,
    parent.id AS parent_id,
    parent.name AS parent_name
FROM edges e1
JOIN nodes parent ON parent.id = e1.source_id
JOIN edges e2 ON e2.source_id = parent.id AND e2.rel_type = 'FEEDS'
JOIN nodes sibling ON sibling.id = e2.target_id
WHERE e1.target_id = $1
  AND e1.rel_type = 'FEEDS'
  AND sibling.id != $1
ORDER BY parent.id, sibling.id;
