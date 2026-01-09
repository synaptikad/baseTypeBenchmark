// Q16: Semantic Tag Search
// Status: NATIVE pour M1/M2 (avec MAGE)
// Paramètre: $tag_pattern (ex: 'brick:')
// Utilise json_util.from_json_list() de MAGE pour parser les tags JSON

MATCH (eq:Equipment)
WHERE eq.tags IS NOT NULL
WITH eq, json_util.from_json_list(eq.tags) AS tag_list
WHERE tag_list IS NOT NULL
UNWIND tag_list AS tag
WITH eq, tag
WHERE toString(tag) STARTS WITH $tag_pattern
RETURN
    eq.id AS equipment_id,
    eq.name,
    collect(toString(tag)) AS matching_tags
ORDER BY equipment_id;
