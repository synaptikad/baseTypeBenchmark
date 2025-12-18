# Points de Fire Damper (Clapet coupe-feu)

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
| Reset Command | cmd-point | - | TRIGGER | Binaire | Ordre réarmement |
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
| Reset Command | BO1 | 00002 |

## Sources
- [EN 15650 Fire Dampers](https://www.en-standard.eu/)
- [EN 1366-2 Fire Resistance Tests](https://www.en-standard.eu/)
- [UL 555 Fire Dampers](https://www.ul.com/)
