# Points de Pressure Reducing Valve (Réducteur de pression)

## Synthèse
- **Total points mesure** : 6
- **Total points commande** : 3
- **Total points état** : 5

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Inlet Pressure | sensor-pressure-point | bar | 0-16 | 10s | Pression entrée |
| Outlet Pressure | sensor-pressure-point | bar | 0-10 | 10s | Pression sortie |
| Pressure Differential | sensor-point | bar | 0-10 | 10s | Différentiel pression |
| Flow Rate | sensor-flow-point | L/min | 0-500 | 10s | Débit traversant |
| Water Temperature | sensor-temp-point | °C | 5-80°C | 1min | Température eau |
| Valve Position | sensor-point | % | 0-100% | 1s | Position vanne (si motorisé) |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Outlet Pressure Setpoint | cmd-sp-point | bar | 1-6 | Analog | Consigne pression sortie |
| High Pressure Threshold | cmd-sp-point | bar | 1-8 | Analog | Seuil alarme haute |
| Low Pressure Threshold | cmd-sp-point | bar | 0.5-4 | Analog | Seuil alarme basse |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Valve Status | status-point | Enum | OK/FAULT | État général |
| Regulation Status | status-point | Enum | REGULATING/AT_SETPOINT/UNABLE | État régulation |
| High Pressure Alarm | status-point | Boolean | FALSE/TRUE | Alarme haute pression sortie |
| Low Pressure Alarm | status-point | Boolean | FALSE/TRUE | Alarme basse pression sortie |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| Inlet Pressure | AI0 | 30001 |
| Outlet Pressure | AI1 | 30002 |
| Valve Status | MSV0 | 40001 |
| Outlet Pressure Setpoint | AO0 | 40101 |
| High Pressure Alarm | BI0 | 10001 |
| Low Pressure Alarm | BI1 | 10002 |

## Sources
- [EN 1567 Pressure Reducing Valves](https://www.en-standard.eu/)
- [AWWA C511 Pressure Reducing Valves](https://www.awwa.org/)
