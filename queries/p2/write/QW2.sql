-- QW2: Metadata Update
-- Updates a tag/property on a node using JSONB
-- Parameters: %(node_id)s, %(tag_key)s, %(tag_value)s

UPDATE p2.nodes
SET data = jsonb_set(
    COALESCE(data, '{}'::jsonb),
    ARRAY[%(tag_key)s],
    to_jsonb(%(tag_value)s::text),
    true
)
WHERE id = %(node_id)s;
