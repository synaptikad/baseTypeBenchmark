# Destination Dispatch System

## Identifiant
- **Code** : DEST_DISPATCH
- **Haystack** : destinationDispatch + system + equip
- **Brick** : brick:Destination_Dispatch_System (subclass of brick:Equipment)

## Description
Système intelligent d'affectation des ascenseurs basé sur la destination finale des passagers. Optimise les trajets en regroupant les passagers allant aux mêmes étages. Interface avancée avec saisie de destination avant embarquement.

## Fonction
Optimiser l'efficacité du groupe d'ascenseurs en assignant les passagers selon leur destination. Réduit le temps d'attente et les arrêts intermédiaires, améliore le flux de personnes aux heures de pointe.

## Variantes Courantes
- **Système hall simple** : Terminaux au rez-de-chaussée uniquement
- **Système tous étages** : Terminaux à chaque niveau
- **Système avec badge** : Intégration contrôle d'accès
- **Système mobile** : Application smartphone pour réservation
- **Système prédictif** : IA anticipant les flux

## Caractéristiques Techniques Typiques
- Terminaux tactiles ou à clavier par zone
- Algorithmes d'optimisation temps réel
- Base de données des trajets et statistiques
- Intégration système de badges/accès
- API pour applications mobiles
- Protocoles : BACnet/IP, Modbus TCP, REST API
- Serveur centralisé avec redondance

## Localisation Typique
- Halls d'ascenseurs à chaque étage
- Lobby principal
- Zones d'accès contrôlé
- Parkings (intégration parcmètres)

## Relations avec Autres Équipements
- **Alimente** : N/A
- **Alimenté par** : Electrical Panel, UPS
- **Contrôlé par** : N/A (système maître)
- **Supervise par** : Building Management System
- **Contrôle** : Group Controller, Elevator Controllers
- **Interagit avec** : Destination Entry Panel, Access Control System, Mobile App Platform

## Quantité Typique par Bâtiment
- Petit (5 étages) : 0 systèmes (non rentable)
- Moyen (15 étages) : 0-1 système (si trafic important)
- Grand (30+ étages) : 1-4 systèmes (zones/tours différentes)

## Sources
- Haystack Project 4.0 - Destination dispatch tagging
- Brick Schema - Advanced elevator control systems
- CIBSE Guide D - Transportation systems in buildings
- Elevator traffic analysis and simulation standards
