-- Q16: Semantic Tag Search
-- Status: NATIVE pour P2
-- Paramètres: $1 = TAG_PATTERN (regex, ex: '^brick:')

SELECT
    eq.id AS equipment_id,
    eq.name,
    array_agg(tag) FILTER (WHERE tag ~ $1) AS matching_tags
FROM nodes eq,
     jsonb_array_elements_text(eq.data->'tags') AS tag
WHERE eq.node_type = 'Equipment'
  AND eq.data->'tags' IS NOT NULL
  AND tag ~ $1
GROUP BY eq.id, eq.name
HAVING COUNT(*) FILTER (WHERE tag ~ $1) > 0
ORDER BY eq.id;
