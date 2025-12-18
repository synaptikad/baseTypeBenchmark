# Points de Dumbwaiter (Monte-charge léger)

## Synthèse
- **Total points mesure** : 7
- **Total points commande** : 4
- **Total points état** : 8

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Current Floor | sensor-point | floor | 0-10 | Temps réel | Étage actuel |
| Car Load | sensor-point | kg | 0-300 | 1s | Charge cabine |
| Load Percentage | sensor-point | % | 0-120% | 1s | Pourcentage charge nominale |
| Motor Temperature | sensor-temp-point | °C | 30-70°C | 1min | Température moteur |
| Trip Count | sensor-point | count | 0-999999 | Sur événement | Voyages cumulés |
| Energy Consumption | sensor-elec-energy-point | kWh | 0-99999 | 1h | Énergie consommée |
| Running Hours | sensor-point | h | 0-999999 | 1h | Heures fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Call Car | cmd-point | floor | 0-10 | Analog | Appel cabine |
| Door Lock | cmd-point | - | LOCK/UNLOCK | Binaire | Verrouillage porte |
| Emergency Stop | cmd-point | - | STOP/RELEASE | Binaire | Arrêt d'urgence |
| Reset Fault | cmd-point | - | RESET | Binaire | Acquittement défaut |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Dumbwaiter Status | status-point | Enum | RUNNING/STOPPED/FAULT | État général |
| Motion Status | status-point | Enum | IDLE/MOVING_UP/MOVING_DOWN | État mouvement |
| Door Status | status-point | Enum | OPEN/CLOSED/LOCKED | État porte |
| Landing Door Status | status-point | Enum | ALL_CLOSED/OPEN | État portes palières |
| Overload Status | status-point | Boolean | FALSE/TRUE | Surcharge |
| Safety Chain | status-point | Boolean | CLOSED/OPEN | Chaîne sécurités |
| Fault Code | status-point | String | Alphanumeric | Code défaut |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| Dumbwaiter Status | MSV0 | 40001 |
| Current Floor | AI0 | 40002 |
| Car Load | AI1 | 40003 |
| Call Car | AO0 | 40101 |
| Door Lock | BO0 | 00001 |
| Emergency Stop | BO1 | 00002 |
| Door Status | MSV1 | 40010 |

## Sources
- [ASME A17.1 Dumbwaiters](https://www.asme.org/)
- [EN 81-3 Service Lifts](https://www.en-standard.eu/)
