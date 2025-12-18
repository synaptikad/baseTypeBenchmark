# Wireless Access Point

## Identifiant
- **Code** : NET-WAP
- **Haystack** : N/A
- **Brick** : N/A

## Description
Point d'accès sans fil fournissant la connectivité Wi-Fi pour utilisateurs et équipements IoT dans le bâtiment. Opère selon standards IEEE 802.11 (a/b/g/n/ac/ax) et peut être géré de manière centralisée ou autonome.

## Fonction
Étend le réseau filaire en réseau sans fil pour couvrir les espaces de travail, zones publiques et équipements IoT bâtiment. Supervise la qualité signal, nombre de clients connectés, utilisation bande passante et interférences. Géré via controller Wi-Fi centralisé ou cloud avec monitoring SNMP.

## Variantes Courantes
- **AP indoor** : Point d'accès intérieur pour bureaux, couloirs, espaces communs
- **AP outdoor** : Point d'accès renforcé pour extérieur et conditions difficiles
- **AP haute densité** : Optimisé pour grands rassemblements (auditoriums, stades)
- **AP IoT** : Spécialisé pour équipements IoT bâtiment (capteurs, actuateurs)
- **Mesh AP** : Forme un réseau maillé sans backhaul filaire

## Caractéristiques Techniques Typiques
- Standards : Wi-Fi 5 (802.11ac), Wi-Fi 6 (802.11ax), Wi-Fi 6E, Wi-Fi 7
- Bandes : 2.4 GHz, 5 GHz, 6 GHz (Wi-Fi 6E/7)
- Débit théorique : 300 Mbps à 10+ Gbps
- PoE : alimenté par PoE/PoE+ (15W à 30W) ou PoE++ (60W)
- Portée : 30-50m indoor, 100-300m outdoor
- Management : Controller-based, cloud-managed, ou standalone
- Consommation : 10W à 30W typique

## Localisation Typique
- Plafond bureaux et espaces de travail
- Couloirs et espaces de circulation
- Zones publiques (lobbies, cafétéria)
- Salles de réunion et auditoriums
- Extérieur bâtiment (parkings, terrasses)

## Relations avec Autres Équipements
- **Alimente** : Connectivité Wi-Fi pour postes, smartphones, IoT bâtiment
- **Alimenté par** : PoE switch, PoE injector
- **Contrôlé par** : Wireless LAN Controller (WLC), cloud management, NMS
- **Connecté à** : Access switch via câble Ethernet (backhaul)
- **Refroidi par** : Ventilation naturelle ou locale

## Quantité Typique par Bâtiment
- Petit (5 étages) : 10-30 AP (1 AP tous les 100-150m²)
- Moyen (15 étages) : 50-150 AP
- Grand (30+ étages) : 150-500+ AP (haute densité utilisateurs)

## Sources
- IEEE 802.11 standards documentation
- Wireless LAN design best practices
- SNMP MIBs for wireless access points
- Wi-Fi site survey methodologies
