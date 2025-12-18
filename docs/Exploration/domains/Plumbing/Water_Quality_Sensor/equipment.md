# Water Quality Sensor

## Identifiant
- **Code** : WATER-QUAL-SNS
- **Haystack** : `water`, `quality`, `sensor`, `equip`
- **Brick** : `brick:Water_Quality_Sensor`

## Description
Capteur multi-paramètres mesurant en continu la qualité physico-chimique de l'eau (pH, conductivité, turbidité, chlore, température). Permet le monitoring en temps réel et la détection d'anomalies de qualité d'eau.

## Fonction
Mesurer et transmettre les paramètres de qualité de l'eau en temps réel, détecter les déviations par rapport aux valeurs normales, déclencher des alarmes en cas de contamination ou dégradation, et alimenter les systèmes d'analytics pour optimisation traitement.

## Variantes Courantes
- **Sonde pH** : Mesure acidité/alcalinité
- **Conductimètre** : Mesure minéralisation/salinité
- **Turbidimètre** : Mesure turbidité/transparence
- **Sonde chlore résiduel** : Vérification désinfection
- **Sonde multi-paramètres** : Plusieurs mesures simultanées
- **Analyseur bactériologique en ligne** : Détection microbiologique

## Caractéristiques Techniques Typiques
- Paramètres mesurés : pH (0-14), conductivité (0-2000 µS/cm), turbidité (0-1000 NTU)
- Précision : pH ±0.1, conductivité ±2%
- Température compensation : Automatique
- Sortie : 4-20mA, Modbus, BACnet
- Calibration : Automatique ou manuelle périodique
- Installation : Immersion ou en ligne (flow-through)

## Localisation Typique
- Arrivée eau réseau urbain
- Sortie traitement (adoucisseur, filtration, UV)
- Boucle retour ECS (contrôle qualité)
- Water Tank (monitoring stockage)
- Greywater System (avant/après traitement)

## Relations avec Autres Équipements
- **Alimente** : N/A (capteur)
- **Alimenté par** : N/A
- **Contrôlé par** : Système de supervision, analytics eau
- **Associé à** : Water Softener, Water Filtration System, UV Disinfection System, Dosing Pump

## Quantité Typique par Bâtiment
- Petit (5 étages) : 1-3 sondes (entrée + points critiques)
- Moyen (15 étages) : 3-8 sondes (multi-points monitoring)
- Grand (30+ étages) : 8-20 sondes (réseau complet + process spéciaux)

## Sources
- Haystack Project - Water quality sensors
- Brick Schema - Water_Quality_Sensor class
- Water quality monitoring standards (WHO, EPA)
- Smart water management systems
