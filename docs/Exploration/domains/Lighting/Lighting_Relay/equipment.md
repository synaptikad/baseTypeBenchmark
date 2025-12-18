# Lighting Relay Module

## Identifiant
- **Code** : LIGHT_RELAY
- **Haystack** : relay, actuator, lighting
- **Brick** : brick:Lighting_Relay, brick:Relay

## Description
Module de commutation électromécanique ou électronique permettant le contrôle marche/arrêt de circuits d'éclairage. Le relais agit comme un interrupteur commandé à distance, permettant l'automatisation de l'éclairage via des systèmes de contrôle, capteurs, ou programmation horaire sans intervention manuelle.

## Fonction
Commuter (ouvrir ou fermer) un ou plusieurs circuits d'éclairage en réponse à des commandes électriques provenant de contrôleurs, capteurs, interrupteurs communicants, ou systèmes de gestion du bâtiment. Isole galvaniquement le circuit de puissance du circuit de contrôle.

## Variantes Courantes
- **Single-Pole Relay** : Commutation simple (1 circuit)
- **Multi-Channel Relay Module** : 4 à 16 relais dans un module
- **Latching Relay** : Bistable, conserve état sans alimentation continue
- **Non-Latching Relay** : Monostable, nécessite alimentation pour maintien d'état
- **Electronic Relay (SSR)** : Solid State Relay sans partie mobile
- **Contactor** : Relais haute puissance pour fortes charges
- **DIN-Rail Relay** : Montage sur rail DIN dans tableau électrique
- **In-Ceiling Relay** : Compact pour montage dans faux-plafond
- **Network Relay** : Communicant BACnet, Modbus, KNX, DALI
- **Wireless Relay** : Contrôle sans fil Zigbee, Z-Wave, EnOcean

## Caractéristiques Techniques Typiques
- Tension de commande: 12-24V DC ou 24-230V AC
- Tension commutée: 120-277V AC ou 12-48V DC
- Courant nominal: 10A à 30A par relais (contacteurs jusqu'à 100A+)
- Nombre de pôles: 1 à 4 pôles
- Type de contact: NO (Normalement Ouvert), NF (Normalement Fermé), ou inverseur
- Durée de vie mécanique: 1-10 millions de cycles
- Durée de vie électrique: 100,000-500,000 cycles (selon charge)
- Temps de commutation: 5-20ms (relais électromécanique), <1ms (SSR)
- Isolation: 4kV minimum entre commande et puissance
- Protection: Suppresseur de surtension, arc électrique
- Communication: DALI, BACnet, Modbus, KNX, relais sec (optionnel)
- Indicateur d'état: LED par canal
- Montage: Rail DIN, encastré, plafond, panneau
- Dissipation thermique: Passive ou ventilée (haute puissance)

## Localisation Typique
- Tableaux électriques et armoires
- Locaux techniques
- Faux-plafond technique
- Près des zones d'éclairage contrôlées
- Gaines techniques
- Salles serveur et télécommunications

## Relations avec Autres Équipements
- **Alimente** : N/A
- **Alimenté par** : Electrical Panel, Lighting Panel, Control Power Supply
- **Contrôlé par** : Lighting Controller, Occupancy Sensor, Photocell, Connected Switch, Time Schedule, Building Automation System
- **Contrôle** : LED Luminaire, Fluorescent Luminaire, groupes de luminaires, circuits d'éclairage

## Quantité Typique par Bâtiment
- Petit (5 étages) : 50-200
- Moyen (15 étages) : 200-800
- Grand (30+ étages) : 800-4,000

## Sources
- Haystack Project - Relay and actuator definitions
- Brick Schema - Relay class
- IEC 61810 - Electromechanical elementary relays
- UL 508 - Industrial control equipment (relay modules)
- Building automation control standards
