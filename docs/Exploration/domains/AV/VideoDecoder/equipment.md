# Video Decoder

## Identifiant
- **Code** : VIDEO_DEC
- **Haystack** : N/A
- **Brick** : N/A

## Description
Décodeur vidéo pour conversion de flux IP en signaux vidéo physiques (HDMI, SDI). Équipement communicant via IP pour contrôle, monitoring de flux et intégration AV-over-IP.

## Fonction
Conversion de flux réseau (H.264/H.265, RTSP, NDI) en sorties vidéo physiques vers displays et projecteurs. Élément récepteur des systèmes AV-over-IP, permet la distribution vidéo sur infrastructure réseau Ethernet. Décodage de streams distants, visioconférence cloud, digital signage réseau.

## Variantes Courantes
- **HDMI Decoder** : Décodage stream vers sortie HDMI
- **SDI Decoder** : Décodage vers 3G-SDI pour environnements broadcast
- **NDI Decoder** : Réception NDI pour production vidéo over IP
- **4K Decoder** : Support 4K60 decoding HEVC
- **Multi-Stream Decoder** : Décodage simultané de plusieurs streams (mosaic)

## Caractéristiques Techniques Typiques
- Sorties : HDMI, 3G-SDI, DisplayPort
- Codecs : H.264, H.265/HEVC, MJPEG, NDI, JPEG2000
- Résolution : 1080p60, 4K30, 4K60 selon modèle
- Streaming : RTSP, RTMP, HLS, SRT, NDI, RTP, multicast
- Latency : 50ms (ultra-low) à 500ms (standard)
- Contrôle : HTTP API, SNMP, Telnet
- Audio : De-embedding vers HDMI, analog audio output
- Network : GbE Ethernet, PoE+ option
- Buffering : Adaptive pour stabilité réseau
- Multicast : Support IGMP pour efficient distribution

## Localisation Typique
- Proximité displays (faux-plafond, rack salle)
- Locaux techniques AV distribués
- Command centers
- Digital signage endpoints
- Récepteurs AV-over-IP

## Relations avec Autres Équipements
- **Alimente** : Display, Projector, AV Matrix Switcher, Video Wall Controller
- **Alimenté par** : Video Encoder, Streaming Server, Media Server, IP cameras
- **Contrôlé par** : AV Control Processor
- **Connecté via** : Network switch, AV over IP infrastructure

## Quantité Typique par Bâtiment
- Petit (5 étages) : 5-15 decoders
- Moyen (15 étages) : 20-60 decoders
- Grand (30+ étages) : 80-200 decoders

## Sources
- H.264/H.265 decoding specifications
- AV-over-IP system architecture (SDVoE, Dante AV)
- IP streaming protocols documentation
