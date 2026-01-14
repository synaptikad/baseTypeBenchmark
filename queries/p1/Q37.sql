-- Q37: Validate Relation Mutation (QW3)
-- P1 version: uses equipment table instead of generic nodes
-- Paramètres: %(source_id)s, %(target_id)s

SELECT
    e.source_id,
    src.name AS source_name,
    e.rel_type,
    e.target_id,
    tgt.name AS target_name
FROM p1.edges e
JOIN p1.equipment src ON e.source_id = src.id
JOIN p1.equipment tgt ON e.target_id = tgt.id
WHERE e.source_id = %(source_id)s
  AND e.target_id = %(target_id)s
  AND e.rel_type = 'FEEDS';
