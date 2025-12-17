-- Table commune pour les séries temporelles, partagée entre les deux profils.
-- Elle reste neutre: aucune propriété JSONB n'est ajoutée.

BEGIN;

CREATE TABLE IF NOT EXISTS timeseries (
    time TIMESTAMPTZ NOT NULL,
    point_id TEXT NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
    quantity TEXT NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    quality TEXT DEFAULT 'raw'
);

SELECT create_hypertable('timeseries', 'time', if_not_exists => TRUE);

COMMIT;
