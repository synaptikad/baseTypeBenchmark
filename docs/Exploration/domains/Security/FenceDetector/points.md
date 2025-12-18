# Points de Fence Detector (Détecteur périmétrique clôture)

## Synthèse
- **Total points mesure** : 5
- **Total points commande** : 3
- **Total points état** : 5

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Vibration Level | sensor-point | % | 0-100% | 100ms | Niveau vibration |
| Tension Level | sensor-point | N | 0-1000 | 1s | Tension câble |
| Zone Length | sensor-point | m | 0-500 | Config | Longueur zone |
| Detection Count | sensor-point | count | 0-99999 | Sur événement | Compteur détections |
| Signal Quality | sensor-point | % | 0-100% | 1min | Qualité signal |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Sensitivity | cmd-sp-point | - | LOW/MEDIUM/HIGH | Enum | Sensibilité |
| Zone Enable | cmd-point | - | ON/OFF | Binaire | Activation zone |
| Calibrate | cmd-point | - | TRIGGER | Binaire | Calibration |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Detector Status | status-point | Enum | OK/ALARM/FAULT | État général |
| Alarm Status | status-point | Boolean | FALSE/TRUE | Alarme active |
| Cable Status | status-point | Enum | OK/CUT/FAULT | État câble |
| Tamper Status | status-point | Boolean | FALSE/TRUE | Sabotage détecté |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | SIA Protocol |
|-------|---------------|-----------------|--------------|
| Vibration Level | AI0 | 30001 | - |
| Tension Level | AI1 | 30002 | - |
| Detector Status | MSV0 | 40001 | Zone Status |
| Alarm Status | BI0 | 10001 | Event BA |
| Tamper Status | BI1 | 10002 | Event TA |

## Sources
- [EN 50131-2 Intrusion Detectors](https://www.en-standard.eu/)
- [PD 6662 Perimeter Protection](https://www.bsigroup.com/)
