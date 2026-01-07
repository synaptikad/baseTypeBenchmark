// Q16: Semantic Tag Search
// Status: DEGRADED pour M1/M2
// Note: Suppose que tags est une liste exportée
// Paramètre: $tag_pattern (ex: 'brick:')

MATCH (eq:Equipment)
WHERE eq.tags IS NOT NULL
UNWIND eq.tags AS tag
WITH eq, tag
WHERE tag STARTS WITH $tag_pattern
RETURN
    eq.id AS equipment_id,
    eq.name,
    collect(tag) AS matching_tags
ORDER BY equipment_id;
