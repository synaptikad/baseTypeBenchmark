# Points de Smoke Detector (Détecteur de fumée)

## Synthèse
- **Total points mesure** : 4
- **Total points commande** : 2
- **Total points état** : 5

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Smoke Level | sensor-point | %/m | 0-20 | 1s | Niveau obscurcissement |
| Chamber Value | sensor-point | % | 0-100% | 5s | Valeur chambre optique |
| Drift Compensation | sensor-point | % | 0-50% | 1h | Compensation dérive |
| Operating Hours | sensor-point | h | 0-999999 | 1h | Heures fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Sensitivity | cmd-sp-point | - | LOW/MEDIUM/HIGH | Enum | Sensibilité détection |
| Test Mode | cmd-point | - | ON/OFF | Binaire | Mode test |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Detector Status | status-point | Enum | NORMAL/PRE-ALARM/ALARM/FAULT | État général |
| Alarm Status | status-point | Boolean | FALSE/TRUE | Alarme active |
| Pre-Alarm Status | status-point | Boolean | FALSE/TRUE | Pré-alarme active |
| Dirty Sensor | status-point | Boolean | FALSE/TRUE | Capteur encrassé |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | SIA/CEI Protocol |
|-------|---------------|-----------------|------------------|
| Smoke Level | AI0 | 30001 | Analog 0x30 |
| Chamber Value | AI1 | 30002 | Diagnostic |
| Detector Status | MSV0 | 40001 | Status 0x00 |
| Alarm Status | BI0 | 10001 | Event FA |
| Pre-Alarm Status | BI1 | 10002 | Event PA |
| Sensitivity | MSV1 | 40002 | Config 0x40 |

## Sources
- [EN 54-7 Smoke Detectors](https://www.en-standard.eu/)
- [NFPA 72 National Fire Alarm Code](https://www.nfpa.org/)
- [UL 268 Smoke Detectors](https://www.ul.com/)
