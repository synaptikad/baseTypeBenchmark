// Q39: Verify Tenant Spaces
// Lister tous les espaces occupés par un locataire donné
// Paramètres: $tenant_id
// Validates: QW9 (Move-In), QW10 (Move-Out), QW11 (Reassignment)

MATCH (t:Tenant {id: $tenant_id})-[:OCCUPIES]->(s:Space)
RETURN s.id AS space_id, s.name AS space_name, labels(s)[0] AS space_type
ORDER BY space_id
