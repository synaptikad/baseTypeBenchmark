# Points de Water Heater (Chauffe-eau)

## Synthèse
- **Total points mesure** : 10
- **Total points commande** : 5
- **Total points état** : 8

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Tank Temperature | sensor-temp-point | °C | 40-80°C | 30s | Température réservoir |
| Inlet Temperature | sensor-temp-point | °C | 5-25°C | 30s | Température eau entrée |
| Outlet Temperature | sensor-temp-point | °C | 40-65°C | 30s | Température eau sortie |
| Flow Rate | sensor-flow-point | L/min | 0-50 | 10s | Débit eau chaude |
| Energy Consumption | sensor-elec-energy-point | kWh | 0-999999 | 1h | Énergie consommée |
| Power Consumption | sensor-elec-power-point | kW | 0-30 kW | 1min | Puissance instantanée |
| Tank Pressure | sensor-pressure-point | bar | 0-10 | 1min | Pression réservoir |
| Heating Element Current | sensor-elec-current-point | A | 0-50 A | 30s | Courant élément chauffant |
| Running Hours | sensor-point | h | 0-999999 | 1h | Heures fonctionnement |
| Heating Cycles | sensor-point | count | 0-999999 | Sur événement | Cycles chauffage |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Temperature Setpoint | cmd-sp-point | °C | 40-70°C | Analog | Consigne température |
| Heating Enable | cmd-point | - | ENABLE/DISABLE | Binaire | Activation chauffage |
| Boost Mode | cmd-point | - | ENABLE/DISABLE | Binaire | Mode boost rapide |
| Eco Mode | cmd-point | - | ENABLE/DISABLE | Binaire | Mode économique |
| Schedule Enable | cmd-point | - | ENABLE/DISABLE | Binaire | Programmation horaire |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Heater Status | status-point | Enum | HEATING/STANDBY/OFF/FAULT | État général |
| Heating Element Status | status-point | Enum | OK/FAULT | État résistance |
| Thermostat Status | status-point | Enum | OK/FAULT | État thermostat |
| Legionella Protection | status-point | Enum | OK/REQUIRED/IN_PROGRESS | Protection légionelle |
| Safety Valve Status | status-point | Enum | OK/OPEN/FAULT | État soupape sécurité |
| Anti-Freeze Active | status-point | Boolean | FALSE/TRUE | Protection antigel active |
| High Temperature Alarm | status-point | Boolean | FALSE/TRUE | Alarme haute température |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| Tank Temperature | AI0 | 30001 |
| Outlet Temperature | AI1 | 30002 |
| Temperature Setpoint | AO0 | 40001 |
| Heater Status | MSV0 | 40010 |
| Heating Enable | BO0 | 00001 |
| Energy Consumption | AI2 | 30003-30004 |
| Power Consumption | AI3 | 30005 |
| High Temperature Alarm | BI0 | 10001 |

## Sources
- [EN 89 Water Heaters](https://www.en-standard.eu/)
- [Legionella Prevention Guidelines](https://www.who.int/)
- [BACnet Hot Water Systems](https://www.bacnet.org/)
