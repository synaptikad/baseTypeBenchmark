// QW1: Space Reservation (M2 = graph Memgraph + TimescaleDB)
// Creates OCCUPIES relationship between tenant and space with period
// Parameters: $qw1_tenant_id, $qw1_space_id, $qw1_start_date, $qw1_end_date
// Note: Idempotent - uses MERGE to avoid duplicates on repeated runs

MATCH (t:Tenant {id: $qw1_tenant_id})
MATCH (s:Space {id: $qw1_space_id})
MERGE (t)-[r:OCCUPIES]->(s)
SET r.start_date = $qw1_start_date, r.end_date = $qw1_end_date
RETURN t.id AS tenant_id, s.id AS space_id;
