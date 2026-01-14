-- Q35: Validate Space Reservation (QW1)
-- Returns tenants occupying a space during a given period
-- Paramètres: %(qw1_space_id)s, %(qw1_start_date)s, %(qw1_end_date)s

SELECT
    t.id AS tenant_id,
    t.name AS tenant_name,
    e.start_date,
    e.end_date
FROM p1.edges e
JOIN p1.tenants t ON e.source_id = t.id
WHERE e.target_id = %(qw1_space_id)s
  AND e.rel_type = 'OCCUPIES'
  AND e.start_date <= %(qw1_end_date)s::date
  AND e.end_date >= %(qw1_start_date)s::date
ORDER BY e.start_date;
