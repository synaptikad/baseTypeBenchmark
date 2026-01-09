-- QW1: Timeseries Append
-- Paramètres: %(point_ids)s, %(timestamps)s, %(values)s (arrays)
-- Intention: Append de nouvelles mesures à TimescaleDB partagé
--
-- Modèle M2: INSERT via UNNEST sur le TimescaleDB partagé (ts.timeseries)

INSERT INTO ts.timeseries (point_id, time, value)
SELECT * FROM UNNEST(
    %(point_ids)s::text[],
    %(timestamps)s::timestamptz[],
    %(values)s::float8[]
);
