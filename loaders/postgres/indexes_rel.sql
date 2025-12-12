-- Indexes pour le profil relationnel strict

BEGIN;

CREATE INDEX IF NOT EXISTS idx_nodes_type ON nodes(type);
CREATE INDEX IF NOT EXISTS idx_nodes_name ON nodes(name);

CREATE INDEX IF NOT EXISTS idx_edges_src_rel ON edges(src_id, rel_type);
CREATE INDEX IF NOT EXISTS idx_edges_dst_rel ON edges(dst_id, rel_type);
CREATE INDEX IF NOT EXISTS idx_edges_rel ON edges(rel_type);

COMMIT;
