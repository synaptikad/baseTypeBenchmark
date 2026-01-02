-- Schéma relationnel optimisé pour PostgreSQL/TimescaleDB (P1)
--
-- Optimisations appliquées:
-- 1. Pas de FK sur edges (intégrité assurée par générateur, gain 10-30% INSERT)
-- 2. Index composites pour traversées graphe efficaces
-- 3. TimescaleDB avec compression automatique après 7 jours
-- 4. Chunk interval 1 jour pour granularité fine

BEGIN;

CREATE EXTENSION IF NOT EXISTS timescaledb;

-- =============================================================================
-- Table des noeuds
-- =============================================================================
CREATE TABLE IF NOT EXISTS nodes (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    name TEXT,
    building_id INTEGER DEFAULT 0
);

-- Index pour filtrage par type (très fréquent)
CREATE INDEX IF NOT EXISTS idx_nodes_type ON nodes(type);

-- Index pour filtrage par building (scale extraction)
CREATE INDEX IF NOT EXISTS idx_nodes_building ON nodes(building_id);

-- Index composite type + building pour requêtes combinées
CREATE INDEX IF NOT EXISTS idx_nodes_type_building ON nodes(type, building_id);

-- =============================================================================
-- Table des relations (sans FK pour performance)
-- =============================================================================
CREATE TABLE IF NOT EXISTS edges (
    src_id TEXT NOT NULL,
    dst_id TEXT NOT NULL,
    rel_type TEXT NOT NULL,
    PRIMARY KEY (src_id, dst_id, rel_type)
);

-- Index composites pour traversées graphe dans les deux sens
CREATE INDEX IF NOT EXISTS idx_edges_src_rel ON edges(src_id, rel_type);
CREATE INDEX IF NOT EXISTS idx_edges_dst_rel ON edges(dst_id, rel_type);

-- Index pour recherche par type de relation uniquement
CREATE INDEX IF NOT EXISTS idx_edges_rel ON edges(rel_type);

-- =============================================================================
-- Hypertable TimescaleDB pour séries temporelles
-- =============================================================================
CREATE TABLE IF NOT EXISTS timeseries (
    time TIMESTAMPTZ NOT NULL,
    point_id TEXT NOT NULL,
    value REAL
);

-- Convertir en hypertable avec chunks de 1 jour
SELECT create_hypertable('timeseries', 'time',
    if_not_exists => TRUE,
    chunk_time_interval => INTERVAL '1 day'
);

-- Index pour lookup par point + time (requêtes typiques)
CREATE INDEX IF NOT EXISTS idx_ts_point_time ON timeseries(point_id, time DESC);

-- Index pour agrégations par time uniquement (Q6, Q7)
CREATE INDEX IF NOT EXISTS idx_ts_time ON timeseries(time);

-- =============================================================================
-- Compression TimescaleDB (données > 7 jours)
-- =============================================================================
ALTER TABLE timeseries SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'point_id',
    timescaledb.compress_orderby = 'time DESC'
);

-- Politique de compression automatique
SELECT add_compression_policy('timeseries', INTERVAL '7 days', if_not_exists => TRUE);

COMMIT;
