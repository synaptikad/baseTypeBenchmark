# Points de Dual Tech Detector (Détecteur bi-technologie)

## Synthèse
- **Total points mesure** : 4
- **Total points commande** : 3
- **Total points état** : 5

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| PIR Signal Level | sensor-point | % | 0-100% | 100ms | Niveau signal PIR |
| Microwave Signal Level | sensor-point | % | 0-100% | 100ms | Niveau signal micro-onde |
| Detection Count | sensor-point | count | 0-99999 | Sur événement | Compteur détections |
| Battery Level | sensor-point | % | 0-100% | 1h | Niveau batterie |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Sensitivity | cmd-sp-point | - | LOW/MEDIUM/HIGH | Enum | Sensibilité |
| Detection Mode | cmd-sp-point | - | AND/OR/PIR_ONLY/MW_ONLY | Enum | Mode détection |
| LED Enable | cmd-point | - | ON/OFF | Binaire | Activation LED |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Detector Status | status-point | Enum | OK/ALARM/FAULT | État général |
| Alarm Status | status-point | Boolean | FALSE/TRUE | Alarme active |
| PIR Status | status-point | Enum | OK/MASKED/FAULT | État PIR |
| Microwave Status | status-point | Enum | OK/FAULT | État micro-onde |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | SIA Protocol |
|-------|---------------|-----------------|--------------|
| PIR Signal Level | AI0 | 30001 | - |
| Microwave Signal Level | AI1 | 30002 | - |
| Detector Status | MSV0 | 40001 | Zone Status |
| Alarm Status | BI0 | 10001 | Event BA |
| Sensitivity | MSV1 | 40002 | Config |

## Sources
- [EN 50131-2-4 Passive Infrared Detectors](https://www.en-standard.eu/)
- [EN 50131-2-5 Microwave Detectors](https://www.en-standard.eu/)
