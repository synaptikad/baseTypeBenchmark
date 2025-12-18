# Points de Temperature Sensor (Capteur de température)

## Synthèse
- **Total points mesure** : 5
- **Total points commande** : 3
- **Total points état** : 5

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Temperature | sensor-temp-point | °C | -40 à +150°C | 1s | Température mesurée |
| Temperature Min | sensor-temp-point | °C | -40 à +150°C | 1h | Température minimum période |
| Temperature Max | sensor-temp-point | °C | -40 à +150°C | 1h | Température maximum période |
| Sensor Resistance | sensor-point | Ω | 0-10000 | 1min | Résistance capteur (RTD) |
| Operating Hours | sensor-point | h | 0-999999 | 1h | Heures fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| High Temperature Threshold | cmd-sp-point | °C | -40 à +150 | Analog | Seuil alarme haute |
| Low Temperature Threshold | cmd-sp-point | °C | -40 à +150 | Analog | Seuil alarme basse |
| Reset Min/Max | cmd-point | - | RESET | Binaire | RAZ min/max |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Sensor Status | status-point | Enum | OK/WARNING/FAULT | État général |
| High Temperature Alarm | status-point | Boolean | FALSE/TRUE | Alarme haute température |
| Low Temperature Alarm | status-point | Boolean | FALSE/TRUE | Alarme basse température |
| Calibration Status | status-point | Enum | OK/REQUIRED | État calibration |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| Temperature | AI0 | 30001 |
| Sensor Status | MSV0 | 40001 |
| High Temperature Alarm | BI0 | 10001 |
| Low Temperature Alarm | BI1 | 10002 |
| High Temperature Threshold | AO0 | 40101 |
| Low Temperature Threshold | AO1 | 40102 |

## Sources
- [IEC 60751 Temperature Sensors](https://webstore.iec.ch/)
- [EN 60584 Thermocouples](https://www.en-standard.eu/)
