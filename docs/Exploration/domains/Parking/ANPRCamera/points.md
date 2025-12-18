# Points de ANPR/LPR Camera

## Synthèse
- **Total points mesure** : 8
- **Total points commande** : 5
- **Total points état** : 9

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Image Quality | sensor-point | % | 0-100% | 5s | Qualité de l'image capturée |
| Recognition Confidence | sensor-point | % | 0-100% | Sur événement | Niveau de confiance de la reconnaissance OCR |
| Processing Time | sensor-point | ms | 50-500 ms | Sur événement | Temps de traitement de reconnaissance |
| Capture Rate | sensor-point | img/min | 0-120 | 1min | Taux de captures d'images |
| CPU Usage | sensor-point | % | 0-100% | 30s | Utilisation processeur embarqué |
| Memory Usage | sensor-point | % | 0-100% | 30s | Utilisation mémoire système |
| Camera Temperature | sensor-temp-point | °C | -40 à +60°C | 1min | Température interne caméra |
| Network Latency | sensor-point | ms | 1-100 ms | 1min | Latence de communication réseau |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| IR Illuminator Enable | cmd-point | - | ON/OFF | Binaire | Activation éclairage infrarouge |
| Focus Adjustment | cmd-point | - | AUTO/MANUAL | Enum | Mode de mise au point |
| Exposure Control | cmd-point | ms | 0.1-100 ms | Analog | Temps d'exposition caméra |
| Recognition Trigger | cmd-point | - | TRIGGER | Binaire | Déclenchement manuel reconnaissance |
| Capture Mode | cmd-point | - | CONTINUOUS/EVENT | Enum | Mode de capture d'images |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Camera Status | status-point | Enum | OK/FAULT/OFFLINE | État général caméra |
| Connection Status | status-point | Enum | CONNECTED/DISCONNECTED | État connexion réseau |
| License Plate Detected | status-point | Boolean | TRUE/FALSE | Plaque détectée dans le champ |
| Last Plate Number | status-point | String | Alphanumeric | Dernière plaque reconnue |
| Recognition Status | status-point | Enum | SUCCESS/FAILED/PROCESSING | État dernière reconnaissance |
| Storage Status | status-point | Enum | OK/FULL/WARNING | État stockage local |
| Lens Contamination | status-point | Enum | CLEAN/DIRTY/BLOCKED | État propreté objectif |
| IR Illuminator Status | status-point | Enum | ON/OFF/FAULT | État éclairage IR |
| Alarm Active | status-point | Boolean | TRUE/FALSE | Alarme technique active |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | ONVIF |
|-------|---------------|-----------------|-------|
| Camera Status | AI0 | 40001 | DeviceMgmt.GetDeviceInformation |
| Image Quality | AI1 | 40002 | Analytics.GetAnalyticsEngines |
| Recognition Confidence | AI2 | 40003 | - |
| Camera Temperature | AI3 | 40004 | DeviceMgmt.GetSystemTemperature |
| IR Illuminator Enable | BO0 | 00001 | Imaging.SetImagingSettings |
| Recognition Trigger | BO1 | 00002 | - |
| License Plate Detected | BI0 | 10001 | Events.PullMessages |
| Connection Status | MSV0 | 40010 | - |

## Sources
- [ONVIF Specifications](https://www.onvif.org/profiles/)
- [LPR/ANPR System Documentation](https://www.parking-net.com/)
