# Points de Escalator

## Synthèse
- **Total points mesure** : 10
- **Total points commande** : 5
- **Total points état** : 11

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Step Speed | sensor-point | m/s | 0-0.75 | 100ms | Vitesse des marches |
| Motor Current | sensor-elec-current-point | A | 0-200 A | 1s | Courant moteur |
| Motor Temperature | sensor-temp-point | °C | 30-80°C | 1min | Température moteur |
| Handrail Speed | sensor-point | m/s | 0-0.75 | 100ms | Vitesse main courante |
| Running Hours | sensor-point | h | 0-999999 | 1h | Heures fonctionnement |
| Passenger Count | sensor-point | count | 0-9999999 | Sur événement | Passagers cumulés |
| Energy Consumption | sensor-elec-energy-point | kWh | 0-999999 | 1h | Énergie consommée |
| Power Consumption | sensor-elec-power-point | kW | 0-50 kW | 1min | Puissance instantanée |
| Vibration Level | sensor-point | mm/s | 0-20 | 1s | Niveau vibrations |
| Chain Tension | sensor-point | % | 0-100% | 1min | Tension chaîne |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Run Command | cmd-point | - | UP/DOWN/STOP | Enum | Direction/arrêt |
| Speed Mode | cmd-point | - | NORMAL/SLOW/STANDBY | Enum | Mode vitesse |
| Emergency Stop | cmd-point | - | STOP/RELEASE | Binaire | Arrêt d'urgence |
| Reset Fault | cmd-point | - | RESET | Binaire | Acquittement défaut |
| Light Control | cmd-point | - | ON/OFF/AUTO | Enum | Éclairage marches |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Escalator Status | status-point | Enum | RUNNING/STOPPED/FAULT/STANDBY | État général |
| Direction | status-point | Enum | UP/DOWN/STOPPED | Direction actuelle |
| Safety Chain Status | status-point | Boolean | CLOSED/OPEN | État chaîne sécurités |
| Step Chain Status | status-point | Enum | OK/ELONGATED/FAULT | État chaîne marches |
| Handrail Status | status-point | Enum | OK/SLIP/FAULT | État main courante |
| Comb Plate Status | status-point | Enum | OK/FAULT | État peignes |
| Drive Status | status-point | Enum | OK/WARNING/FAULT | État variateur |
| Brake Status | status-point | Enum | OK/ENGAGED/FAULT | État frein |
| Emergency Stop Active | status-point | Boolean | FALSE/TRUE | Arrêt urgence actif |
| Passenger Present | status-point | Boolean | FALSE/TRUE | Présence passagers |
| Maintenance Required | status-point | Boolean | FALSE/TRUE | Maintenance requise |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| Escalator Status | MSV0 | 40001 |
| Direction | MSV1 | 40002 |
| Step Speed | AI0 | 40003 |
| Motor Current | AI1 | 40004 |
| Motor Temperature | AI2 | 40005 |
| Run Command | MSV2 | 40101 |
| Speed Mode | MSV3 | 40102 |
| Safety Chain Status | BI0 | 10001 |

## Sources
- [EN 115-1 Escalator Safety](https://www.en-standard.eu/)
- [ASME A17.1 Escalators](https://www.asme.org/)
- [BACnet Escalator Objects](https://www.bacnet.org/)
