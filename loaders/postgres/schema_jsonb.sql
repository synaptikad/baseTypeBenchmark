-- Schéma relationnel + JSONB pour PostgreSQL/TimescaleDB
-- Les propriétés additionnelles sont stockées dans props tout en conservant le schéma comparable.

BEGIN;

CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE IF NOT EXISTS nodes (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    name TEXT NOT NULL,
    props JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS edges (
    src_id TEXT NOT NULL,
    dst_id TEXT NOT NULL,
    rel_type TEXT NOT NULL,
    props JSONB NOT NULL DEFAULT '{}'::jsonb,
    PRIMARY KEY (src_id, dst_id, rel_type),
    FOREIGN KEY (src_id) REFERENCES nodes(id) ON DELETE CASCADE,
    FOREIGN KEY (dst_id) REFERENCES nodes(id) ON DELETE CASCADE
);

COMMIT;
