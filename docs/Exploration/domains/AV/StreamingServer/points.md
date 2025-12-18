# Points de Streaming Server (Serveur streaming)

## Synthèse
- **Total points mesure** : 10
- **Total points commande** : 6
- **Total points état** : 7

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Active Streams | sensor-point | count | 0-1000 | 1s | Flux actifs |
| Connected Viewers | sensor-point | count | 0-100000 | 30s | Spectateurs connectés |
| Total Bitrate Out | sensor-point | Gbps | 0-100 | 30s | Débit sortie total |
| CPU Usage | sensor-point | % | 0-100% | 30s | Utilisation CPU |
| Memory Usage | sensor-point | % | 0-100% | 30s | Utilisation mémoire |
| GPU Usage | sensor-point | % | 0-100% | 30s | Utilisation GPU |
| Network Throughput | sensor-point | Gbps | 0-100 | 30s | Débit réseau |
| Encoding Latency | sensor-point | ms | 0-5000 | 1s | Latence encodage |
| Dropped Frames | sensor-point | count | 0-999999 | 1min | Images perdues |
| Uptime | sensor-point | h | 0-99999 | 1h | Temps fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Stream Enable | cmd-point | - | ON/OFF | Binaire | Activation streaming |
| Input Select | cmd-sp-point | - | Input ID | Analog | Sélection entrée |
| Output Profile | cmd-sp-point | - | Profile ID | Analog | Profil sortie |
| Recording Enable | cmd-point | - | ON/OFF | Binaire | Activation enregistrement |
| Transcode Enable | cmd-point | - | ON/OFF | Binaire | Activation transcodage |
| System Restart | cmd-point | - | TRIGGER | Binaire | Redémarrage |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Server Status | status-point | Enum | OK/WARNING/FAULT | État général |
| Stream Status | status-point | Enum | LIVE/STOPPED/ERROR | État flux |
| Input Status | status-point | Enum | ACTIVE/NO_SIGNAL/ERROR | État entrée |
| Encoder Status | status-point | Enum | OK/OVERLOAD/FAULT | État encodeur |
| CDN Status | status-point | Enum | CONNECTED/DISCONNECTED | État CDN |
| GPU Status | status-point | Enum | OK/WARNING/FAULT | État GPU |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | HTTP API |
|-------|---------------|-----------------|----------|
| Active Streams | AI0 | 30001 | /api/streams |
| Connected Viewers | AI1 | 30002 | /api/viewers |
| Total Bitrate Out | AI2 | 30003 | /api/stats |
| Server Status | MSV0 | 40001 | /api/status |
| Stream Status | MSV1 | 40002 | /api/stream |
| Stream Enable | BO0 | 00001 | /api/stream/start |

## Sources
- [RTMP Protocol](https://www.adobe.com/)
- [HLS Specification](https://developer.apple.com/)
- [SRT Alliance](https://www.srtalliance.org/)
- [WebRTC Standard](https://www.w3.org/)
