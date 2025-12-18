# Points de Multi-Sensor Detector (Détecteur multicapteur)

## Synthèse
- **Total points mesure** : 6
- **Total points commande** : 3
- **Total points état** : 6

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Smoke Level | sensor-point | %/m | 0-20 | 1s | Niveau fumée optique |
| Temperature | sensor-temp-point | °C | -10 à +80°C | 5s | Température mesurée |
| CO Level | sensor-point | ppm | 0-500 | 5s | Niveau monoxyde carbone |
| Heat Rate of Rise | sensor-point | °C/min | 0-30 | 5s | Vitesse montée température |
| Combined Risk Index | sensor-point | % | 0-100% | 1s | Indice risque combiné |
| Operating Hours | sensor-point | h | 0-999999 | 1h | Heures fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Sensitivity | cmd-sp-point | - | LOW/MEDIUM/HIGH | Enum | Sensibilité détection |
| Detection Mode | cmd-sp-point | - | SMOKE/HEAT/CO/MULTI | Enum | Mode détection |
| Test Mode | cmd-point | - | ON/OFF | Binaire | Mode test |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Detector Status | status-point | Enum | NORMAL/PRE-ALARM/ALARM/FAULT | État général |
| Smoke Alarm | status-point | Boolean | FALSE/TRUE | Alarme fumée |
| Heat Alarm | status-point | Boolean | FALSE/TRUE | Alarme chaleur |
| CO Alarm | status-point | Boolean | FALSE/TRUE | Alarme CO |
| Dirty Sensor | status-point | Boolean | FALSE/TRUE | Capteur encrassé |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | SIA/CEI Protocol |
|-------|---------------|-----------------|------------------|
| Smoke Level | AI0 | 30001 | Analog 0x30 |
| Temperature | AI1 | 30002 | Analog 0x31 |
| CO Level | AI2 | 30003 | Analog 0x32 |
| Combined Risk Index | AI3 | 30004 | - |
| Detector Status | MSV0 | 40001 | Status 0x00 |
| Smoke Alarm | BI0 | 10001 | Event FA |
| Sensitivity | MSV1 | 40002 | Config 0x40 |

## Sources
- [EN 54-29 Multi-Sensor Detectors](https://www.en-standard.eu/)
- [EN 54-7 Smoke Detectors](https://www.en-standard.eu/)
- [EN 54-5 Heat Detectors](https://www.en-standard.eu/)
- [EN 54-31 CO Detectors](https://www.en-standard.eu/)
