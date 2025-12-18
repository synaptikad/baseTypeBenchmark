# Points de Induction Loop Detector

## Synthèse
- **Total points mesure** : 7
- **Total points commande** : 4
- **Total points état** : 6

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Loop Frequency | sensor-point | kHz | 20-200 kHz | 100ms | Fréquence opérationnelle boucle |
| Inductance | sensor-point | µH | 50-500 µH | 100ms | Inductance mesurée boucle |
| Frequency Shift | sensor-point | % | 0-15% | 50ms | Variation fréquence (détection) |
| Detection Count | sensor-point | count | 0-999999 | Sur événement | Comptage total détections |
| Detection Duration | sensor-point | s | 0-600 s | Sur événement | Durée présence véhicule |
| Sensitivity Level | sensor-point | - | 1-9 | Sur demande | Niveau de sensibilité détecteur |
| Loop Resistance | sensor-point | Ω | 0-100 Ω | 1min | Résistance boucle (diagnostic) |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Detection Enable | cmd-point | - | ENABLE/DISABLE | Binaire | Activation/désactivation détection |
| Sensitivity Adjust | cmd-sp-point | - | 1-9 | Analog | Ajustement sensibilité |
| Reset Counter | cmd-point | - | RESET | Binaire | Remise à zéro compteur |
| Detection Mode | cmd-point | - | PULSE/PRESENCE | Enum | Mode de détection |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Detector Status | status-point | Enum | OK/FAULT/OFFLINE | État général détecteur |
| Vehicle Present | status-point | Boolean | TRUE/FALSE | Présence véhicule sur boucle |
| Loop Fault | status-point | Enum | OK/OPEN/SHORT/CROSSTALK | État boucle inductive |
| Detection Output | status-point | Boolean | TRUE/FALSE | Sortie relais détection |
| Calibration Status | status-point | Enum | OK/REQUIRED/IN_PROGRESS | État calibration |
| Last Detection Time | status-point | Timestamp | ISO8601 | Horodatage dernière détection |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| Detector Status | MSV0 | 40001 |
| Vehicle Present | BI0 | 10001 |
| Loop Frequency | AI0 | 40002 |
| Frequency Shift | AI1 | 40003 |
| Detection Count | AI2 | 40004-40005 |
| Detection Enable | BO0 | 00001 |
| Sensitivity Adjust | AO0 | 40101 |
| Loop Fault | MSV1 | 40011 |

## Sources
- [ASTM E2563 Standard](https://www.astm.org/)
- [Inductive Loop Detector Specifications](https://www.trafficdetection.com/)
