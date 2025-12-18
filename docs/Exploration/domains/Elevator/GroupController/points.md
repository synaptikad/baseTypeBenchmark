# Points de Group Controller

## Synthèse
- **Total points mesure** : 10
- **Total points commande** : 6
- **Total points état** : 10

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Average Wait Time | sensor-point | s | 0-300 | 1min | Temps attente moyen |
| Average Travel Time | sensor-point | s | 0-300 | 1min | Temps trajet moyen |
| Hall Call Count | sensor-point | count | 0-1000 | 1min | Appels paliers en attente |
| Car Calls Count | sensor-point | count | 0-1000 | 1min | Appels cabine en attente |
| Traffic Intensity | sensor-point | % | 0-100% | 5min | Intensité trafic |
| Cars Available | sensor-point | count | 0-20 | 1s | Cabines disponibles |
| Cars In Motion | sensor-point | count | 0-20 | 1s | Cabines en mouvement |
| Energy Consumption | sensor-elec-energy-point | kWh | 0-999999 | 1h | Énergie groupe |
| Efficiency Score | sensor-point | % | 0-100% | 15min | Score efficacité algorithme |
| Uptime | sensor-point | h | 0-999999 | 1h | Temps fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Traffic Mode | cmd-point | - | NORMAL/UP_PEAK/DOWN_PEAK/INTERFLOOR | Enum | Mode trafic |
| Car Enable | cmd-point | - | ENABLE/DISABLE | Binaire | Activation cabine (par car) |
| Priority Floor | cmd-sp-point | floor | -5 à 100 | Analog | Étage prioritaire |
| Algorithm Select | cmd-point | - | COLLECTIVE/DESTINATION/AI | Enum | Algorithme dispatch |
| Emergency Recall | cmd-point | floor | -5 à 100 | Analog | Rappel d'urgence |
| Reset Statistics | cmd-point | - | RESET | Binaire | RAZ statistiques |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Group Status | status-point | Enum | OK/DEGRADED/FAULT | État général groupe |
| Car 1 Status | status-point | Enum | AVAILABLE/BUSY/OUT_OF_SERVICE | État cabine 1 |
| Car 2 Status | status-point | Enum | AVAILABLE/BUSY/OUT_OF_SERVICE | État cabine 2 |
| Car N Status | status-point | Enum | AVAILABLE/BUSY/OUT_OF_SERVICE | État cabine N |
| Traffic Mode Active | status-point | Enum | NORMAL/UP_PEAK/DOWN_PEAK/INTERFLOOR | Mode actif |
| Fire Mode Status | status-point | Enum | INACTIVE/PHASE1/PHASE2 | Mode incendie |
| Communication Status | status-point | Enum | ALL_OK/PARTIAL/FAILED | État comm. cabines |
| BMS Connection | status-point | Enum | CONNECTED/DISCONNECTED | État connexion BMS |
| Algorithm Status | status-point | Enum | RUNNING/LEARNING/FAULT | État algorithme |
| Peak Hour Active | status-point | Boolean | FALSE/TRUE | Heure de pointe |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| Group Status | MSV0 | 40001 |
| Average Wait Time | AI0 | 40002 |
| Average Travel Time | AI1 | 40003 |
| Cars Available | AI2 | 40004 |
| Traffic Intensity | AI3 | 40005 |
| Traffic Mode | MSV1 | 40101 |
| Car Enable | BO0-BO7 | 00001-00008 |
| Fire Mode Status | MSV2 | 40010 |

## Sources
- [ASHRAE Guideline 20](https://www.ashrae.org/)
- [ISO 18738 Elevator Traffic](https://www.iso.org/)
- [BACnet Elevator Group](https://www.bacnet.org/)
