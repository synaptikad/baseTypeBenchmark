// QW8: Remove Property
// Équivalent M1 - Suppression de propriété
// Paramètres: $node_id, $key_to_remove
//
// Note: REMOVE supprime la propriété du nœud

MATCH (n {id: $node_id})
// Pour supprimer dynamiquement, on doit utiliser une approche différente
// Cypher ne supporte pas REMOVE n[$key] dynamiquement
// On utilise SET à null qui a le même effet
CALL {
    WITH n
    SET n[$key_to_remove] = null
    RETURN n
}
RETURN n.id AS id;
