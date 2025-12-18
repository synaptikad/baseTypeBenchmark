# Points de Video Scaler (Convertisseur vidéo)

## Synthèse
- **Total points mesure** : 6
- **Total points commande** : 6
- **Total points état** : 5

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Input Resolution | sensor-point | pixels | Various | 1s | Résolution entrée |
| Output Resolution | sensor-point | pixels | Various | 1s | Résolution sortie |
| Input Frame Rate | sensor-point | fps | 0-120 | 1s | FPS entrée |
| Output Frame Rate | sensor-point | fps | 0-120 | 1s | FPS sortie |
| Processing Latency | sensor-point | ms | 0-100 | 1s | Latence traitement |
| Temperature | sensor-temp-point | °C | 0-70°C | 30s | Température interne |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Output Resolution | cmd-sp-point | - | 720p/1080p/4K/8K | Enum | Résolution sortie |
| Output Frame Rate | cmd-sp-point | fps | 24/30/50/60/120 | Enum | FPS sortie |
| Aspect Ratio | cmd-sp-point | - | MAINTAIN/STRETCH/CROP | Enum | Mode aspect ratio |
| Scaling Mode | cmd-sp-point | - | BILINEAR/BICUBIC/LANCZOS | Enum | Mode mise à l'échelle |
| Output Enable | cmd-point | - | ON/OFF | Binaire | Activation sortie |
| Test Pattern | cmd-point | - | ON/OFF | Binaire | Mire test |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Scaler Status | status-point | Enum | OK/FAULT | État général |
| Input Status | status-point | Enum | ACTIVE/NO_SIGNAL/UNSUPPORTED | État entrée |
| Output Status | status-point | Enum | ACTIVE/MUTED | État sortie |
| HDCP Status | status-point | Enum | OK/FAULT | État HDCP |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | RS-232/IP |
|-------|---------------|-----------------|-----------|
| Input Resolution | AI0 | 30001 | GET IN RES |
| Output Resolution | AI1 | 30002 | GET OUT RES |
| Scaler Status | MSV0 | 40001 | GET STATUS |
| Input Status | MSV1 | 40002 | GET INPUT |
| Output Resolution Set | MSV2 | 40003 | SET OUT RES |
| Output Enable | BO0 | 00001 | OUTPUT |

## Sources
- [HDMI 2.1 Specification](https://www.hdmi.org/)
- [DisplayPort Standard](https://www.displayport.org/)
- [VESA Timing Standard](https://vesa.org/)
