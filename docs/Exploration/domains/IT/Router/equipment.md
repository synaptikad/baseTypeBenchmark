# Router

## Identifiant
- **Code** : NET-RTR
- **Haystack** : N/A
- **Brick** : N/A

## Description
Équipement réseau Layer 3 assurant le routage de paquets IP entre différents réseaux et sous-réseaux. Interconnecte les réseaux internes du bâtiment avec l'extérieur (Internet, WAN, MPLS) et gère les politiques de routage.

## Fonction
Assure le routage intelligent du trafic réseau entre segments, sites distants et vers Internet. Implémente les protocoles de routage dynamique (BGP, OSPF, EIGRP), NAT, VPN et QoS. Supervisable via SNMP, NETCONF ou API pour monitoring de performance et disponibilité.

## Variantes Courantes
- **Edge Router** : Routeur de bordure connectant le réseau interne à Internet/WAN
- **Core Router** : Routeur principal du backbone interne haute capacité
- **Branch Router** : Routeur compact pour sites distants et agences
- **VPN Concentrator** : Routeur spécialisé pour terminaison de tunnels VPN
- **Service Router** : Routeur intégrant services (firewall, load balancing, WAN optimization)

## Caractéristiques Techniques Typiques
- Formats : 1U à 4U (datacenter), boîtier compact (branch)
- Débit : 1 Gbps à 400+ Gbps
- Interfaces : Ethernet (RJ45, SFP, QSFP), Serial (WAN legacy)
- Protocoles routage : BGP, OSPF, EIGRP, RIP, IS-IS
- Redondance : dual PSU, dual control plane (chassis haute-disponibilité)
- Management : SNMP, SSH, NETCONF/YANG, REST API
- Consommation : 50W (branch) à 2000W+ (core)

## Localisation Typique
- Salle réseau principale (MDF)
- Datacenter (zone core network)
- DMZ (zone démilitarisée)
- Point de présence opérateur (PoP)
- Branch office (sites distants)

## Relations avec Autres Équipements
- **Alimente** : Routage inter-réseaux, accès Internet, connectivité WAN
- **Alimenté par** : PDU, UPS réseau critique
- **Contrôlé par** : NMS, monitoring centralisé, SDN controller, DCIM
- **Connecté à** : Core switches, firewalls, load balancers, liens WAN/Internet
- **Refroidi par** : Climatisation salle technique

## Quantité Typique par Bâtiment
- Petit (5 étages) : 1-2 routeurs (edge + backup)
- Moyen (15 étages) : 2-4 routeurs (edge redondant + core)
- Grand (30+ étages) : 4-10+ routeurs (multi-sites, redondance géographique)

## Sources
- RFC 2328 (OSPF), RFC 4271 (BGP)
- SNMP monitoring for routers
- NETCONF/YANG data models for routers
- Network management best practices
