-- Chargement des arêtes pour le profil JSONB
\echo 'Chargement des edges depuis :' :edges_csv

CREATE TEMP TABLE tmp_edges (
    src_id TEXT,
    dst_id TEXT,
    rel_type TEXT
);

\copy tmp_edges (src_id, dst_id, rel_type) FROM :'edges_csv' CSV HEADER;

-- Ajout des quantités logiques manquantes dans nodes
INSERT INTO nodes (id, type, name)
SELECT DISTINCT dst_id AS id, 'Quantity' AS type, dst_id AS name
FROM tmp_edges te
WHERE te.rel_type = 'MEASURES'
  AND NOT EXISTS (SELECT 1 FROM nodes n WHERE n.id = te.dst_id);

INSERT INTO edges (src_id, dst_id, rel_type)
SELECT src_id, dst_id, rel_type FROM tmp_edges;

DROP TABLE tmp_edges;

-- Propriétés JSONB neutres sur les arêtes
UPDATE edges
SET props = jsonb_build_object('confidence', 1.0, 'source', 'synthetic')
WHERE props = '{}'::jsonb;

-- Compléter les propriétés des noeuds ajoutés pour les quantités
UPDATE nodes
SET props = jsonb_build_object(
    'kind', type,
    'tags', to_jsonb(ARRAY_REMOVE(ARRAY[
        CASE WHEN type = 'Quantity' THEN 'bms:quantity' END
    ]::TEXT[], NULL))
)
WHERE type = 'Quantity' AND props = '{}'::jsonb;

-- Ajout de tags JSONB dérivés des quantités mesurées
WITH point_quantities AS (
    SELECT m.src_id AS point_id, array_agg(DISTINCT 'quantity:' || m.dst_id) AS tags
    FROM edges m
    WHERE m.rel_type = 'MEASURES'
    GROUP BY m.src_id
)
UPDATE nodes n
SET props = jsonb_set(
    props,
    '{tags}',
    to_jsonb(
        ARRAY(
            SELECT DISTINCT tag
            FROM (
                SELECT jsonb_array_elements_text(COALESCE(n.props->'tags', '[]'::jsonb)) AS tag
                UNION ALL
                SELECT unnest(pq.tags)
            ) merged
            WHERE tag IS NOT NULL
        )
    ),
    FALSE
)
FROM point_quantities pq
WHERE n.id = pq.point_id;
