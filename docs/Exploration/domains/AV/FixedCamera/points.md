# Points de Fixed Camera (Caméra fixe)

## Synthèse
- **Total points mesure** : 7
- **Total points commande** : 6
- **Total points état** : 6

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Resolution | sensor-point | MP | 1-8 | Config | Résolution |
| Frame Rate | sensor-point | fps | 1-60 | 1s | Images par seconde |
| Bitrate | sensor-point | Mbps | 0-20 | 1s | Débit flux |
| Light Level | sensor-point | lux | 0-100000 | 1s | Niveau luminosité |
| Exposure | sensor-point | ms | 0-1000 | 1s | Temps exposition |
| Focus Distance | sensor-point | m | 0.1-100 | 1s | Distance mise au point |
| Uptime | sensor-point | h | 0-99999 | 1h | Temps fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Stream Enable | cmd-point | - | ON/OFF | Binaire | Activation flux |
| Resolution Set | cmd-sp-point | - | 720p/1080p/4K | Enum | Configuration résolution |
| Frame Rate Set | cmd-sp-point | fps | 15/25/30/60 | Enum | Configuration FPS |
| Exposure Mode | cmd-sp-point | - | AUTO/MANUAL | Enum | Mode exposition |
| White Balance | cmd-sp-point | - | AUTO/DAYLIGHT/TUNGSTEN | Enum | Balance blancs |
| Focus Mode | cmd-sp-point | - | AUTO/MANUAL | Enum | Mode mise au point |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Camera Status | status-point | Enum | OK/FAULT | État général |
| Stream Status | status-point | Enum | STREAMING/STOPPED/FAULT | État flux |
| Exposure Status | status-point | Enum | OK/OVEREXPOSED/UNDEREXPOSED | État exposition |
| Focus Status | status-point | Enum | FOCUSED/FOCUSING/FAULT | État mise au point |
| Recording Status | status-point | Enum | RECORDING/STOPPED | État enregistrement |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | NDI/SDI |
|-------|---------------|-----------------|---------|
| Frame Rate | AI0 | 30001 | Tally |
| Bitrate | AI1 | 30002 | - |
| Camera Status | MSV0 | 40001 | Status |
| Stream Enable | BO0 | 00001 | Tally |
| Resolution Set | MSV1 | 40002 | Format |
| Exposure Mode | MSV2 | 40003 | - |

## Sources
- [SMPTE ST 2110](https://www.smpte.org/)
- [NDI Protocol](https://www.ndi.tv/)
- [VISCA Protocol](https://pro.sony/)
