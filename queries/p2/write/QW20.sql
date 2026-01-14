-- QW20: Restore Removed Key (cleanup QW8)
-- Restaure la clé supprimée par QW8 dans data->'metadata'
-- Paramètres: %(qw8_node_id)s, %(qw8_key_to_remove)s, %(qw8_original_value)s

UPDATE p2.nodes
SET data = jsonb_set(
    data,
    ARRAY['metadata', %(qw8_key_to_remove)s],
    to_jsonb(%(qw8_original_value)s::text)
)
WHERE id = %(qw8_node_id)s
RETURNING id;
