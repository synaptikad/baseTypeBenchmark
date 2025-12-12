-- Chargement des noeuds pour le profil relationnel strict
\echo 'Chargement des nodes depuis :' :nodes_csv
\copy nodes (id, type, name) FROM :'nodes_csv' CSV HEADER;
