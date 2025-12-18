# Video Conference Codec

## Identifiant
- **Code** : VC_CODEC
- **Haystack** : N/A
- **Brick** : N/A

## Description
Système central de visioconférence assurant l'encodage/décodage vidéo et audio, la gestion d'appels et l'orchestration des périphériques. Équipement hautement communicant via API REST, SNMP, Telnet pour supervision et intégration.

## Fonction
Orchestrateur de la visioconférence : gestion des appels (SIP, H.323, proprietary), traitement audio/vidéo, contrôle des caméras, intégration avec calendriers et plateformes cloud. Point central de supervision et d'analytics pour les salles de réunion.

## Variantes Courantes
- **Room System Codec** : Codec pour salle de réunion, supporte multiple caméras et écrans
- **Personal Codec** : Codec compact pour petites salles ou bureaux individuels
- **Telepresence Codec** : Codec haute-performance pour systèmes immersifs multi-écrans
- **USB Codec** : Codec connect via USB pour BYOD (Bring Your Own Device)
- **Appliance Codec** : Serveur dédié pour large deployment ou MCU

## Caractéristiques Techniques Typiques
- Résolutions supportées : 1080p30/60, 4K30/60 (haut de gamme)
- Protocoles : SIP, H.323, H.320, proprietary (Zoom Rooms, Teams Rooms, WebRTC)
- Codecs vidéo : H.264, H.265/HEVC, VP8, VP9
- Codecs audio : AAC-LD, Opus, G.722, G.711
- Contrôle : API REST, HTTPS, SSH, Telnet, SNMP
- Sorties vidéo : 1-3 HDMI outputs
- Entrées caméra : HDMI, USB, IP (RTSP)
- Audio : Dante, AES67, USB audio, analog I/O
- Réseau : Dual GbE (LAN + AV network), PoE option

## Localisation Typique
- Salles de visioconférence dédiées
- Salles de réunion équipées
- Salles de conseil
- Executive offices
- Espaces collaboration hybrides
- Auditoriums (large-scale events)

## Relations avec Autres Équipements
- **Alimente** : Display, Projector
- **Contrôle** : PTZ Camera, Fixed Camera, Microphone Array
- **Alimenté par** : DSP (audio), Wireless Presentation Gateway (content share)
- **Contrôlé par** : AV Control Processor, Touch Panel Controller, Room Scheduling Display
- **Connecté via** : HDBaseT Extender, USB Extender

## Quantité Typique par Bâtiment
- Petit (5 étages) : 3-8 codecs
- Moyen (15 étages) : 15-35 codecs
- Grand (30+ étages) : 50-100 codecs

## Sources
- SIP/H.323 protocol standards
- Video conferencing API documentation
- Enterprise collaboration platform integration guides
