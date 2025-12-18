# SAN Switch (Fibre Channel Switch)

## Identifiant
- **Code** : STOR-SAN-SW
- **Haystack** : N/A
- **Brick** : N/A

## Description
Commutateur Fibre Channel dédié au réseau SAN (Storage Area Network), interconnectant serveurs et baies de stockage avec protocole FC. Assure commutation haute performance et faible latence pour trafic block storage.

## Fonction
Fournit le fabric Fibre Channel reliant serveurs aux storage arrays pour accès block-level. Gère le zoning, routage FC et qualité de service. Supervisable via SNMP, API propriétaires et SMI-S pour monitoring de performance, erreurs et topologie SAN.

## Variantes Courantes
- **Edge Switch (Access)** : Connexion serveurs et petites baies (8-24 ports)
- **Core/Director Switch** : Backbone SAN haute densité (128-768 ports)
- **Top-of-Rack FC Switch** : Switch compact monté dans racks serveurs
- **Multi-protocol Switch** : Support FC + FCoE (Fibre Channel over Ethernet)
- **Gen6/Gen7 Switch** : Dernières générations (32/64 Gbps par port)

## Caractéristiques Techniques Typiques
- Formats : 1U (24-48 ports) à châssis modulaire (256+ ports)
- Vitesses : 8, 16, 32, 64 Gbps Fibre Channel
- Distance : jusqu'à 10-100 km avec optique longue portée
- Latency : < 1 microseconde (port-to-port)
- Redondance : dual PSU, dual management modules
- Management : Web GUI, CLI, SNMP, REST API, SMI-S
- Consommation : 100W à 2000W+ (directors)

## Localisation Typique
- Datacenter (zone SAN fabric)
- Salle serveur principale
- Storage room dédiée
- En haut de racks serveurs (ToR deployment)

## Relations avec Autres Équipements
- **Alimente** : Connectivité SAN serveurs vers storage
- **Alimenté par** : PDU, UPS critique
- **Contrôlé par** : SAN management software, DCIM, monitoring centralisé
- **Connecté à** : Serveurs (via HBA), storage arrays, autres FC switches
- **Refroidi par** : Climatisation précision datacenter

## Quantité Typique par Bâtiment
- Petit (5 étages) : 2-4 switches (fabric A/B redondant)
- Moyen (15 étages) : 4-8 switches (multiple fabrics, edge + core)
- Grand (30+ étages) : 8-20+ switches (large SAN, multi-sites)

## Sources
- Fibre Channel Protocol specifications (FC-PI-6)
- SAN fabric design best practices
- SMI-S monitoring for FC switches
- Zoning and fabric management documentation
