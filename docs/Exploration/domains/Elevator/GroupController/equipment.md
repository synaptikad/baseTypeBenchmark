# Group Controller

## Identifiant
- **Code** : GRP_CTRL
- **Haystack** : elev + group + controller + equip
- **Brick** : brick:Elevator_Group_Controller (subclass of brick:Controller)

## Description
Contrôleur central coordonnant plusieurs ascenseurs travaillant ensemble en groupe. Optimise la répartition des appels pour minimiser les temps d'attente et la consommation énergétique. Intelligence collective des ascenseurs.

## Fonction
Coordonner de 2 à 8 ascenseurs en un groupe cohérent, répartir intelligemment les appels d'étage, minimiser le temps d'attente moyen, équilibrer l'usure des équipements, optimiser la consommation énergétique.

## Variantes Courantes
- **Contrôleur duplex** : Coordination de 2 ascenseurs
- **Contrôleur triplex/quadruplex** : 3-4 ascenseurs
- **Contrôleur large groupe** : 5-8 ascenseurs
- **Contrôleur zoné** : Gestion par zones d'étages (sky lobbies)
- **Contrôleur adaptatif** : Apprentissage des flux de trafic

## Caractéristiques Techniques Typiques
- Processeur multi-cœurs haute performance
- Algorithmes d'optimisation avancés
- Analyse trafic en temps réel
- Modes adaptatifs (matin, midi, soir, weekend)
- Gestion priorités (VIP, pompiers, urgence)
- Protocoles : BACnet/IP, Modbus TCP, Ethernet/IP
- Redondance processeur critique

## Localisation Typique
- Salle des machines principale
- Local technique central ascenseurs
- Armoire technique au rez-de-chaussée
- Intégré dans Elevator Monitoring System

## Relations avec Autres Équipements
- **Alimente** : N/A
- **Alimenté par** : Electrical Panel, UPS
- **Contrôlé par** : Destination Dispatch System (si présent)
- **Supervise par** : Elevator Monitoring System, BMS
- **Contrôle** : Elevator Controllers (du groupe)
- **Reçoit données de** : Hall Call Stations, Load Weighing Devices

## Quantité Typique par Bâtiment
- Petit (5 étages) : 0-1 contrôleur (si 2+ ascenseurs groupés)
- Moyen (15 étages) : 1-2 contrôleurs (groupes de 4-6 ascenseurs)
- Grand (30+ étages) : 2-6 contrôleurs (plusieurs groupes/zones)

## Sources
- Haystack Project 4.0 - Controller and group control tagging
- Brick Schema - Controller hierarchies
- ISO 8100-20 - Energy calculation for lifts (group efficiency)
- Elevator dispatching algorithms research
