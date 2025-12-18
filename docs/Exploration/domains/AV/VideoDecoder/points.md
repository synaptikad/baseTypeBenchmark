# Points de Video Decoder (Décodeur vidéo)

## Synthèse
- **Total points mesure** : 7
- **Total points commande** : 5
- **Total points état** : 6

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Input Bitrate | sensor-point | Mbps | 0-100 | 1s | Débit entrée |
| Output Resolution | sensor-point | pixels | Various | 1s | Résolution sortie |
| Frame Rate | sensor-point | fps | 0-60 | 1s | Images par seconde |
| Buffer Level | sensor-point | % | 0-100% | 1s | Niveau buffer |
| Decode Latency | sensor-point | ms | 0-1000 | 1s | Latence décodage |
| Temperature | sensor-temp-point | °C | 0-80°C | 30s | Température interne |
| Uptime | sensor-point | h | 0-99999 | 1h | Temps fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Stream Select | cmd-sp-point | - | Stream URL | String | Sélection flux |
| Output Format | cmd-sp-point | - | 720p/1080p/4K | Enum | Format sortie |
| Output Enable | cmd-point | - | ON/OFF | Binaire | Activation sortie |
| Aspect Ratio | cmd-sp-point | - | 16:9/4:3/AUTO | Enum | Ratio aspect |
| System Reboot | cmd-point | - | TRIGGER | Binaire | Redémarrage |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Decoder Status | status-point | Enum | OK/WARNING/FAULT | État général |
| Stream Status | status-point | Enum | DECODING/BUFFERING/NO_SIGNAL/ERROR | État flux |
| Input Format | status-point | Enum | H.264/H.265/VP9 | Format entrée |
| Sync Status | status-point | Enum | LOCKED/UNLOCKED | État synchronisation |
| Output Status | status-point | Enum | ACTIVE/MUTED | État sortie |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | TCP/IP |
|-------|---------------|-----------------|--------|
| Input Bitrate | AI0 | 30001 | Query |
| Buffer Level | AI1 | 30002 | Query |
| Decoder Status | MSV0 | 40001 | Query |
| Stream Status | MSV1 | 40002 | Query |
| Stream Select | MSV2 | 40003 | STREAM url |
| Output Enable | BO0 | 00001 | OUTPUT |

## Sources
- [SMPTE ST 2110](https://www.smpte.org/)
- [NDI Protocol](https://www.ndi.tv/)
- [RTSP RFC 7826](https://datatracker.ietf.org/)
