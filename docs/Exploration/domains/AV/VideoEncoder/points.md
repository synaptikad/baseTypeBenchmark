# Points de Video Encoder (Encodeur vidéo)

## Synthèse
- **Total points mesure** : 8
- **Total points commande** : 6
- **Total points état** : 6

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Input Resolution | sensor-point | pixels | Various | 1s | Résolution entrée |
| Output Bitrate | sensor-point | Mbps | 0-100 | 1s | Débit sortie |
| Frame Rate | sensor-point | fps | 0-60 | 1s | Images par seconde |
| Encoding Load | sensor-point | % | 0-100% | 1s | Charge encodage |
| Buffer Level | sensor-point | % | 0-100% | 1s | Niveau buffer |
| Temperature | sensor-temp-point | °C | 0-80°C | 30s | Température interne |
| Dropped Frames | sensor-point | count | 0-999999 | 1min | Images perdues |
| Uptime | sensor-point | h | 0-99999 | 1h | Temps fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Encoding Enable | cmd-point | - | ON/OFF | Binaire | Activation encodage |
| Codec Select | cmd-sp-point | - | H.264/H.265/AV1 | Enum | Sélection codec |
| Bitrate Set | cmd-sp-point | Mbps | 1-50 | Analog | Configuration débit |
| Resolution Set | cmd-sp-point | - | 720p/1080p/4K | Enum | Configuration résolution |
| Profile Set | cmd-sp-point | - | 1-10 | Analog | Sélection profil |
| System Reboot | cmd-point | - | TRIGGER | Binaire | Redémarrage |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Encoder Status | status-point | Enum | OK/WARNING/FAULT | État général |
| Encoding Status | status-point | Enum | ENCODING/STOPPED/OVERLOAD | État encodage |
| Input Status | status-point | Enum | ACTIVE/NO_SIGNAL/UNSUPPORTED | État entrée |
| Output Status | status-point | Enum | STREAMING/RECORDING/IDLE | État sortie |
| Quality Status | status-point | Enum | OPTIMAL/DEGRADED/POOR | État qualité |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | NDI/SRT |
|-------|---------------|-----------------|---------|
| Output Bitrate | AI0 | 30001 | Stats |
| Encoding Load | AI1 | 30002 | Stats |
| Encoder Status | MSV0 | 40001 | Status |
| Encoding Status | MSV1 | 40002 | Status |
| Encoding Enable | BO0 | 00001 | Control |
| Bitrate Set | AO0 | 40101 | Config |

## Sources
- [SMPTE ST 2110](https://www.smpte.org/)
- [NDI Protocol](https://www.ndi.tv/)
- [SRT Alliance](https://www.srtalliance.org/)
