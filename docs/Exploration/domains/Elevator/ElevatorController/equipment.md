# Elevator Controller

## Identifiant
- **Code** : ELEV_CTRL
- **Haystack** : elev + controller + equip
- **Brick** : brick:Elevator_Controller (subclass of brick:Controller)

## Description
Automate programmable gérant le fonctionnement d'un ou plusieurs ascenseurs. Contrôle les mouvements, la sécurité, les portes et l'interface avec le système de supervision. Équipement central de l'intelligence embarquée.

## Fonction
Gérer en temps réel tous les aspects du fonctionnement d'un ascenseur : réponse aux appels, contrôle moteur, gestion des portes, surveillance sécurité, communication avec les systèmes de bâtiment.

## Variantes Courantes
- **Contrôleur simple cabine** : Gestion d'un seul ascenseur
- **Contrôleur duplex** : Coordination de 2 ascenseurs
- **Contrôleur de groupe** : Coordination de 3-8 ascenseurs (voir Group Controller)
- **Contrôleur MRL** : Pour ascenseurs sans machinerie dédiée
- **Contrôleur régénératif** : Avec récupération d'énergie

## Caractéristiques Techniques Typiques
- Processeur industriel temps réel
- Mémoire programme et données
- Entrées/sorties : 50 à 200+ I/O selon complexité
- Communication : Ethernet, RS-485, CAN bus
- Protocoles : BACnet/IP, Modbus TCP, LON, OPC UA
- Interface : Écran tactile ou LED + boutons
- Redondance : Processeur backup selon criticité

## Localisation Typique
- Salle des machines (machinerie)
- Local technique en gaine
- Armoire en haut de gaine (MRL)
- Local technique étage

## Relations avec Autres Équipements
- **Alimente** : N/A
- **Alimenté par** : Electrical Panel, UPS
- **Contrôlé par** : Group Controller (si présent)
- **Supervise par** : Elevator Monitoring System, BMS
- **Contrôle** : Elevator Drive, Door Operator, Car Operating Panel, Hall Call Station
- **Reçoit données de** : Position Encoder, Load Weighing Device, Safety Sensors

## Quantité Typique par Bâtiment
- Petit (5 étages) : 1-2 contrôleurs (1 par ascenseur)
- Moyen (15 étages) : 4-8 contrôleurs (1 par ascenseur ou 1 pour 2)
- Grand (30+ étages) : 12-32 contrôleurs (selon architecture)

## Sources
- Haystack Project 4.0 - Controller equipment tagging
- Brick Schema - Elevator_Controller class
- IEC 61131 - Programmable controllers standards
- Building automation integration protocols
