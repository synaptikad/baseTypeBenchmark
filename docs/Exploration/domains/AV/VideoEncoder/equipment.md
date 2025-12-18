# Video Encoder

## Identifiant
- **Code** : VIDEO_ENC
- **Haystack** : N/A
- **Brick** : N/A

## Description
Encodeur vidéo pour conversion de signaux vidéo en flux IP streamable. Équipement communicant via IP pour contrôle d'encodage, monitoring qualité et intégration avec systèmes de distribution.

## Fonction
Conversion de sources vidéo (HDMI, SDI) en flux réseau (H.264/H.265, RTSP, RTMP, NDI) pour distribution IP, streaming, enregistrement distant ou AV-over-IP. Permet le transport vidéo sur réseau Ethernet standard, l'intégration avec systèmes de visioconférence cloud et le broadcasting interne.

## Variantes Courantes
- **HDMI Encoder** : Encodage HDMI vers H.264/H.265 stream
- **SDI Encoder** : Encodage 3G-SDI broadcast vers IP
- **NDI Encoder** : Conversion vers NDI pour production vidéo over IP
- **4K Encoder** : Support 4K60 encoding avec HEVC
- **Low-Latency Encoder** : Latence <100ms pour applications live critiques

## Caractéristiques Techniques Typiques
- Entrées : HDMI, 3G-SDI, DisplayPort, DVI
- Codecs : H.264, H.265/HEVC, MJPEG, NDI, JPEG2000
- Résolution : 1080p60, 4K30, 4K60 selon modèle
- Bitrate : 1-50 Mbps configurable
- Streaming : RTSP, RTMP, HLS, SRT, NDI, RTP
- Latency : 50ms (ultra-low) à 500ms (standard)
- Contrôle : HTTP API, SNMP, Telnet
- Audio : Embedded audio encoding (AAC, MP3, PCM)
- Network : GbE Ethernet, PoE+ option
- Multi-streaming : Simultaneous multiple outputs (RTSP + RTMP + local)

## Localisation Typique
- Locaux techniques AV (racks)
- Salles de visioconférence
- Studios internes
- Auditoriums
- Command centers

## Relations avec Autres Équipements
- **Alimenté par** : PTZ Camera, Fixed Camera, AV Matrix Switcher, Video Conference Codec
- **Alimente** : Streaming Server, Recording Server, Video Decoder, Display (IP stream)
- **Contrôlé par** : AV Control Processor, Media Server
- **Connecté via** : Network switch, AV over IP infrastructure

## Quantité Typique par Bâtiment
- Petit (5 étages) : 2-8 encoders
- Moyen (15 étages) : 10-25 encoders
- Grand (30+ étages) : 30-80 encoders

## Sources
- H.264/H.265 encoding standards
- RTSP and RTMP streaming protocols
- NDI (Network Device Interface) specifications
