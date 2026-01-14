// QW13: Cancel Space Reservation
// Supprimer une relation OCCUPIES entre un tenant et un espace
// Parametres: $tenant_id, $space_id, $start_date, $end_date
//
// Use case: Annuler une reservation d'espace (cleanup de QW9)

MATCH (t:Tenant {id: $tenant_id})-[r:OCCUPIES]->(s:Space {id: $space_id})
WHERE r.start_date IS NULL OR r.start_date = $start_date
DELETE r
RETURN t.id AS tenant_id, s.id AS space_id, 1 AS reservations_cancelled;
