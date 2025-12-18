# DHW Tank

## Identifiant
- **Code** : DHW-TANK
- **Haystack** : `domesticWater`, `hot`, `tank`, `equip`
- **Brick** : `brick:Domestic_Hot_Water_Tank`

## Description
Ballon de stockage d'eau chaude sanitaire (ECS) destiné à fournir de l'eau chaude aux usages domestiques du bâtiment. Il maintient un volume d'eau à température contrôlée et peut être équipé de résistances électriques ou d'échangeurs thermiques.

## Fonction
Stocker l'eau chaude sanitaire à température régulée (généralement 55-60°C) pour répondre aux besoins instantanés du bâtiment tout en prévenant le développement de légionelles. Permet de découpler la production de chaleur de la demande instantanée.

## Variantes Courantes
- **Tank électrique** : Chauffage par résistances électriques intégrées
- **Tank avec échangeur** : Chauffage indirect via échangeur alimenté par chaudière ou réseau de chaleur
- **Tank solaire** : Intégré à un système solaire thermique avec appoint
- **Tank stratifié** : Conception favorisant la stratification thermique pour meilleure efficacité

## Caractéristiques Techniques Typiques
- Capacité : 200L à 5000L (bâtiments tertiaires)
- Température de consigne : 55-60°C (anti-légionelles)
- Isolation thermique renforcée (classe énergétique)
- Pression de service : 6-10 bars
- Multiple sondes de température (haut, milieu, bas)
- Anode anticorrosion (sacrificielle ou à courant imposé)

## Localisation Typique
- Local technique chaufferie
- Sous-sol technique
- Salle des machines
- Gaine technique (petites capacités)

## Relations avec Autres Équipements
- **Alimente** : Réseau de distribution ECS, DHW Circulation Pump, Mixing Valve
- **Alimenté par** : Water Heater, Heat Exchanger, réseau eau froide, Potable Water Pump
- **Contrôlé par** : Contrôleur DDC/PLC, régulation température
- **Mesure** : Temperature Sensor (multiple niveaux), Pressure Sensor, Level Sensor

## Quantité Typique par Bâtiment
- Petit (5 étages) : 1-2 tanks (300-500L total)
- Moyen (15 étages) : 2-4 tanks (1000-2000L total)
- Grand (30+ étages) : 4-8 tanks (3000-6000L total) avec production décentralisée possible

## Sources
- Haystack Project - Equipment definitions
- Brick Schema - Domestic Hot Water classes
- ASHRAE Guideline 12 - Minimizing the Risk of Legionellosis
- Building automation standards (BACnet, Modbus)
