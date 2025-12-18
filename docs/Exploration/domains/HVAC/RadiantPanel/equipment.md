# Radiant Panel (Panneau rayonnant)

## Identifiant
- **Code** : RAD / RP
- **Haystack** : `radiantPanel-equip`
- **Brick** : `brick:Radiant_Panel`

## Description
Système de chauffage et/ou refroidissement par rayonnement qui échange la chaleur principalement par radiation thermique avec les occupants et surfaces environnantes. Peut être au plafond, au sol, ou mural. Alimenté par eau chaude ou eau glacée.

## Fonction
Assurer le confort thermique par échange radiatif (pas de mouvement d'air), avec une sensation de confort supérieure à des températures d'air plus basses. Efficacité énergétique élevée grâce aux basses températures d'eau.

## Variantes Courantes
- **Plafond rayonnant** : Panneaux au plafond (refroidissement et chauffage)
- **Plancher rayonnant** : Tubes noyés dans dalle (principalement chauffage)
- **Mur rayonnant** : Panneaux muraux (moins courant)
- **Panneau actif (TABS)** : Thermally Activated Building Systems, dalle massive
- **Panneau passif** : Échange uniquement radiatif
- **Panneau chauffant seul** : Chauffage uniquement
- **Panneau réversible** : Chaud et froid

## Caractéristiques Techniques Typiques
- Puissance surfacique : 50 - 150 W/m² (chauffage), 40 - 100 W/m² (refroidissement)
- Température eau chaude : 30-45°C (plancher), 35-55°C (plafond chauffage)
- Température eau glacée : 14-18°C (plafond refroidissement)
- Surface active : variable selon zone
- Protocoles : BACnet, Modbus (via vannes/contrôleurs)
- Points de supervision : températures eau aller/retour, température surface, alarmes

## Localisation Typique
- Plafonds de bureaux, salles de réunion
- Sols de logements, bureaux
- Murs (rare)

## Relations avec Autres Équipements
- **Alimente** : Zone (confort radiatif)
- **Alimenté par** : Chiller (eau glacée), Boiler/Heat Pump (eau chaude)
- **Contrôlé par** : Thermostats de zone, Vannes motorisées, BMS
- **Interagit avec** : Pompes de circulation, Capteurs température surface, Sonde humidité (anti-condensation)

## Quantité Typique par Bâtiment
- Petit (5 étages) : 10-50 zones avec panneaux
- Moyen (15 étages) : 50-200 zones
- Grand (30+ étages) : 200-800 zones

## Sources
- Haystack Project - Radiant Equipment
- Brick Schema - Radiant Panel Classes
- BACnet Standard - Radiant Systems Control
- ASHRAE Handbook - Radiant Heating and Cooling
