# Points de Motorized Valve (Vanne motorisée)

## Synthèse
- **Total points mesure** : 6
- **Total points commande** : 4
- **Total points état** : 7

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Valve Position | sensor-point | % | 0-100% | 1s | Position vanne (0=fermée) |
| Actuator Torque | sensor-point | Nm | 0-100 | 1s | Couple actionneur |
| Motor Current | sensor-elec-current-point | A | 0-5 A | 1s | Courant moteur |
| Flow Through | sensor-flow-point | L/min | 0-500 | 10s | Débit traversant |
| Water Temperature | sensor-temp-point | °C | 5-80°C | 30s | Température eau |
| Operating Cycles | sensor-point | count | 0-999999 | Sur événement | Cycles cumulés |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Valve Command | cmd-point | - | OPEN/CLOSE/STOP | Enum | Commande ouverture/fermeture |
| Position Setpoint | cmd-sp-point | % | 0-100% | Analog | Consigne position |
| Emergency Close | cmd-point | - | TRIGGER | Binaire | Fermeture urgence |
| Manual Override | cmd-point | - | ENABLE/DISABLE | Binaire | Mode manuel |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Valve Status | status-point | Enum | OK/OPENING/CLOSING/FAULT | État général |
| Position Status | status-point | Enum | OPEN/CLOSED/INTERMEDIATE | Position actuelle |
| Actuator Status | status-point | Enum | OK/OVERLOAD/FAULT | État actionneur |
| End Switch Open | status-point | Boolean | FALSE/TRUE | Fin de course ouvert |
| End Switch Closed | status-point | Boolean | FALSE/TRUE | Fin de course fermé |
| Manual Mode Active | status-point | Boolean | FALSE/TRUE | Mode manuel actif |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| Valve Position | AI0 | 30001 |
| Valve Status | MSV0 | 40001 |
| Valve Command | MSV1 | 40101 |
| Position Setpoint | AO0 | 40201 |
| End Switch Open | BI0 | 10001 |
| End Switch Closed | BI1 | 10002 |
| Emergency Close | BO0 | 00001 |

## Sources
- [EN 1074 Valves](https://www.en-standard.eu/)
- [ISA S75.01 Valve Sizing](https://www.isa.org/)
- [BACnet Valve Objects](https://www.bacnet.org/)
