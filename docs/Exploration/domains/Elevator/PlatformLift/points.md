# Points de Platform Lift

## Synthèse
- **Total points mesure** : 8
- **Total points commande** : 5
- **Total points état** : 10

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Current Position | sensor-point | mm | 0-5000 | 100ms | Position actuelle |
| Platform Load | sensor-point | kg | 0-500 | 1s | Charge plateforme |
| Load Percentage | sensor-point | % | 0-120% | 1s | Pourcentage charge nominale |
| Motor Temperature | sensor-temp-point | °C | 30-70°C | 1min | Température moteur |
| Hydraulic Pressure | sensor-point | bar | 0-200 | 1s | Pression hydraulique |
| Trip Count | sensor-point | count | 0-999999 | Sur événement | Voyages cumulés |
| Energy Consumption | sensor-elec-energy-point | kWh | 0-99999 | 1h | Énergie consommée |
| Running Hours | sensor-point | h | 0-999999 | 1h | Heures fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Move Up | cmd-point | - | TRIGGER | Binaire | Commande montée |
| Move Down | cmd-point | - | TRIGGER | Binaire | Commande descente |
| Emergency Stop | cmd-point | - | STOP/RELEASE | Binaire | Arrêt d'urgence |
| Gate Unlock | cmd-point | - | UNLOCK | Binaire | Déverrouillage portillon |
| Reset Fault | cmd-point | - | RESET | Binaire | Acquittement défaut |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Lift Status | status-point | Enum | READY/MOVING/FAULT | État général |
| Position Status | status-point | Enum | TOP/BOTTOM/INTERMEDIATE | Position |
| Motion Status | status-point | Enum | IDLE/MOVING_UP/MOVING_DOWN | État mouvement |
| Gate Status | status-point | Enum | OPEN/CLOSED/LOCKED | État portillon |
| Safety Edge Status | status-point | Enum | CLEAR/ACTIVATED | État bord sensible |
| Overload Status | status-point | Boolean | FALSE/TRUE | Surcharge |
| Safety Chain | status-point | Boolean | CLOSED/OPEN | Chaîne sécurités |
| Hydraulic Status | status-point | Enum | OK/LOW_OIL/FAULT | État hydraulique |
| Battery Status | status-point | Enum | OK/LOW/FAULT | État batterie secours |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| Lift Status | MSV0 | 40001 |
| Current Position | AI0 | 40002 |
| Platform Load | AI1 | 40003 |
| Hydraulic Pressure | AI2 | 40004 |
| Move Up | BO0 | 00001 |
| Move Down | BO1 | 00002 |
| Gate Status | MSV1 | 40010 |
| Position Status | MSV2 | 40011 |

## Sources
- [EN 81-41 Platform Lifts](https://www.en-standard.eu/)
- [ASME A18.1 Platform Lifts](https://www.asme.org/)
- [ADA Accessibility Requirements](https://www.ada.gov/)
