// Q1: Chaîne de distribution énergétique (Energy Distribution Chain)
// Complexité: Traversée récursive de l'arbre de compteurs (8 niveaux max)
// Domaines: Energy, Equipment
// Use case: Identifier tous les équipements alimentés par les compteurs racine

// Trouver les compteurs racine et tracer la chaîne énergétique
MATCH (root:Node)
WHERE root.type = "Meter" AND root.is_root = true
WITH root
OPTIONAL MATCH path = (root)-[:FEEDS*1..8]->(child:Node)
WHERE child.type IN ["Meter", "Equipment"]
WITH root, child, length(path) AS depth
RETURN
    depth,
    COUNT(DISTINCT child) AS meters_at_level,
    COUNT(DISTINCT CASE WHEN child.type = "Equipment" THEN child END) AS equipments_fed
ORDER BY depth
LIMIT 50;
