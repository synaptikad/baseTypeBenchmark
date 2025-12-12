-- Indexes pour le profil JSONB
-- On reprend les index structurels du profil relationnel et on limite l'indexation JSONB aux filtres utilisés.

BEGIN;

CREATE INDEX IF NOT EXISTS idx_nodes_type ON nodes(type);
CREATE INDEX IF NOT EXISTS idx_nodes_name ON nodes(name);

CREATE INDEX IF NOT EXISTS idx_edges_src_rel ON edges(src_id, rel_type);
CREATE INDEX IF NOT EXISTS idx_edges_dst_rel ON edges(dst_id, rel_type);
CREATE INDEX IF NOT EXISTS idx_edges_rel ON edges(rel_type);

-- Index JSONB minimal utilisé pour les filtres de tags (Q4)
CREATE INDEX IF NOT EXISTS idx_nodes_props_gin ON nodes USING GIN (props jsonb_path_ops);

-- Pas d'index GIN sur edges.props : les propriétés ajoutées sont statiques et non interrogées dans les requêtes Q1..Q8.

COMMIT;
