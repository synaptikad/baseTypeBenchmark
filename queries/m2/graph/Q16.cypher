// Q16: Semantic Tag Search
// Status: NATIVE pour M1/M2
// Parametre: $tag_pattern (ex: '^brick:' - regex pattern becomes 'brick:.*' for Memgraph)
// Note: tags est une liste Cypher native
// Note: Memgraph regex ne supporte pas ^ correctement, on transforme le pattern

MATCH (eq:Equipment)
WHERE eq.tags IS NOT NULL
UNWIND eq.tags AS tag
WITH eq, tag,
     // Transform ^pattern to pattern.* for Memgraph compatibility
     CASE WHEN $tag_pattern STARTS WITH '^'
          THEN substring($tag_pattern, 1) + '.*'
          ELSE $tag_pattern END AS memgraph_pattern
WHERE toString(tag) =~ memgraph_pattern
RETURN
    eq.id AS equipment_id,
    eq.name,
    collect(toString(tag)) AS matching_tags
ORDER BY equipment_id;
