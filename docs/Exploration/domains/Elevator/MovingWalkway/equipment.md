# Moving Walkway

## Identifiant
- **Code** : MOVING_WALK
- **Haystack** : movingWalkway + equip
- **Brick** : brick:Moving_Walkway (subclass of brick:Vertical_Transport_Equipment)

## Description
Trottoir roulant permettant le déplacement horizontal ou faiblement incliné de personnes sur de longues distances. Équipement communicant pour supervision et optimisation énergétique dans les grands espaces.

## Fonction
Faciliter le déplacement des personnes sur de longues distances horizontales ou faibles pentes, typiquement dans les aéroports, gares et grands centres commerciaux.

## Variantes Courantes
- **Tapis horizontal** : Pente 0°, corridors et longs passages
- **Tapis incliné** : Pente jusqu'à 12°, faibles dénivelés
- **Tapis à vitesse variable** : Accélération en zone centrale
- **Tapis bidirectionnel** : Sens modifiable selon flux
- **Tapis extérieur** : Protection météo

## Caractéristiques Techniques Typiques
- Largeur : 800mm, 1000mm ou 1400mm
- Vitesse : 0.5 m/s à 0.75 m/s
- Longueur : 10m à 200m
- Inclinaison max : 12° (6° typique)
- Capacité : 6000 à 11000 personnes/heure
- Protocoles : BACnet, Modbus TCP, OPC UA
- Mode éco : Arrêt ou ralentissement si inoccupé

## Localisation Typique
- Aéroports (terminaux, satellites)
- Gares (quais, correspondances)
- Centres commerciaux (longues allées)
- Centres de congrès
- Parkings souterrains vers bâtiment

## Relations avec Autres Équipements
- **Alimente** : N/A
- **Alimenté par** : Electrical Panel
- **Contrôlé par** : Walkway Controller, PLC
- **Supervise par** : Building Management System
- **Interagit avec** : Occupancy Sensor, Lighting System, Fire Alarm System

## Quantité Typique par Bâtiment
- Petit (5 étages) : 0 tapis roulants
- Moyen (15 étages) : 0-2 tapis (si distances importantes)
- Grand (30+ étages) : 0-8 tapis (selon configuration et usage)

## Sources
- Haystack Project 4.0 - Moving walkway equipment
- Brick Schema - Moving_Walkway class
- EN 115-1:2017 - Safety of escalators and moving walks
- ISO 25745-3 - Energy performance of moving walks
