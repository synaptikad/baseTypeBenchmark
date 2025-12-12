-- Chargement des noeuds pour le profil JSONB
\echo 'Chargement des nodes depuis :' :nodes_csv
\copy nodes (id, type, name) FROM :'nodes_csv' CSV HEADER;

-- Mise à jour des propriétés JSONB de base
UPDATE nodes
SET props = jsonb_build_object(
    'kind', type,
    'tags', to_jsonb(ARRAY_REMOVE(ARRAY[
        CASE WHEN type = 'Site' THEN 'haystack:site' END,
        CASE WHEN type = 'Building' THEN 'haystack:building' END,
        CASE WHEN type = 'Floor' THEN 'brick:Floor' END,
        CASE WHEN type = 'Space' THEN 'brick:Space' END,
        CASE WHEN type = 'Equipment' THEN 'brick:Equipment' END,
        CASE WHEN type = 'Point' THEN 'brick:Point' END,
        CASE WHEN type = 'Meter' THEN 'haystack:meter' END,
        CASE WHEN type = 'Tenant' THEN 'haystack:tenant' END
    ]::TEXT[], NULL))
)
WHERE props = '{}'::jsonb;
