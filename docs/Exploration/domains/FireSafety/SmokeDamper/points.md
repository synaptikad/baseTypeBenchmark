# Points de Smoke Damper (Clapet pare-fumée)

## Synthèse
- **Total points mesure** : 3
- **Total points commande** : 3
- **Total points état** : 5

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Position | sensor-point | % | 0-100% | 1s | Position clapet |
| Actuator Current | sensor-point | mA | 0-500 | 10s | Courant actionneur |
| Operating Cycles | sensor-point | count | 0-99999 | Sur événement | Cycles cumulés |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Close Command | cmd-point | - | TRIGGER | Binaire | Ordre fermeture |
| Open Command | cmd-point | - | TRIGGER | Binaire | Ordre ouverture |
| Test Mode | cmd-point | - | ON/OFF | Binaire | Mode test |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Damper Status | status-point | Enum | OPEN/CLOSED/TRANSIT/FAULT | État général |
| Closed Position | status-point | Boolean | FALSE/TRUE | Position fermée |
| Open Position | status-point | Boolean | FALSE/TRUE | Position ouverte |
| Actuator Status | status-point | Enum | OK/FAULT | État actionneur |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| Position | AI0 | 30001 |
| Damper Status | MSV0 | 40001 |
| Closed Position | BI0 | 10001 |
| Open Position | BI1 | 10002 |
| Close Command | BO0 | 00001 |
| Open Command | BO1 | 00002 |

## Sources
- [EN 12101-8 Smoke Control Dampers](https://www.en-standard.eu/)
- [UL 555S Smoke Dampers](https://www.ul.com/)
- [NFPA 92 Smoke Control Systems](https://www.nfpa.org/)
