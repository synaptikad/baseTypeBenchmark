-- Chargement des arêtes pour le profil relationnel strict
\echo 'Chargement des edges depuis :' :edges_csv

CREATE TEMP TABLE tmp_edges (
    src_id TEXT,
    dst_id TEXT,
    rel_type TEXT
);

\copy tmp_edges (src_id, dst_id, rel_type) FROM :'edges_csv' CSV HEADER;

-- Les quantités logiques (MEASURES) ne sont pas présentes dans nodes.csv : on les ajoute pour respecter les clés étrangères.
INSERT INTO nodes (id, type, name)
SELECT DISTINCT dst_id AS id, 'Quantity' AS type, dst_id AS name
FROM tmp_edges te
WHERE te.rel_type = 'MEASURES'
  AND NOT EXISTS (SELECT 1 FROM nodes n WHERE n.id = te.dst_id);

INSERT INTO edges (src_id, dst_id, rel_type)
SELECT src_id, dst_id, rel_type FROM tmp_edges;

DROP TABLE tmp_edges;
