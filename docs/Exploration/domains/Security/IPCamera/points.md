# Points de IP Camera (Caméra IP)

## Synthèse
- **Total points mesure** : 8
- **Total points commande** : 7
- **Total points état** : 7

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Resolution | sensor-point | MP | 1-12 | Config | Résolution image |
| Frame Rate | sensor-point | fps | 1-60 | 1s | Images par seconde |
| Bitrate | sensor-point | Mbps | 0-20 | 1s | Débit flux |
| Light Level | sensor-point | lux | 0-100000 | 1s | Niveau luminosité |
| Compression Ratio | sensor-point | % | 0-100% | 1min | Taux compression |
| Network Bandwidth | sensor-point | Mbps | 0-100 | 30s | Bande passante utilisée |
| Storage Rate | sensor-point | GB/h | 0-50 | 1min | Taux stockage |
| Uptime | sensor-point | h | 0-99999 | 1h | Temps fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Stream Enable | cmd-point | - | ON/OFF | Binaire | Activation flux |
| Recording Enable | cmd-point | - | ON/OFF | Binaire | Activation enregistrement |
| IR Mode | cmd-sp-point | - | AUTO/ON/OFF | Enum | Mode infrarouge |
| Privacy Mask | cmd-point | - | ON/OFF | Binaire | Masque confidentialité |
| PTZ Pan | cmd-sp-point | ° | -180 à +180 | Analog | Position pan |
| PTZ Tilt | cmd-sp-point | ° | -90 à +90 | Analog | Position tilt |
| PTZ Zoom | cmd-sp-point | x | 1-30 | Analog | Niveau zoom |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Camera Status | status-point | Enum | OK/FAULT | État général |
| Stream Status | status-point | Enum | STREAMING/STOPPED/FAULT | État flux |
| Recording Status | status-point | Enum | RECORDING/STOPPED | État enregistrement |
| Motion Detected | status-point | Boolean | FALSE/TRUE | Mouvement détecté |
| IR Status | status-point | Enum | OFF/ON | État infrarouge |
| Tampering Detected | status-point | Boolean | FALSE/TRUE | Sabotage détecté |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | ONVIF |
|-------|---------------|-----------------|-------|
| Frame Rate | AI0 | 30001 | GetVideoSourceConfiguration |
| Bitrate | AI1 | 30002 | GetVideoEncoderConfiguration |
| Camera Status | MSV0 | 40001 | GetDeviceStatus |
| Stream Status | MSV1 | 40002 | GetStreamUri |
| Motion Detected | BI0 | 10001 | RuleEngineEvent |
| Stream Enable | BO0 | 00001 | StartMulticastStreaming |
| PTZ Pan | AO0 | 40101 | AbsoluteMove |

## Sources
- [ONVIF Core Specification](https://www.onvif.org/)
- [EN 62676 Video Surveillance](https://www.en-standard.eu/)
