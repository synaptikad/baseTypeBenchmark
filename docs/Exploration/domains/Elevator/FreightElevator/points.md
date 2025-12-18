# Points de Freight Elevator

## Synthèse
- **Total points mesure** : 11
- **Total points commande** : 6
- **Total points état** : 12

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Current Floor | sensor-point | floor | -5 à 50 | Temps réel | Étage actuel |
| Car Speed | sensor-point | m/s | 0-2.5 | 100ms | Vitesse déplacement |
| Car Load | sensor-point | kg | 0-10000 | 1s | Charge cabine |
| Load Percentage | sensor-point | % | 0-120% | 1s | Pourcentage charge nominale |
| Motor Temperature | sensor-temp-point | °C | 30-90°C | 1min | Température moteur |
| Drive Current | sensor-elec-current-point | A | 0-800 A | 1s | Courant variateur |
| Energy Consumption | sensor-elec-energy-point | kWh | 0-999999 | 1h | Énergie consommée |
| Trip Count | sensor-point | count | 0-9999999 | Sur événement | Voyages cumulés |
| Door Cycles | sensor-point | count | 0-9999999 | Sur événement | Cycles portes |
| Platform Level | sensor-point | mm | -50 à +50 | 100ms | Niveau plateforme |
| Hydraulic Pressure | sensor-point | bar | 0-300 | 1s | Pression hydraulique (si applicable) |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Call Car | cmd-point | floor | -5 à 50 | Analog | Appel cabine |
| Door Control | cmd-point | - | OPEN/CLOSE/HOLD | Enum | Commande portes |
| Operation Mode | cmd-point | - | NORMAL/ATTENDANT/INDEPENDENT | Enum | Mode opérationnel |
| Out of Service | cmd-point | - | ENABLE/DISABLE | Binaire | Mise hors service |
| Emergency Stop | cmd-point | - | STOP/RELEASE | Binaire | Arrêt d'urgence |
| Light Curtain Bypass | cmd-point | - | ENABLE/DISABLE | Binaire | Bypass rideau optique |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Elevator Status | status-point | Enum | RUNNING/STOPPED/FAULT/MAINTENANCE | État général |
| Motion Status | status-point | Enum | IDLE/MOVING_UP/MOVING_DOWN/LEVELING | État mouvement |
| Car Door Status | status-point | Enum | OPEN/CLOSED/OPENING/CLOSING/FAULT | Portes cabine |
| Gate Status | status-point | Enum | OPEN/CLOSED/FAULT | Portes palières |
| Overload Status | status-point | Boolean | FALSE/TRUE | Surcharge détectée |
| Drive Status | status-point | Enum | OK/WARNING/FAULT | État variateur |
| Safety Chain | status-point | Boolean | CLOSED/OPEN | Chaîne sécurités |
| Fire Mode | status-point | Enum | INACTIVE/PHASE1/PHASE2 | Mode incendie |
| Attendant Mode | status-point | Boolean | FALSE/TRUE | Mode accompagnateur |
| Light Curtain | status-point | Enum | CLEAR/BLOCKED/FAULT | État rideau optique |
| Alarm Active | status-point | Boolean | FALSE/TRUE | Alarme active |
| Key Switch | status-point | Enum | NORMAL/INSPECTION/FIRE/INDEPENDENT | Position clé |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| Elevator Status | MSV0 | 40001 |
| Current Floor | AI0 | 40002 |
| Car Speed | AI1 | 40003 |
| Car Load | AI2 | 40004 |
| Motor Temperature | AI3 | 40005 |
| Call Car | AO0 | 40101 |
| Door Control | MSV1 | 40102 |
| Fire Mode | MSV2 | 40010 |

## Sources
- [EN 81-20/50 Elevator Safety](https://www.en-standard.eu/)
- [ASME A17.1 Freight Elevators](https://www.asme.org/)
- [OSHA Freight Elevator Requirements](https://www.osha.gov/)
