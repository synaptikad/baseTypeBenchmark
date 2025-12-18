# Wireless LAN Controller

## Identifiant
- **Code** : NET-WLC
- **Haystack** : N/A
- **Brick** : N/A

## Description
Contrôleur centralisé gérant une flotte de points d'accès sans fil. Assure la configuration, monitoring, sécurité et optimisation radio de l'infrastructure Wi-Fi à l'échelle du bâtiment ou campus.

## Fonction
Centralise la gestion de dizaines à milliers d'AP, applique les politiques réseau, gère le roaming transparent, optimise les canaux radio et détecte les intrusions sans fil. Fournit visibilité complète sur l'infrastructure Wi-Fi via dashboard, SNMP et API.

## Variantes Courantes
- **Hardware WLC** : Appliance physique dédiée pour grands déploiements
- **Virtual WLC** : Contrôleur virtualisé sur hyperviseur
- **Cloud WLC** : Solution SaaS hébergée (cloud-managed Wi-Fi)
- **Embedded WLC** : Contrôleur intégré dans switch réseau
- **Mobility Controller** : WLC avancé pour mobilité inter-sites

## Caractéristiques Techniques Typiques
- Formats : 1U à 2U (hardware), VM ou conteneur (software)
- Capacité : gestion de 50 à 10000+ AP
- Débit agrégé : 10 Gbps à 100+ Gbps
- Fonctions : provisioning AP, RF management, rogue AP detection, guest portal
- Redondance : clustering haute disponibilité
- Management : Web GUI, CLI, SNMP, REST API
- Consommation : 100W à 500W (hardware)

## Localisation Typique
- Datacenter
- Salle réseau principale (MDF)
- Infrastructure cloud (pour solutions cloud-managed)
- Salle technique centralisée

## Relations avec Autres Équipements
- **Alimente** : Gestion centralisée infrastructure Wi-Fi
- **Alimenté par** : PDU, UPS
- **Contrôlé par** : NMS, monitoring centralisé, NAC (Network Access Control)
- **Connecté à** : Core switches, wireless access points, authentication servers (RADIUS)
- **Refroidi par** : Climatisation datacenter

## Quantité Typique par Bâtiment
- Petit (5 étages) : 1-2 WLC (primaire + backup)
- Moyen (15 étages) : 2-4 WLC (redondance, segmentation)
- Grand (30+ étages) : 4-10+ WLC (multi-sites, clustering)

## Sources
- CAPWAP protocol (RFC 5415, 5416)
- Wireless LAN controller architecture
- Centralized vs distributed Wi-Fi management
- SNMP monitoring for WLC
