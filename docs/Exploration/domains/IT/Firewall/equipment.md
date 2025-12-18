# Firewall

## Identifiant
- **Code** : NET-FW
- **Haystack** : N/A
- **Brick** : N/A

## Description
Équipement de sécurité réseau filtrant le trafic selon des règles définies pour protéger l'infrastructure IT. Analyse les paquets en mode stateful et peut intégrer des fonctions avancées (IPS, antivirus, anti-malware, DLP).

## Fonction
Protège les réseaux internes contre les menaces externes et contrôle les flux entre zones de sécurité (Internet, DMZ, LAN, datacenter). Supervise et logue tout le trafic, détecte les intrusions et applique les politiques de sécurité. Monitoring via SNMP, syslog et API propriétaires.

## Variantes Courantes
- **Firewall périmétrique** : Protection de bordure Internet/WAN
- **Firewall interne** : Segmentation entre zones de sécurité internes
- **Next-Gen Firewall (NGFW)** : Intègre IPS, application control, SSL inspection
- **Firewall virtuel** : Instance virtualisée pour protection micro-segmentation
- **UTM (Unified Threat Management)** : Firewall tout-en-un pour PME

## Caractéristiques Techniques Typiques
- Formats : 1U (SMB) à 4U (datacenter haute capacité)
- Débit : 1 Gbps à 100+ Gbps
- Connexions simultanées : 100K à 50M+ sessions
- Interfaces : 4 à 24+ ports (copper/fiber)
- Redondance : dual PSU, clustering actif/actif ou actif/passif
- Management : Web GUI, CLI, SNMP, REST API, syslog
- Consommation : 100W à 1500W

## Localisation Typique
- DMZ (zone démilitarisée)
- Salle réseau périmétrique
- Datacenter (entrées/sorties sécurisées)
- Entre segments réseau critiques
- Sites distants (branch office)

## Relations avec Autres Équipements
- **Alimente** : Sécurisation du trafic réseau, contrôle d'accès applicatif
- **Alimenté par** : PDU, UPS critique
- **Contrôlé par** : SIEM (Security Information Event Management), NMS, firewall management center
- **Connecté à** : Routeurs (upstream/downstream), switches core, load balancers, IPS/IDS
- **Refroidi par** : Climatisation salle technique

## Quantité Typique par Bâtiment
- Petit (5 étages) : 1-2 firewalls (primaire + backup)
- Moyen (15 étages) : 2-6 firewalls (périmètre + segmentation interne)
- Grand (30+ étages) : 6-20+ firewalls (multi-sites, zones multiples)

## Sources
- Stateful firewall architecture documentation
- NGFW features and capabilities
- SNMP monitoring for security appliances
- Syslog event correlation best practices
