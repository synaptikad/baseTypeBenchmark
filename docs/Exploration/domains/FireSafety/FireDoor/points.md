# Points de Fire Door (Porte coupe-feu)

## Synthèse
- **Total points mesure** : 3
- **Total points commande** : 3
- **Total points état** : 6

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Opening Angle | sensor-point | ° | 0-180 | 1s | Angle ouverture |
| Open Duration | sensor-point | s | 0-3600 | 1s | Durée ouverture |
| Operating Cycles | sensor-point | count | 0-999999 | Sur événement | Cycles cumulés |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Release Command | cmd-point | - | TRIGGER | Binaire | Ordre libération (fermeture) |
| Hold Open | cmd-point | - | ON/OFF | Binaire | Maintien ouvert |
| Test Mode | cmd-point | - | ON/OFF | Binaire | Mode test |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Door Status | status-point | Enum | CLOSED/OPEN/HELD_OPEN/FAULT | État général |
| Closed Contact | status-point | Boolean | FALSE/TRUE | Contact fermé |
| Held Open Status | status-point | Boolean | FALSE/TRUE | Maintenue ouverte |
| Closer Status | status-point | Enum | OK/FAULT | État ferme-porte |
| Obstruction Detected | status-point | Boolean | FALSE/TRUE | Obstacle détecté |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | SIA/CEI Protocol |
|-------|---------------|-----------------|------------------|
| Opening Angle | AI0 | 30001 | - |
| Door Status | MSV0 | 40001 | Status 0x10 |
| Closed Contact | BI0 | 10001 | Status DC |
| Held Open Status | BI1 | 10002 | Status HO |
| Release Command | BO0 | 00001 | Command RL |

## Sources
- [EN 14637 Fire Door Holders](https://www.en-standard.eu/)
- [EN 1154 Door Closers](https://www.en-standard.eu/)
- [NFPA 80 Fire Doors](https://www.nfpa.org/)
