# Points de DHW Tank (Ballon eau chaude sanitaire)

## Synthèse
- **Total points mesure** : 10
- **Total points commande** : 5
- **Total points état** : 8

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Tank Top Temperature | sensor-temp-point | °C | 40-80°C | 30s | Température haut de ballon |
| Tank Middle Temperature | sensor-temp-point | °C | 40-75°C | 30s | Température milieu ballon |
| Tank Bottom Temperature | sensor-temp-point | °C | 30-60°C | 30s | Température bas de ballon |
| Supply Temperature | sensor-temp-point | °C | 40-65°C | 30s | Température départ ECS |
| Return Temperature | sensor-temp-point | °C | 35-55°C | 30s | Température retour bouclage |
| Flow Rate | sensor-flow-point | L/min | 0-100 | 10s | Débit soutirage |
| Tank Pressure | sensor-pressure-point | bar | 0-10 | 1min | Pression ballon |
| Energy Stored | sensor-point | kWh | 0-500 | 5min | Énergie stockée |
| Volume | sensor-volume-point | L | 0-5000 | 1h | Volume ballon |
| Heating Power | sensor-elec-power-point | kW | 0-50 | 1min | Puissance chauffage |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Temperature Setpoint | cmd-sp-point | °C | 50-70°C | Analog | Consigne température |
| Heating Enable | cmd-point | - | ENABLE/DISABLE | Binaire | Activation chauffage |
| Legionella Cycle | cmd-point | - | TRIGGER | Binaire | Cycle anti-légionelle |
| Eco Mode | cmd-point | - | ENABLE/DISABLE | Binaire | Mode économique |
| Schedule Enable | cmd-point | - | ENABLE/DISABLE | Binaire | Programmation horaire |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Tank Status | status-point | Enum | HEATING/STANDBY/OFF/FAULT | État général |
| Heating Status | status-point | Enum | OFF/PRIMARY/BACKUP | Source chauffage |
| Legionella Status | status-point | Enum | OK/REQUIRED/IN_PROGRESS | État anti-légionelle |
| Anode Status | status-point | Enum | OK/WORN/REPLACE | État anode sacrificielle |
| Safety Valve Status | status-point | Enum | OK/OPEN/FAULT | État soupape sécurité |
| High Temperature Alarm | status-point | Boolean | FALSE/TRUE | Alarme haute température |
| Low Temperature Alarm | status-point | Boolean | FALSE/TRUE | Alarme basse température |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| Tank Top Temperature | AI0 | 30001 |
| Tank Bottom Temperature | AI1 | 30002 |
| Supply Temperature | AI2 | 30003 |
| Tank Status | MSV0 | 40001 |
| Temperature Setpoint | AO0 | 40101 |
| Heating Enable | BO0 | 00001 |
| Legionella Status | MSV1 | 40010 |

## Sources
- [EN 12897 Water Heaters](https://www.en-standard.eu/)
- [Legionella Prevention Guidelines](https://www.who.int/)
- [ASHRAE 90.1 Water Heating](https://www.ashrae.org/)
