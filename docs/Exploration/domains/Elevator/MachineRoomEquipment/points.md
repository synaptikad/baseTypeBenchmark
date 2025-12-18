# Points de Machine Room Equipment

## Synthèse
- **Total points mesure** : 10
- **Total points commande** : 5
- **Total points état** : 8

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Room Temperature | sensor-temp-point | °C | 10-40°C | 1min | Température locale |
| Room Humidity | sensor-humidity-point | %RH | 20-80% | 1min | Humidité locale |
| Motor Temperature | sensor-temp-point | °C | 30-90°C | 1min | Température moteur |
| Controller Temperature | sensor-temp-point | °C | 20-50°C | 1min | Température contrôleur |
| Brake Temperature | sensor-temp-point | °C | 20-80°C | 1min | Température frein |
| Oil Temperature | sensor-temp-point | °C | 20-60°C | 1min | Température huile (hydraulique) |
| Oil Level | sensor-point | % | 0-100% | 5min | Niveau huile |
| Ventilation Flow | sensor-point | m³/h | 0-5000 | 5min | Débit ventilation |
| Power Consumption | sensor-elec-power-point | kW | 0-100 | 1min | Puissance totale |
| Vibration Level | sensor-point | mm/s | 0-20 | 1s | Niveau vibrations |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Ventilation Control | cmd-point | - | ON/OFF/AUTO | Enum | Commande ventilation |
| Heating Control | cmd-point | - | ON/OFF/AUTO | Enum | Commande chauffage |
| Temperature Setpoint | cmd-sp-point | °C | 15-35°C | Analog | Consigne température |
| Lighting Control | cmd-point | - | ON/OFF/AUTO | Enum | Éclairage local |
| Emergency Lighting | cmd-point | - | ON/OFF | Binaire | Éclairage secours |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Room Status | status-point | Enum | OK/WARNING/CRITICAL | État général |
| Ventilation Status | status-point | Enum | OK/FAULT | État ventilation |
| Heating Status | status-point | Enum | OK/FAULT | État chauffage |
| High Temperature Alarm | status-point | Boolean | FALSE/TRUE | Alarme haute temp |
| Low Temperature Alarm | status-point | Boolean | FALSE/TRUE | Alarme basse temp |
| High Humidity Alarm | status-point | Boolean | FALSE/TRUE | Alarme humidité |
| Door Status | status-point | Enum | CLOSED/OPEN | État porte accès |
| Fire Detector Status | status-point | Enum | OK/ALARM/FAULT | État détecteur incendie |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| Room Status | MSV0 | 40001 |
| Room Temperature | AI0 | 40002 |
| Room Humidity | AI1 | 40003 |
| Motor Temperature | AI2 | 40004 |
| Oil Level | AI3 | 40005 |
| Ventilation Control | MSV1 | 40101 |
| Temperature Setpoint | AO0 | 40102 |
| High Temperature Alarm | BI0 | 10001 |

## Sources
- [EN 81-20 Machine Room Requirements](https://www.en-standard.eu/)
- [ASHRAE Guidelines](https://www.ashrae.org/)
- [ISO 4190 Elevator Installations](https://www.iso.org/)
