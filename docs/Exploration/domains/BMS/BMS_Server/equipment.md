# BMS Server

## Identifiant
- **Code** : BMS-SRV
- **Haystack** : server, bms
- **Brick** : BMS_Server

## Description
Serveur central du système de gestion technique du bâtiment. Point de convergence de toutes les informations provenant des contrôleurs de terrain, héberge le logiciel de supervision, les bases de données temps réel et historiques.

## Fonction
Collecte, stocke et analyse les données de tous les équipements connectés. Fournit l'interface de supervision pour les opérateurs, génère les rapports, gère les alarmes, exécute les stratégies d'optimisation globales et assure l'archivage des données.

## Variantes Courantes
- **On-Premise BMS Server** : Serveur physique sur site
- **Virtualized BMS Server** : Machine virtuelle
- **Cloud BMS Server** : Serveur hébergé dans le cloud
- **Redundant BMS Server** : Architecture redondante haute disponibilité

## Caractéristiques Techniques Typiques
- Serveur Windows/Linux
- Base de données SQL (historisation)
- Logiciel BMS/SCADA
- Interfaces multi-protocoles (BACnet, Modbus, LON, KNX)
- Interface web/client lourd
- Capacité: 10,000 à 100,000+ points
- Redondance possible (actif/standby)

## Localisation Typique
- Salle serveur informatique
- Local technique central
- Datacenter on-premise
- Cloud (hébergement distant)

## Relations avec Autres Équipements
- **Alimente** : Aucun (supervision uniquement)
- **Alimenté par** : Infrastructure IT (UPS)
- **Contrôlé par** : Opérateurs, système de gestion énergétique
- **Communique avec** : Tous DDC, Network Controller, Protocol Gateway, SCADA

## Quantité Typique par Bâtiment
- Petit (5 étages) : 1 BMS-SRV
- Moyen (15 étages) : 1-2 BMS-SRV (avec redondance)
- Grand (30+ étages) : 2-4 BMS-SRV (architecture distribuée)

## Sources
- Haystack Project - System and server modeling
- Brick Schema - Building management systems
- BACnet Operator Workstation specifications
