# Video Management System (VMS)

## Identifiant
- **Code** : VMS
- **Haystack** : vms
- **Brick** : brick:Video_Management_System

## Description
Plateforme logicielle centralisée pour la gestion, le contrôle et l'analyse de multiples sources vidéo (caméras, NVR, DVR). Fournit interface unifiée pour visualisation live, lecture d'enregistrements, gestion d'événements, configuration des caméras, et intégration avec systèmes tiers (contrôle d'accès, alarme, BMS).

## Fonction
Gestion centralisée de l'infrastructure vidéo, visualisation multi-écrans, recherche et export de vidéos, gestion des droits utilisateurs, analytics vidéo, corrélation d'événements, intégration systèmes de sécurité, reporting.

## Variantes Courantes
- **VMS on-premise** : Serveurs dédiés dans le bâtiment
- **VMS cloud/hybride** : Hébergement cloud avec edge recording
- **VMS enterprise** : Multi-sites, milliers de caméras
- **PSIM intégré** : Intégration avec Physical Security Information Management
- **VMS open platform** : Supporte multiples fabricants (ONVIF)
- **VMS embedded** : Intégré dans NVR haut de gamme

## Caractéristiques Techniques Typiques
- Capacité : 10 à 100 000+ caméras
- Architecture : Serveur central + serveurs d'enregistrement distribués
- Base de données : SQL Server, PostgreSQL, MariaDB
- API : REST, SOAP, SDK
- Protocoles : ONVIF, RTSP, propriétaires
- Intégrations : BACnet, Modbus, OPC, SNMP
- Clients : Windows, Web, Mobile (iOS/Android)
- Analytics : Motion, Line crossing, Face recognition, LPR, People counting
- Redondance : Failover, load balancing
- Stockage : SAN, NAS, DAS, Cloud

## Localisation Typique
- Salle serveurs principale
- Centre de contrôle sécurité (SOC)
- Postes opérateurs (clients)
- Data center (pour déploiements cloud)

## Relations avec Autres Équipements
- **Alimente** : N/A
- **Alimenté par** : Server infrastructure, UPS
- **Contrôlé par** : PSIM, Building Management System (intégration)
- **Reçoit de** : IP Camera, NVR, DVR, Video Analytics Server
- **Envoie à** : Client Workstations, Mobile Devices, Alarm Panel
- **Interagit avec** : Access Control System, Intrusion Detection System, Fire Alarm

## Quantité Typique par Bâtiment
- Petit (5 étages) : 1 serveur VMS (ou cloud)
- Moyen (15 étages) : 1-2 serveurs VMS
- Grand (30+ étages) : 2-5 serveurs VMS (architecture distribuée)

## Sources
- ONVIF VMS Specifications
- PSIM Integration Standards
- Brick Schema - Video Management System
