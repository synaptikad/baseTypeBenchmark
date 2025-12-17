-- Schéma JSONB optimisé pour PostgreSQL/TimescaleDB (P2)
--
-- Optimisations appliquées:
-- 1. Colonnes extraites du JSONB pour index B-tree efficaces
-- 2. Index GIN avec jsonb_path_ops (plus compact, requêtes @> rapides)
-- 3. Edges avec JSONB optionnel pour propriétés étendues
-- 4. Même hypertable timeseries que P1

BEGIN;

CREATE EXTENSION IF NOT EXISTS timescaledb;

-- =============================================================================
-- Table des noeuds avec JSONB flexible
-- =============================================================================
CREATE TABLE IF NOT EXISTS nodes (
    -- Colonnes extraites pour index B-tree rapides
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    name TEXT,
    building_id INTEGER DEFAULT 0,
    -- Document JSONB pour propriétés flexibles
    data JSONB NOT NULL DEFAULT '{}'::jsonb
);

-- Index B-tree sur colonnes extraites (rapide pour égalité/range)
CREATE INDEX IF NOT EXISTS idx_nodes_type ON nodes(type);
CREATE INDEX IF NOT EXISTS idx_nodes_building ON nodes(building_id);
CREATE INDEX IF NOT EXISTS idx_nodes_type_building ON nodes(type, building_id);

-- Index GIN pour recherches dans le document JSONB
-- jsonb_path_ops: plus compact, supporte uniquement @> mais suffisant
CREATE INDEX IF NOT EXISTS idx_nodes_gin ON nodes USING GIN (data jsonb_path_ops);

-- =============================================================================
-- Table des relations avec propriétés optionnelles
-- =============================================================================
CREATE TABLE IF NOT EXISTS edges (
    src_id TEXT NOT NULL,
    dst_id TEXT NOT NULL,
    rel_type TEXT NOT NULL,
    -- Propriétés optionnelles (NULL si non utilisé = économie espace)
    props JSONB DEFAULT NULL,
    PRIMARY KEY (src_id, dst_id, rel_type)
);

-- Index composites pour traversées graphe
CREATE INDEX IF NOT EXISTS idx_edges_src_rel ON edges(src_id, rel_type);
CREATE INDEX IF NOT EXISTS idx_edges_dst_rel ON edges(dst_id, rel_type);
CREATE INDEX IF NOT EXISTS idx_edges_rel ON edges(rel_type);

-- Index GIN sur propriétés edges (si utilisé)
CREATE INDEX IF NOT EXISTS idx_edges_props_gin ON edges USING GIN (props jsonb_path_ops)
    WHERE props IS NOT NULL;

-- =============================================================================
-- Hypertable TimescaleDB (identique à P1)
-- =============================================================================
CREATE TABLE IF NOT EXISTS timeseries (
    time TIMESTAMPTZ NOT NULL,
    point_id TEXT NOT NULL,
    value DOUBLE PRECISION,
    -- Métadonnées optionnelles pour P2 (qualité, source, etc.)
    metadata JSONB DEFAULT NULL
);

SELECT create_hypertable('timeseries', 'time',
    if_not_exists => TRUE,
    chunk_time_interval => INTERVAL '1 day'
);

CREATE INDEX IF NOT EXISTS idx_ts_point_time ON timeseries(point_id, time DESC);
CREATE INDEX IF NOT EXISTS idx_ts_time ON timeseries(time);

-- Compression avec support métadonnées
ALTER TABLE timeseries SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'point_id',
    timescaledb.compress_orderby = 'time DESC'
);

SELECT add_compression_policy('timeseries', INTERVAL '7 days', if_not_exists => TRUE);

COMMIT;
