# Escalator

## Identifiant
- **Code** : ESCALATOR
- **Haystack** : escalator + equip
- **Brick** : brick:Escalator (subclass of brick:Vertical_Transport_Equipment)

## Description
Escalier mécanique motorisé permettant le déplacement continu de personnes entre deux niveaux. Équipement communicant intégré au BMS pour la supervision de l'état, des performances et la gestion énergétique.

## Fonction
Assurer le transport vertical continu et fluide de grands volumes de personnes entre des niveaux adjacents. Optimise les flux de circulation dans les espaces à forte affluence.

## Variantes Courantes
- **Escalator standard** : Pente 30°, hauteur jusqu'à 6m
- **Escalator à forte pente** : Pente 35°, espaces réduits
- **Escalator haute capacité** : Largeur 1200mm, zones à fort trafic
- **Escalator extérieur** : Protection météo renforcée
- **Escalator à vitesse variable** : Ralentissement automatique si inoccupé

## Caractéristiques Techniques Typiques
- Largeur marche : 600mm, 800mm ou 1000mm
- Vitesse : 0.5 m/s (standard) à 0.75 m/s (express)
- Capacité : 4500 à 13500 personnes/heure selon largeur
- Inclinaison : 30° (standard) ou 35° (spécial)
- Hauteur : 3m à 10m typiquement
- Protocoles : BACnet, Modbus TCP, OPC UA
- Capteurs : Présence, vibration, température, sécurité

## Localisation Typique
- Halls d'entrée et atriums
- Centres commerciaux
- Stations de métro et gares
- Aéroports
- Immeubles de bureaux (lobby)

## Relations avec Autres Équipements
- **Alimente** : N/A
- **Alimenté par** : Electrical Panel
- **Contrôlé par** : Escalator Controller, PLC
- **Supervise par** : Building Management System, Monitoring System
- **Interagit avec** : Lighting System (éclairage marches), Fire Alarm System

## Quantité Typique par Bâtiment
- Petit (5 étages) : 0 escalators
- Moyen (15 étages) : 0-4 escalators (lobby/niveaux publics)
- Grand (30+ étages) : 4-12 escalators (zones publiques)

## Sources
- Haystack Project 4.0 - Escalator equipment tagging
- Brick Schema - Escalator class
- EN 115-1:2017 - Safety of escalators and moving walks
- ISO 25745-3 - Energy performance of escalators
