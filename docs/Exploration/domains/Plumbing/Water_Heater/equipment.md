# Water Heater

## Identifiant
- **Code** : WATER-HTR
- **Haystack** : `domesticWater`, `hot`, `heater`, `equip`
- **Brick** : `brick:Water_Heater`

## Description
Équipement de production de chaleur dédié au chauffage de l'eau sanitaire. Peut être instantané ou à accumulation, et utilise différentes sources d'énergie (gaz, électricité, fuel, pompe à chaleur).

## Fonction
Chauffer l'eau froide sanitaire pour la porter à température d'usage (55-60°C). Peut fonctionner en instantané (à la demande) ou charger un ballon de stockage. Assure la production primaire d'eau chaude sanitaire du bâtiment.

## Variantes Courantes
- **Chauffe-eau électrique** : Résistances électriques, instantané ou à accumulation
- **Chauffe-eau gaz** : Brûleur gaz avec échangeur, rendement élevé (condensation)
- **Pompe à chaleur sanitaire** : COP élevé, récupération calories air ambiant ou extérieur
- **Chauffe-eau solaire** : Capteurs solaires thermiques avec appoint
- **Chauffe-eau thermodynamique** : Combinaison PAC et résistance électrique

## Caractéristiques Techniques Typiques
- Puissance : 10 kW à 200 kW (tertiaire)
- Rendement : 85-98% (gaz condensation), COP 3-4 (PAC)
- Température de sortie : 55-65°C
- Débit instantané : 10-100 L/min (selon technologie)
- Communication : BACnet, Modbus, relais TOR
- Régulation modulante ou tout/rien

## Localisation Typique
- Chaufferie
- Local technique ECS
- Sous-sol
- Salle des machines

## Relations avec Autres Équipements
- **Alimente** : DHW Tank, réseau distribution ECS
- **Alimenté par** : Réseau eau froide, réseau gaz/électricité
- **Contrôlé par** : Contrôleur DDC, thermostat, régulation cascade
- **Mesure** : Temperature Sensor (entrée/sortie), Flow Meter, Water Meter

## Quantité Typique par Bâtiment
- Petit (5 étages) : 1 heater (20-40 kW)
- Moyen (15 étages) : 2-3 heaters (60-120 kW total) en cascade
- Grand (30+ étages) : 3-6 heaters (150-300 kW total) avec redondance

## Sources
- Haystack Project - Water heating equipment
- Brick Schema - Water_Heater class
- ASHRAE Handbook - HVAC Applications, Service Water Heating
- Building energy codes and standards
