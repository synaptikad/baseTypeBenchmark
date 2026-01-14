// Q35: Validate Space Reservation (QW1) - M2 graph query
// Retourne les tenants qui occupent une salle sur une période donnée
// Paramètres: $qw1_space_id, $qw1_start_date, $qw1_end_date

MATCH (t:Tenant)-[r:OCCUPIES]->(s:Space {id: $qw1_space_id})
WHERE r.start_date <= $qw1_end_date AND r.end_date >= $qw1_start_date
RETURN t.id AS tenant_id,
       t.name AS tenant_name,
       r.start_date AS start_date,
       r.end_date AS end_date
ORDER BY r.start_date;
