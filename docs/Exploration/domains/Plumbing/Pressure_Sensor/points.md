# Points de Pressure Sensor (Capteur de pression)

## Synthèse
- **Total points mesure** : 5
- **Total points commande** : 3
- **Total points état** : 5

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Pressure | sensor-pressure-point | bar | 0-16 | 1s | Pression mesurée |
| Pressure Min | sensor-pressure-point | bar | 0-16 | 1h | Pression minimum période |
| Pressure Max | sensor-pressure-point | bar | 0-16 | 1h | Pression maximum période |
| Sensor Temperature | sensor-temp-point | °C | -20 à +80°C | 1min | Température capteur |
| Operating Hours | sensor-point | h | 0-999999 | 1h | Heures fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| High Pressure Threshold | cmd-sp-point | bar | 0-16 | Analog | Seuil alarme haute |
| Low Pressure Threshold | cmd-sp-point | bar | 0-16 | Analog | Seuil alarme basse |
| Reset Min/Max | cmd-point | - | RESET | Binaire | RAZ min/max |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Sensor Status | status-point | Enum | OK/WARNING/FAULT | État général |
| High Pressure Alarm | status-point | Boolean | FALSE/TRUE | Alarme haute pression |
| Low Pressure Alarm | status-point | Boolean | FALSE/TRUE | Alarme basse pression |
| Calibration Status | status-point | Enum | OK/REQUIRED | État calibration |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| Pressure | AI0 | 30001 |
| Sensor Status | MSV0 | 40001 |
| High Pressure Alarm | BI0 | 10001 |
| Low Pressure Alarm | BI1 | 10002 |
| High Pressure Threshold | AO0 | 40101 |
| Low Pressure Threshold | AO1 | 40102 |

## Sources
- [IEC 60770 Transmitters](https://webstore.iec.ch/)
- [EN 837 Pressure Gauges](https://www.en-standard.eu/)
