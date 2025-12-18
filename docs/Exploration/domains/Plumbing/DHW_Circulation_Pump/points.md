# Points de DHW Circulation Pump (Pompe de bouclage ECS)

## Synthèse
- **Total points mesure** : 8
- **Total points commande** : 4
- **Total points état** : 7

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Flow Rate | sensor-flow-point | L/min | 0-100 | 10s | Débit bouclage |
| Return Temperature | sensor-temp-point | °C | 35-55°C | 30s | Température retour |
| Motor Current | sensor-elec-current-point | A | 0-5 A | 1s | Courant moteur |
| Motor Speed | sensor-point | RPM | 0-3000 | 1s | Vitesse moteur |
| Power Consumption | sensor-elec-power-point | W | 0-500 | 1min | Puissance |
| Differential Pressure | sensor-pressure-point | mbar | 0-500 | 10s | Différentiel pression |
| Running Hours | sensor-point | h | 0-999999 | 1h | Heures fonctionnement |
| Energy Consumption | sensor-elec-energy-point | kWh | 0-99999 | 1h | Énergie consommée |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Pump Command | cmd-point | - | START/STOP/AUTO | Enum | Commande pompe |
| Speed Setpoint | cmd-sp-point | % | 0-100% | Analog | Consigne vitesse |
| Temperature Setpoint | cmd-sp-point | °C | 45-55°C | Analog | Consigne température retour |
| Schedule Enable | cmd-point | - | ENABLE/DISABLE | Binaire | Programmation horaire |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Pump Status | status-point | Enum | RUNNING/STOPPED/FAULT | État général |
| Motor Status | status-point | Enum | OK/OVERLOAD/FAULT | État moteur |
| Speed Status | status-point | Enum | MIN/NORMAL/MAX | État vitesse |
| Low Temperature Alarm | status-point | Boolean | FALSE/TRUE | Alarme basse température |
| No Flow Alarm | status-point | Boolean | FALSE/TRUE | Alarme absence débit |
| Thermal Overload | status-point | Boolean | FALSE/TRUE | Surcharge thermique |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| Flow Rate | AI0 | 30001 |
| Return Temperature | AI1 | 30002 |
| Motor Current | AI2 | 30003 |
| Pump Status | MSV0 | 40001 |
| Pump Command | MSV1 | 40101 |
| Speed Setpoint | AO0 | 40201 |
| Low Temperature Alarm | BI0 | 10001 |

## Sources
- [EN 16297 Circulators](https://www.en-standard.eu/)
- [ErP Directive 2009/125/EC](https://ec.europa.eu/)
- [Europump Guidelines](https://europump.net/)
