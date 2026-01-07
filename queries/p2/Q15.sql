-- Q15: Warranty Expiry
-- Status: NATIVE pour P2
-- Paramètres: $1 = DAYS_AHEAD (integer, ex: 90), $2 = REFERENCE_DATE (date)

SELECT
    eq.id AS equipment_id,
    eq.name,
    eq.data->>'equipment_type' AS equipment_type,
    (eq.data->'metadata'->>'warranty_end')::date AS warranty_end,
    ((eq.data->'metadata'->>'warranty_end')::date - $2::date) AS days_remaining
FROM nodes eq
WHERE eq.node_type = 'Equipment'
  AND eq.data->'metadata'->>'warranty_end' IS NOT NULL
  AND (eq.data->'metadata'->>'warranty_end')::date <= ($2::date + $1 * INTERVAL '1 day')
  AND (eq.data->'metadata'->>'warranty_end')::date >= $2::date
ORDER BY days_remaining, eq.id;
