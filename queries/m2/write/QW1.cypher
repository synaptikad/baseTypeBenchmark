// QW1: Space Reservation (M2 = graph Memgraph + TimescaleDB)
// Creates OCCUPIES relationship between tenant and space with period
// Parameters: $qw1_tenant_id, $qw1_space_id, $qw1_start_date, $qw1_end_date

MATCH (t:Tenant {id: $qw1_tenant_id})
MATCH (s:Space {id: $qw1_space_id})
CREATE (t)-[:OCCUPIES {start_date: $qw1_start_date, end_date: $qw1_end_date}]->(s)
RETURN t.id AS tenant_id, s.id AS space_id;
