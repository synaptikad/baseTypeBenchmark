// QW16: Remove Maintenance Event
// Supprimer la propriete maintenance_history
// Parametres: $equipment_id
//
// Use case: Nettoyer l'historique de maintenance (cleanup de QW4)

MATCH (eq:Equipment {id: $equipment_id})
REMOVE eq.maintenance_history
RETURN eq.id AS id, 1 AS maintenance_history_removed;
