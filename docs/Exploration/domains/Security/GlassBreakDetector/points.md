# Points de Glass Break Detector (Détecteur bris de glace)

## Synthèse
- **Total points mesure** : 3
- **Total points commande** : 2
- **Total points état** : 4

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Sound Level | sensor-point | dB | 0-120 | 100ms | Niveau sonore |
| Detection Count | sensor-point | count | 0-9999 | Sur événement | Compteur détections |
| Battery Level | sensor-point | % | 0-100% | 1h | Niveau batterie |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Sensitivity | cmd-sp-point | - | LOW/MEDIUM/HIGH | Enum | Sensibilité |
| Test Mode | cmd-point | - | ON/OFF | Binaire | Mode test |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Detector Status | status-point | Enum | OK/ALARM/FAULT | État général |
| Alarm Status | status-point | Boolean | FALSE/TRUE | Alarme active |
| Tamper Status | status-point | Boolean | FALSE/TRUE | Sabotage détecté |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | SIA Protocol |
|-------|---------------|-----------------|--------------|
| Sound Level | AI0 | 30001 | - |
| Detector Status | MSV0 | 40001 | Zone Status |
| Alarm Status | BI0 | 10001 | Event BA |
| Tamper Status | BI1 | 10002 | Event TA |

## Sources
- [EN 50131-2-7-1 Glass Break Detectors](https://www.en-standard.eu/)
- [UL 639 Intrusion Detection Units](https://www.ul.com/)
