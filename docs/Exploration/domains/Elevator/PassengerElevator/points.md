# Points de Passenger Elevator

## Synthèse
- **Total points mesure** : 12
- **Total points commande** : 6
- **Total points état** : 14

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Current Floor | sensor-point | floor | -5 à 100 | Temps réel | Étage actuel de la cabine |
| Car Speed | sensor-point | m/s | 0-10 | 100ms | Vitesse de déplacement |
| Car Load | sensor-point | kg | 0-2500 | 1s | Charge cabine |
| Load Percentage | sensor-point | % | 0-120% | 1s | Pourcentage charge nominale |
| Door Opening Time | sensor-point | s | 1-5 | Sur événement | Temps ouverture portes |
| Motor Temperature | sensor-temp-point | °C | 30-80°C | 1min | Température moteur traction |
| Machine Room Temperature | sensor-temp-point | °C | 15-40°C | 5min | Température local machinerie |
| Drive Current | sensor-elec-current-point | A | 0-500 A | 1s | Courant variateur |
| Energy Consumption | sensor-elec-energy-point | kWh | 0-999999 | 1h | Énergie consommée cumulée |
| Trip Count | sensor-point | count | 0-9999999 | Sur événement | Nombre de voyages total |
| Door Cycles | sensor-point | count | 0-9999999 | Sur événement | Cycles ouverture portes |
| Waiting Time | sensor-point | s | 0-300 | Sur événement | Temps attente usager |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Call Car | cmd-point | floor | -5 à 100 | Analog | Appel cabine à étage |
| Door Control | cmd-point | - | OPEN/CLOSE/HOLD | Enum | Commande portes |
| Operation Mode | cmd-point | - | NORMAL/INSPECTION/FIRE | Enum | Mode opérationnel |
| Out of Service Cmd | cmd-point | - | ENABLE/DISABLE | Binaire | Mise hors service |
| Emergency Stop | cmd-point | - | STOP/RELEASE | Binaire | Arrêt d'urgence |
| Priority Call | cmd-point | floor | -5 à 100 | Analog | Appel prioritaire (pompiers) |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Elevator Status | status-point | Enum | RUNNING/STOPPED/FAULT/MAINTENANCE | État général |
| Motion Status | status-point | Enum | IDLE/MOVING_UP/MOVING_DOWN/LEVELING | État mouvement |
| Door Status | status-point | Enum | OPEN/CLOSED/OPENING/CLOSING/FAULT | État portes cabine |
| Landing Door Status | status-point | Enum | OPEN/CLOSED/FAULT | État portes palières |
| Drive Status | status-point | Enum | OK/WARNING/FAULT | État variateur |
| Safety Chain Status | status-point | Boolean | CLOSED/OPEN | État chaîne sécurités |
| Overload Status | status-point | Boolean | FALSE/TRUE | Surcharge détectée |
| Fire Mode Status | status-point | Enum | INACTIVE/PHASE1/PHASE2 | Mode incendie |
| Emergency Power | status-point | Enum | NORMAL/ON_BACKUP | Alimentation secours |
| Inspection Mode | status-point | Boolean | FALSE/TRUE | Mode inspection |
| Out of Service Status | status-point | Boolean | FALSE/TRUE | Hors service |
| Door Zone | status-point | Boolean | FALSE/TRUE | En zone portes |
| Alarm Active | status-point | Boolean | FALSE/TRUE | Alarme cabine active |
| Communication Status | status-point | Enum | OK/FAULT | État interphone cabine |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| Current Floor | AI0 | 40001 |
| Car Speed | AI1 | 40002 |
| Car Load | AI2 | 40003 |
| Motor Temperature | AI3 | 40004 |
| Elevator Status | MSV0 | 40010 |
| Motion Status | MSV1 | 40011 |
| Door Status | MSV2 | 40012 |
| Call Car | AO0 | 40101 |
| Operation Mode | MSV3 | 40102 |

## Sources
- [EN 81-20/50 Safety Norms](https://www.en-standard.eu/)
- [ASME A17.1 Safety Code](https://www.asme.org/)
- [BACnet Elevator Working Group](https://www.bacnet.org/)
