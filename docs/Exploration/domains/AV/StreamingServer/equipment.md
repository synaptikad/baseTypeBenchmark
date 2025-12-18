# Streaming Server

## Identifiant
- **Code** : STREAM_SRV
- **Haystack** : N/A
- **Brick** : N/A

## Description
Serveur de streaming vidéo pour diffusion live et VOD (Video On Demand) sur réseau corporate. Équipement communicant via API pour gestion de streams, monitoring audience et analytics.

## Fonction
Distribution de flux vidéo live (événements, town halls, formations) ou à la demande vers multiples utilisateurs simultanés. Gestion du transcodage multi-bitrate, CDN interne, authentification utilisateurs, analytics de viewership. Intégration avec systèmes de visioconférence et capture vidéo.

## Variantes Courantes
- **On-Premise Streaming Server** : Serveur physique ou VM interne
- **Cloud Streaming Service** : Solution SaaS avec infrastructure cloud
- **Hybrid Streaming Platform** : Mix local encoding + cloud distribution
- **Enterprise Video Platform** : Plateforme complète avec CMS, search, analytics
- **Live Streaming Appliance** : Hardware dédié pour live events

## Caractéristiques Techniques Typiques
- Protocoles : RTMP, RTSP, HLS, DASH, WebRTC
- Codecs : H.264, H.265, VP9, AV1
- Transcodage : Multi-bitrate adaptive streaming (ABR)
- Résolution : 720p à 4K selon bandwidth
- Concurrent viewers : 100 à 10000+ selon infrastructure
- CDN : Internal CDN avec edge caching
- Contrôle : REST API, GraphQL, admin portal
- Storage : Intégré pour VOD ou NAS/SAN externe
- Authentication : SSO, LDAP, SAML integration
- Analytics : Viewer count, engagement, bandwidth usage
- Latency : 3-30s (HLS), <1s (WebRTC low-latency)

## Localisation Typique
- Data center interne
- Salle serveurs IT
- Cloud infrastructure (hybrid deployments)

## Relations avec Autres Équipements
- **Alimenté par** : Video Encoder, PTZ Camera, Video Conference Codec, Media Server
- **Alimente** : Video Decoder, Client endpoints (PCs, mobiles, displays)
- **Contrôlé par** : Web admin interface, API clients
- **Intégré avec** : Calendar systems, Employee directory, Content Management Systems

## Quantité Typique par Bâtiment
- Petit (5 étages) : 0-1 server
- Moyen (15 étages) : 1-2 servers (+ cloud)
- Grand (30+ étages) : 2-5 servers (+ cloud)

## Sources
- HTTP Live Streaming (HLS) specifications
- RTMP and DASH streaming protocols
- Enterprise video platform architecture documentation
