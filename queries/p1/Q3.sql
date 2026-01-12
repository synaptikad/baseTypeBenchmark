-- Q3: Space Services
-- Paramètre: $1 = SPACE_ID

SELECT
    eq.id AS equipment_id,
    eq.name AS equipment_name,
    eq.equipment_type,
    ed.rel_type AS relation_type
FROM edges ed
JOIN equipment eq ON eq.id = ed.source_id
WHERE ed.target_id = $1
  AND ed.rel_type = 'SERVES'
ORDER BY ed.rel_type, eq.id;
