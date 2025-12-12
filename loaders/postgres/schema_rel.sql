-- Schéma relationnel strict pour PostgreSQL/TimescaleDB
-- Ce profil conserve uniquement les colonnes relationnelles explicites.

BEGIN;

CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE IF NOT EXISTS nodes (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS edges (
    src_id TEXT NOT NULL,
    dst_id TEXT NOT NULL,
    rel_type TEXT NOT NULL,
    PRIMARY KEY (src_id, dst_id, rel_type),
    FOREIGN KEY (src_id) REFERENCES nodes(id) ON DELETE CASCADE,
    FOREIGN KEY (dst_id) REFERENCES nodes(id) ON DELETE CASCADE
);

COMMIT;
