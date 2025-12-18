# Points de Mixing Valve (Vanne de mélange)

## Synthèse
- **Total points mesure** : 7
- **Total points commande** : 4
- **Total points état** : 6

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Mixed Temperature | sensor-temp-point | °C | 20-70°C | 1s | Température mélange |
| Hot Inlet Temperature | sensor-temp-point | °C | 50-80°C | 5s | Température entrée chaude |
| Cold Inlet Temperature | sensor-temp-point | °C | 5-25°C | 5s | Température entrée froide |
| Valve Position | sensor-point | % | 0-100% | 1s | Position vanne |
| Flow Rate | sensor-flow-point | L/min | 0-200 | 10s | Débit mélangé |
| Actuator Torque | sensor-point | Nm | 0-20 | 5s | Couple actionneur |
| Operating Cycles | sensor-point | count | 0-999999 | Sur événement | Cycles cumulés |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Temperature Setpoint | cmd-sp-point | °C | 30-60°C | Analog | Consigne température |
| Valve Position Setpoint | cmd-sp-point | % | 0-100% | Analog | Consigne position |
| Manual Override | cmd-point | - | ENABLE/DISABLE | Binaire | Mode manuel |
| Scald Protection Enable | cmd-point | - | ENABLE/DISABLE | Binaire | Protection anti-brûlure |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Valve Status | status-point | Enum | OK/REGULATING/FAULT | État général |
| Actuator Status | status-point | Enum | OK/FAULT | État actionneur |
| Scald Protection Active | status-point | Boolean | FALSE/TRUE | Protection active |
| High Temperature Alarm | status-point | Boolean | FALSE/TRUE | Alarme haute température |
| Low Temperature Alarm | status-point | Boolean | FALSE/TRUE | Alarme basse température |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| Mixed Temperature | AI0 | 30001 |
| Hot Inlet Temperature | AI1 | 30002 |
| Cold Inlet Temperature | AI2 | 30003 |
| Valve Position | AI3 | 30004 |
| Temperature Setpoint | AO0 | 40101 |
| Valve Status | MSV0 | 40001 |
| High Temperature Alarm | BI0 | 10001 |

## Sources
- [EN 1111 Thermostatic Mixing Valves](https://www.en-standard.eu/)
- [ASSE 1017 Mixing Valves](https://www.asse-plumbing.org/)
