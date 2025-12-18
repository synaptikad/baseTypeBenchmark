# Points de Stair Lift

## Synthèse
- **Total points mesure** : 7
- **Total points commande** : 4
- **Total points état** : 9

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Current Position | sensor-point | % | 0-100% | 100ms | Position sur rail (0=bas, 100=haut) |
| Seat Load | sensor-point | kg | 0-150 | 1s | Charge siège |
| Motor Current | sensor-elec-current-point | A | 0-20 A | 1s | Courant moteur |
| Battery Voltage | sensor-elec-volt-point | V | 20-30 V | 1min | Tension batterie |
| Trip Count | sensor-point | count | 0-999999 | Sur événement | Voyages cumulés |
| Energy Consumption | sensor-elec-energy-point | kWh | 0-99999 | 1h | Énergie consommée |
| Running Hours | sensor-point | h | 0-999999 | 1h | Heures fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Move Up | cmd-point | - | TRIGGER | Binaire | Commande montée |
| Move Down | cmd-point | - | TRIGGER | Binaire | Commande descente |
| Emergency Stop | cmd-point | - | STOP/RELEASE | Binaire | Arrêt d'urgence |
| Reset Fault | cmd-point | - | RESET | Binaire | Acquittement défaut |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Lift Status | status-point | Enum | READY/MOVING/FAULT/CHARGING | État général |
| Position Status | status-point | Enum | TOP/BOTTOM/INTERMEDIATE | Position |
| Motion Status | status-point | Enum | IDLE/MOVING_UP/MOVING_DOWN | État mouvement |
| Seat Status | status-point | Enum | FOLDED/UNFOLDED | État siège |
| Armrest Status | status-point | Enum | UP/DOWN | État accoudoir |
| Footrest Status | status-point | Enum | FOLDED/UNFOLDED | État repose-pieds |
| Battery Status | status-point | Enum | OK/LOW/CHARGING/FAULT | État batterie |
| Safety Sensors | status-point | Enum | CLEAR/OBSTRUCTED | Capteurs obstacle |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| Lift Status | MSV0 | 40001 |
| Current Position | AI0 | 40002 |
| Seat Load | AI1 | 40003 |
| Battery Voltage | AI2 | 40004 |
| Move Up | BO0 | 00001 |
| Move Down | BO1 | 00002 |
| Position Status | MSV1 | 40010 |
| Battery Status | MSV2 | 40011 |

## Sources
- [EN 81-40 Stair Lifts](https://www.en-standard.eu/)
- [ASME A18.1 Stairway Lifts](https://www.asme.org/)
- [ADA Accessibility Requirements](https://www.ada.gov/)
