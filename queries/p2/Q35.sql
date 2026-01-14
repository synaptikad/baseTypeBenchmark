-- Q35: Validate Space Reservation (QW1)
-- Returns tenants occupying a space during a given period
-- Paramètres: %(qw1_space_id)s, %(qw1_start_date)s, %(qw1_end_date)s

SELECT
    n.id AS tenant_id,
    n.name AS tenant_name,
    (e.properties->>'start_date')::date AS start_date,
    (e.properties->>'end_date')::date AS end_date
FROM p2.edges e
JOIN p2.nodes n ON e.source_id = n.id
WHERE e.target_id = %(qw1_space_id)s
  AND e.rel_type = 'OCCUPIES'
  AND (e.properties->>'start_date')::date <= %(qw1_end_date)s::date
  AND (e.properties->>'end_date')::date >= %(qw1_start_date)s::date
ORDER BY (e.properties->>'start_date')::date;
