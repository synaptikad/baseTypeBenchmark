# Points de Service Elevator

## Synthèse
- **Total points mesure** : 10
- **Total points commande** : 6
- **Total points état** : 12

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Current Floor | sensor-point | floor | -5 à 100 | Temps réel | Étage actuel |
| Car Speed | sensor-point | m/s | 0-4 | 100ms | Vitesse déplacement |
| Car Load | sensor-point | kg | 0-3000 | 1s | Charge cabine |
| Load Percentage | sensor-point | % | 0-120% | 1s | Pourcentage charge nominale |
| Motor Temperature | sensor-temp-point | °C | 30-85°C | 1min | Température moteur |
| Drive Current | sensor-elec-current-point | A | 0-600 A | 1s | Courant variateur |
| Energy Consumption | sensor-elec-energy-point | kWh | 0-999999 | 1h | Énergie consommée |
| Trip Count | sensor-point | count | 0-9999999 | Sur événement | Voyages cumulés |
| Door Opening Time | sensor-point | s | 1-5 | Sur événement | Temps ouverture |
| Waiting Time | sensor-point | s | 0-300 | Sur événement | Temps attente |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Call Car | cmd-point | floor | -5 à 100 | Analog | Appel cabine |
| Door Control | cmd-point | - | OPEN/CLOSE/HOLD | Enum | Commande portes |
| Operation Mode | cmd-point | - | NORMAL/INDEPENDENT/SERVICE | Enum | Mode opérationnel |
| Out of Service | cmd-point | - | ENABLE/DISABLE | Binaire | Mise hors service |
| Emergency Stop | cmd-point | - | STOP/RELEASE | Binaire | Arrêt d'urgence |
| Floor Restriction | cmd-point | floors | BITMASK | Binaire | Restriction étages |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Elevator Status | status-point | Enum | RUNNING/STOPPED/FAULT/MAINTENANCE | État général |
| Motion Status | status-point | Enum | IDLE/MOVING_UP/MOVING_DOWN/LEVELING | État mouvement |
| Door Status | status-point | Enum | OPEN/CLOSED/OPENING/CLOSING/FAULT | État portes |
| Drive Status | status-point | Enum | OK/WARNING/FAULT | État variateur |
| Safety Chain | status-point | Boolean | CLOSED/OPEN | Chaîne sécurités |
| Overload Status | status-point | Boolean | FALSE/TRUE | Surcharge |
| Fire Mode | status-point | Enum | INACTIVE/PHASE1/PHASE2 | Mode incendie |
| Independent Mode | status-point | Boolean | FALSE/TRUE | Mode indépendant |
| Out of Service | status-point | Boolean | FALSE/TRUE | Hors service |
| Door Zone | status-point | Boolean | FALSE/TRUE | En zone portes |
| Alarm Active | status-point | Boolean | FALSE/TRUE | Alarme active |
| Key Switch | status-point | Enum | NORMAL/INSPECTION/FIRE/SERVICE | Position clé |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| Elevator Status | MSV0 | 40001 |
| Current Floor | AI0 | 40002 |
| Car Speed | AI1 | 40003 |
| Car Load | AI2 | 40004 |
| Call Car | AO0 | 40101 |
| Door Control | MSV1 | 40102 |
| Operation Mode | MSV2 | 40103 |
| Fire Mode | MSV3 | 40010 |

## Sources
- [EN 81-20/50 Elevator Safety](https://www.en-standard.eu/)
- [ASME A17.1 Service Elevators](https://www.asme.org/)
