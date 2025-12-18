# Points de Moving Walkway (Tapis roulant)

## Synthèse
- **Total points mesure** : 9
- **Total points commande** : 5
- **Total points état** : 10

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Belt Speed | sensor-point | m/s | 0-0.75 | 100ms | Vitesse du tapis |
| Motor Current | sensor-elec-current-point | A | 0-100 A | 1s | Courant moteur |
| Motor Temperature | sensor-temp-point | °C | 30-80°C | 1min | Température moteur |
| Handrail Speed | sensor-point | m/s | 0-0.75 | 100ms | Vitesse main courante |
| Running Hours | sensor-point | h | 0-999999 | 1h | Heures fonctionnement |
| Passenger Count | sensor-point | count | 0-9999999 | Sur événement | Passagers cumulés |
| Energy Consumption | sensor-elec-energy-point | kWh | 0-999999 | 1h | Énergie consommée |
| Power Consumption | sensor-elec-power-point | kW | 0-30 kW | 1min | Puissance instantanée |
| Belt Tension | sensor-point | % | 0-100% | 1min | Tension tapis |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Run Command | cmd-point | - | FORWARD/REVERSE/STOP | Enum | Direction/arrêt |
| Speed Mode | cmd-point | - | NORMAL/SLOW/STANDBY | Enum | Mode vitesse |
| Emergency Stop | cmd-point | - | STOP/RELEASE | Binaire | Arrêt d'urgence |
| Reset Fault | cmd-point | - | RESET | Binaire | Acquittement défaut |
| Light Control | cmd-point | - | ON/OFF/AUTO | Enum | Éclairage tapis |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Walkway Status | status-point | Enum | RUNNING/STOPPED/FAULT/STANDBY | État général |
| Direction | status-point | Enum | FORWARD/REVERSE/STOPPED | Direction actuelle |
| Safety Chain Status | status-point | Boolean | CLOSED/OPEN | Chaîne sécurités |
| Belt Status | status-point | Enum | OK/SLIP/FAULT | État tapis |
| Handrail Status | status-point | Enum | OK/SLIP/FAULT | État main courante |
| Comb Plate Status | status-point | Enum | OK/FAULT | État peignes |
| Drive Status | status-point | Enum | OK/WARNING/FAULT | État variateur |
| Emergency Stop Active | status-point | Boolean | FALSE/TRUE | Arrêt urgence actif |
| Passenger Present | status-point | Boolean | FALSE/TRUE | Présence passagers |
| Maintenance Required | status-point | Boolean | FALSE/TRUE | Maintenance requise |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| Walkway Status | MSV0 | 40001 |
| Direction | MSV1 | 40002 |
| Belt Speed | AI0 | 40003 |
| Motor Current | AI1 | 40004 |
| Motor Temperature | AI2 | 40005 |
| Run Command | MSV2 | 40101 |
| Speed Mode | MSV3 | 40102 |
| Safety Chain Status | BI0 | 10001 |

## Sources
- [EN 115-1 Moving Walks](https://www.en-standard.eu/)
- [ASME A17.1 Moving Walks](https://www.asme.org/)
