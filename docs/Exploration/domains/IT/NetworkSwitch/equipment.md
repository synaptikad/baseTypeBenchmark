# Network Switch

## Identifiant
- **Code** : NET-SWITCH
- **Haystack** : N/A
- **Brick** : N/A

## Description
Équipement réseau assurant la commutation de trames Ethernet au niveau Layer 2 et/ou Layer 3 du modèle OSI. Interconnecte les serveurs, équipements réseau et infrastructure IT avec supervision via SNMP, CLI, ou API REST.

## Fonction
Fournit la connectivité réseau entre équipements IT dans le datacenter ou bâtiment. Gère les VLANs, QoS, routage, agrégation de liens et sécurité réseau. Supervisable pour monitoring de bande passante, erreurs, température, alimentation.

## Variantes Courantes
- **ToR Switch (Top-of-Rack)** : Switch d'accès monté en haut de chaque rack serveur
- **Aggregation/Distribution Switch** : Switch intermédiaire pour agrégation de trafic
- **Core Switch** : Switch principal haute capacité, backbone du réseau datacenter
- **Access Switch** : Switch d'accès pour postes de travail et équipements bâtiment
- **Management Switch** : Switch dédié au réseau de management out-of-band

## Caractéristiques Techniques Typiques
- Formats : 1U (24-48 ports) à 2U-4U (48-128 ports)
- Vitesses ports : 1 GbE, 10 GbE, 25 GbE, 40 GbE, 100 GbE
- Capacité switching : 1 Tbps à 25+ Tbps
- Alimentation redondante (2 PSU)
- Management : SNMP v2/v3, SSH/Telnet, REST API, NETCONF/YANG
- Consommation : 50W (access) à 1000W+ (core)
- Monitoring : température, ventilateurs, alimentation, utilisation CPU/mémoire

## Localisation Typique
- En haut de chaque rack serveur (ToR)
- Salle réseau (Network Operations Center)
- MDF (Main Distribution Frame) et IDF (Intermediate Distribution Frame)
- Datacenter (zones core, aggregation, access)
- Local technique étage

## Relations avec Autres Équipements
- **Alimente** : Connectivité réseau pour serveurs, storage, équipements bâtiment
- **Alimenté par** : PDU, UPS réseau
- **Contrôlé par** : NMS (Network Management System), monitoring SNMP, SDN controller
- **Connecté à** : Servers, storage arrays, autres switches (uplink/downlink), routeurs, firewalls
- **Refroidi par** : Climatisation salle technique, CRAC/CRAH

## Quantité Typique par Bâtiment
- Petit (5 étages) : 5-15 switches (access + distribution)
- Moyen (15 étages) : 20-50 switches (architecture 3-tiers)
- Grand (30+ étages) : 50-200+ switches (multiple datacenters + étages)

## Sources
- SNMP MIB-II standard (RFC 1213)
- IEEE 802.1Q (VLAN), 802.3ad (LACP)
- Network monitoring best practices
- DCIM network discovery protocols (LLDP, CDP)
