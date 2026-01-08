-- QW1: Timeseries Append
-- Inserts batch of timeseries measurements into shared Timescale
-- Parameters: %(point_ids)s, %(timestamps)s, %(values)s (arrays)

INSERT INTO ts.timeseries (point_id, time, value)
SELECT * FROM UNNEST(
    %(point_ids)s::text[],
    %(timestamps)s::timestamptz[],
    %(values)s::float8[]
);
