# Network Video Recorder (NVR)

## Identifiant
- **Code** : NVR
- **Haystack** : nvr
- **Brick** : brick:Video_Server

## Description
Serveur d'enregistrement vidéo en réseau dédié à la réception, au stockage et à la gestion des flux vidéo provenant de caméras IP. Fonctionne sans besoin d'encodage (contrairement au DVR) car reçoit des flux déjà numérisés. Peut gérer de quelques caméras à plusieurs centaines selon le modèle.

## Fonction
Réception et enregistrement des flux vidéo IP, stockage sur disques durs (RAID), lecture et export de vidéos, gestion des événements, interface de visualisation live et playback, intégration avec systèmes tiers via API.

## Variantes Courantes
- **NVR standalone compact** : 4-16 canaux, intégré avec écran
- **NVR rack** : 16-64 canaux, format serveur 19"
- **NVR haute capacité** : 64-256+ canaux, architecture distribuée
- **Hybrid NVR** : Supporte aussi entrées analogiques via encodeurs
- **NVR edge** : Enregistrement déporté sur site distant

## Caractéristiques Techniques Typiques
- Canaux : 4 à 256+ caméras
- Bande passante entrante : 80-400 Mbps
- Stockage : 2TB à 100TB+ (baies RAID 5/6/10)
- Résolution max par canal : 4K, 8K
- Compression : H.264, H.265
- Sorties vidéo : HDMI, VGA, DisplayPort
- Redondance : Dual power supply, RAID, failover
- Protocoles : ONVIF, RTSP, propriétaires
- API : REST, SOAP pour intégration
- Alimentation : 100-240V AC

## Localisation Typique
- Salles serveurs sécurisées
- Locaux techniques
- Centre de sécurité (Security Operations Center)
- Armoires de brassage

## Relations avec Autres Équipements
- **Alimente** : N/A (peut fournir PoE aux caméras si PoE NVR)
- **Alimenté par** : UPS, PDU
- **Contrôlé par** : Video Management System (optionnel)
- **Reçoit de** : IP Camera, Video Encoder
- **Envoie à** : Video Management Server, Client Workstations
- **Synchronisé avec** : Network Time Server (NTP)

## Quantité Typique par Bâtiment
- Petit (5 étages) : 1-2 NVR
- Moyen (15 étages) : 2-5 NVR
- Grand (30+ étages) : 5-15 NVR

## Sources
- ONVIF Recording Control Specification
- Network Video Recorder Standards
- Brick Schema - Video Server Class
