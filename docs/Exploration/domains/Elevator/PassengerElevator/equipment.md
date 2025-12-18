# Passenger Elevator

## Identifiant
- **Code** : PASS_ELEV
- **Haystack** : elev + passenger + equip
- **Brick** : brick:Elevator (subclass of brick:Vertical_Transport_Equipment)

## Description
Ascenseur conçu pour le transport vertical de personnes entre les différents niveaux d'un bâtiment. Équipement communicant intégré au système de gestion du bâtiment pour la supervision, le contrôle et l'optimisation des déplacements.

## Fonction
Assurer le transport vertical des occupants du bâtiment de manière sûre, confortable et efficace. Contribue à la gestion des flux de personnes et à l'accessibilité du bâtiment.

## Variantes Courantes
- **Ascenseur à traction** : Système avec câbles et contrepoids, utilisé pour les bâtiments moyens à hauts
- **Ascenseur hydraulique** : Système à vérin hydraulique, pour bâtiments bas (2-8 étages)
- **Ascenseur sans machinerie** : Machinerie intégrée dans la gaine, gain d'espace
- **Ascenseur haute vitesse** : Pour gratte-ciels (>4 m/s)
- **Ascenseur double cabine** : Deux cabines indépendantes dans une même gaine

## Caractéristiques Techniques Typiques
- Capacité : 630 kg à 2500 kg (8 à 33 personnes)
- Vitesse : 0.5 m/s à 10 m/s selon hauteur du bâtiment
- Nombre d'arrêts : 2 à 100+ étages
- Portes automatiques avec capteurs de présence
- Protocoles : BACnet, Modbus TCP, LON, protocoles propriétaires
- Communication : Ethernet, RS-485, sans fil

## Localisation Typique
- Noyau central du bâtiment
- Hall d'entrée principal
- Zones de circulation verticale
- Près des cages d'escalier

## Relations avec Autres Équipements
- **Alimente** : N/A (équipement de transport)
- **Alimenté par** : Electrical Panel, Emergency Generator
- **Contrôlé par** : Elevator Controller, Group Controller, Destination Dispatch System
- **Supervise par** : Elevator Monitoring System, Building Management System
- **Interagit avec** : Hall Call Station, Car Operating Panel, Access Control System

## Quantité Typique par Bâtiment
- Petit (5 étages) : 1-2 ascenseurs
- Moyen (15 étages) : 4-8 ascenseurs
- Grand (30+ étages) : 12-32 ascenseurs (souvent groupés par zones)

## Sources
- Haystack Project 4.0 - Vertical Transport Equipment tagging
- Brick Schema - Elevator class definition
- EN 81-20:2020 - Safety rules for construction and installation of lifts
- ISO 25745 - Energy performance of lifts and escalators
