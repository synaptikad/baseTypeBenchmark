-- Q37: Validate Relation Mutation (QW3)
-- Status: NATIVE pour P2 (edges table)
-- Paramètres: %(source_id)s, %(target_id)s
-- Semantic: Vérifie que la relation FEEDS existe entre source et target

SELECT
    e.source_id,
    s.name AS source_name,
    e.rel_type,
    e.target_id,
    t.name AS target_name
FROM p2.edges e
JOIN p2.nodes s ON e.source_id = s.id
JOIN p2.nodes t ON e.target_id = t.id
WHERE e.source_id = %(source_id)s
  AND e.target_id = %(target_id)s
  AND e.rel_type = 'FEEDS';
