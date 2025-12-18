# Points de Microwave Detector (Détecteur micro-onde)

## Synthèse
- **Total points mesure** : 4
- **Total points commande** : 3
- **Total points état** : 5

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Signal Level | sensor-point | % | 0-100% | 100ms | Niveau signal |
| Doppler Shift | sensor-point | Hz | 0-500 | 100ms | Décalage Doppler |
| Detection Count | sensor-point | count | 0-99999 | Sur événement | Compteur détections |
| Operating Hours | sensor-point | h | 0-99999 | 1h | Heures fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Sensitivity | cmd-sp-point | - | LOW/MEDIUM/HIGH | Enum | Sensibilité |
| Range | cmd-sp-point | m | 5-30 | Analog | Portée détection |
| LED Enable | cmd-point | - | ON/OFF | Binaire | Activation LED |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Detector Status | status-point | Enum | OK/ALARM/FAULT | État général |
| Alarm Status | status-point | Boolean | FALSE/TRUE | Alarme active |
| Direction | status-point | Enum | TOWARD/AWAY/CROSSING | Direction mouvement |
| Tamper Status | status-point | Boolean | FALSE/TRUE | Sabotage détecté |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | SIA Protocol |
|-------|---------------|-----------------|--------------|
| Signal Level | AI0 | 30001 | - |
| Doppler Shift | AI1 | 30002 | - |
| Detector Status | MSV0 | 40001 | Zone Status |
| Alarm Status | BI0 | 10001 | Event BA |
| Sensitivity | MSV1 | 40002 | Config |

## Sources
- [EN 50131-2-5 Microwave Detectors](https://www.en-standard.eu/)
- [FCC Part 15 Radio Frequency](https://www.fcc.gov/)
