// Q16: Semantic Tag Search
// Status: NATIVE pour M1/M2
// Parametre: $tag_pattern (ex: '^brick:' - regex pattern)
// Note: tags est maintenant une liste Cypher native (pas JSON string)
// Note: Utilise =~ pour regex matching (compatible avec le pattern '^brick:')

MATCH (eq:Equipment)
WHERE eq.tags IS NOT NULL
UNWIND eq.tags AS tag
WITH eq, tag
WHERE toString(tag) =~ $tag_pattern
RETURN
    eq.id AS equipment_id,
    eq.name,
    collect(toString(tag)) AS matching_tags
ORDER BY equipment_id;
