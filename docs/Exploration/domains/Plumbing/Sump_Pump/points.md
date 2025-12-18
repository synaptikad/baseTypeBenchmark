# Points de Sump Pump (Pompe de relevage)

## Synthèse
- **Total points mesure** : 8
- **Total points commande** : 4
- **Total points état** : 8

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Sump Level | sensor-level-point | % | 0-100% | 5s | Niveau puisard |
| Discharge Flow | sensor-flow-point | L/min | 0-500 | 10s | Débit refoulement |
| Motor Current | sensor-elec-current-point | A | 0-30 A | 1s | Courant moteur |
| Motor Temperature | sensor-temp-point | °C | 30-80°C | 1min | Température moteur |
| Power Consumption | sensor-elec-power-point | kW | 0-10 | 1min | Puissance |
| Running Hours | sensor-point | h | 0-999999 | 1h | Heures fonctionnement |
| Start Count | sensor-point | count | 0-999999 | Sur événement | Démarrages cumulés |
| Pump Cycles Today | sensor-point | count | 0-1000 | 1h | Cycles aujourd'hui |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Pump Command | cmd-point | - | START/STOP/AUTO | Enum | Commande pompe |
| Start Level | cmd-sp-point | % | 50-90% | Analog | Niveau démarrage |
| Stop Level | cmd-sp-point | % | 10-40% | Analog | Niveau arrêt |
| High Level Alarm SP | cmd-sp-point | % | 80-100% | Analog | Seuil alarme niveau haut |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Pump Status | status-point | Enum | RUNNING/STOPPED/FAULT | État général |
| Motor Status | status-point | Enum | OK/OVERLOAD/FAULT | État moteur |
| Float Switch Status | status-point | Enum | LOW/NORMAL/HIGH | État flotteur |
| High Level Alarm | status-point | Boolean | FALSE/TRUE | Alarme niveau haut |
| Overflow Alarm | status-point | Boolean | FALSE/TRUE | Alarme débordement |
| Dry Run Protection | status-point | Boolean | FALSE/TRUE | Protection marche à sec |
| Thermal Overload | status-point | Boolean | FALSE/TRUE | Surcharge thermique |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| Sump Level | AI0 | 30001 |
| Motor Current | AI1 | 30002 |
| Pump Status | MSV0 | 40001 |
| Pump Command | MSV1 | 40101 |
| Start Level | AO0 | 40201 |
| Stop Level | AO1 | 40202 |
| High Level Alarm | BI0 | 10001 |

## Sources
- [EN 12050 Lifting Plants](https://www.en-standard.eu/)
- [IEC 60034 Motors](https://webstore.iec.ch/)
