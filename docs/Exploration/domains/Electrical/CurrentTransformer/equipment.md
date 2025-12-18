# Transformateur de Courant (CT - Current Transformer)

## Identifiant
- **Code** : TC / CT
- **Haystack** : sensor, current-sensor
- **Brick** : Current_Sensor

## Description
Capteur de mesure qui transforme un courant élevé (primaire) en un courant proportionnel faible (secondaire 1A ou 5A) utilisable par les appareils de mesure et de protection. Permet la mesure de courants importants de manière sécurisée et normalisée.

## Fonction
Adapter le courant circulant dans les conducteurs principaux à un niveau compatible avec les compteurs d'énergie, relais de protection et analyseurs. Assure l'isolation galvanique entre le circuit de puissance et les circuits de mesure/protection.

## Variantes Courantes
- **TC tore fermé** : Installation sur conducteur dénudé (montage initial)
- **TC tore ouvrant** : Installation sans coupure (retrofit)
- **TC pince ampèremétrique** : Mesure temporaire ou fixe
- **TC bobine de Rogowski** : Pour courants très élevés ou formes complexes
- **TC précision comptage** : Classe 0.2S à 0.5S (facturation)
- **TC précision protection** : Classe 5P, 10P (relais protection)

## Caractéristiques Techniques Typiques
- Rapports de transformation : 50/5A à 5000/5A (ou /1A)
- Classe de précision : 0.2S, 0.5, 1 (comptage), 5P, 10P (protection)
- Puissance de précision : 2.5 à 30 VA
- Isolement : 0.72 à 36 kV
- Montage : Traversant, tore ouvrant, sur barre
- Sortie : 1A ou 5A normalisée

## Localisation Typique
- TGBT (départs principaux)
- Tableaux divisionnaires (circuits mesurés)
- Cellules MT (transformateur)
- Armoires électriques avec comptage

## Relations avec Autres Équipements
- **Mesure** : Courant circulant dans conducteurs
- **Alimente** : Compteurs d'énergie, analyseurs de puissance, relais de protection
- **Associé à** : Conducteurs de puissance, jeu de barres
- **Supervisé via** : Compteurs/analyseurs raccordés

## Quantité Typique par Bâtiment
- Petit (5 étages) : 10-30
- Moyen (15 étages) : 50-150
- Grand (30+ étages) : 150-500

## Sources
- Brick Schema (Current_Sensor class)
- Haystack v4 (sensor, current tags)
- Standards IEC 61869-2 (transformateurs de courant)
- Documentation technique mesure électrique
