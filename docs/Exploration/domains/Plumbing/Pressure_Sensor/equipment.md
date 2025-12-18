# Pressure Sensor

## Identifiant
- **Code** : PRESSURE-SNS
- **Haystack** : `water`, `pressure`, `sensor`, `equip`
- **Brick** : `brick:Water_Pressure_Sensor`

## Description
Transmetteur de pression mesurant la pression statique ou dynamique de l'eau dans les canalisations et équipements. Élément clé pour le monitoring, la régulation et la protection des systèmes hydrauliques.

## Fonction
Mesurer en continu la pression d'eau dans les circuits, transmettre les valeurs au système de contrôle, permettre la régulation des pompes à vitesse variable, détecter les anomalies de pression, et protéger contre les surpressions ou dépressions.

## Variantes Courantes
- **Transmetteur piézorésistif** : Technologie standard, bon rapport qualité/prix
- **Transmetteur piézoélectrique** : Hautes fréquences, transitoires rapides
- **Transmetteur capacitif** : Haute stabilité, basses pressions
- **Pressostat** : Contact sec seuil de pression (tout/rien)
- **Transmetteur différentiel** : Mesure delta P (filtres, échangeurs)

## Caractéristiques Techniques Typiques
- Plage de mesure : 0-6 bars (distribution), 0-16 bars (surpression)
- Précision : ±0.25% à ±1% pleine échelle
- Sortie : 4-20mA, 0-10V, Modbus, BACnet
- Raccordement : 1/4" NPT, 1/2" BSP
- Température compensation : -10°C à +80°C
- Indice de protection : IP65-67

## Localisation Typique
- Refoulement Booster Pump (régulation pression)
- Entrée/sortie Pressure Reducing Valve
- DHW Tank (pression stockage)
- Collecteurs distribution (monitoring zones)
- Aspiration pompes (protection cavitation)

## Relations avec Autres Équipements
- **Alimente** : N/A (capteur)
- **Alimenté par** : N/A
- **Contrôlé par** : Régulation pompes, vannes, supervision
- **Associé à** : Booster Pump (régulation cascade), Pressure Reducing Valve, Motorized Valve

## Quantité Typique par Bâtiment
- Petit (5 étages) : 3-8 capteurs (pompes, circuits principaux)
- Moyen (15 étages) : 8-20 capteurs (multi-zones, régulation)
- Grand (30+ étages) : 20-60 capteurs (monitoring détaillé étagement pression)

## Sources
- Haystack Project - Pressure sensors
- Brick Schema - Pressure_Sensor class
- ISA standards - Pressure measurement
- Building automation protocols
