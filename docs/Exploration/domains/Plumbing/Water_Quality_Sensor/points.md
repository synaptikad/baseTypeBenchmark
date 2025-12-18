# Points de Water Quality Sensor (Capteur qualité eau)

## Synthèse
- **Total points mesure** : 10
- **Total points commande** : 4
- **Total points état** : 6

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| pH | sensor-point | pH | 0-14 | 30s | pH de l'eau |
| Conductivity | sensor-point | µS/cm | 0-5000 | 30s | Conductivité |
| Turbidity | sensor-point | NTU | 0-1000 | 1min | Turbidité |
| Chlorine Residual | sensor-point | mg/L | 0-10 | 1min | Chlore résiduel |
| Dissolved Oxygen | sensor-point | mg/L | 0-20 | 1min | Oxygène dissous |
| Temperature | sensor-temp-point | °C | 0-50°C | 30s | Température eau |
| ORP | sensor-point | mV | -1000 à +1000 | 1min | Potentiel redox |
| Total Dissolved Solids | sensor-point | ppm | 0-5000 | 1min | TDS |
| Ammonia | sensor-point | mg/L | 0-50 | 5min | Ammoniac |
| Nitrates | sensor-point | mg/L | 0-100 | 5min | Nitrates |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| pH Low Threshold | cmd-sp-point | pH | 6-8 | Analog | Seuil alarme pH bas |
| pH High Threshold | cmd-sp-point | pH | 6-8 | Analog | Seuil alarme pH haut |
| Chlorine Threshold | cmd-sp-point | mg/L | 0-5 | Analog | Seuil alarme chlore |
| Calibration Trigger | cmd-point | - | TRIGGER | Binaire | Lancement calibration |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Sensor Status | status-point | Enum | OK/WARNING/FAULT | État général |
| pH Alarm | status-point | Boolean | FALSE/TRUE | Alarme pH hors plage |
| Chlorine Alarm | status-point | Boolean | FALSE/TRUE | Alarme chlore hors plage |
| Turbidity Alarm | status-point | Boolean | FALSE/TRUE | Alarme turbidité |
| Calibration Status | status-point | Enum | OK/REQUIRED/IN_PROGRESS | État calibration |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| pH | AI0 | 30001 |
| Conductivity | AI1 | 30002 |
| Turbidity | AI2 | 30003 |
| Chlorine Residual | AI3 | 30004 |
| Temperature | AI4 | 30005 |
| Sensor Status | MSV0 | 40001 |
| pH Alarm | BI0 | 10001 |
| pH Low Threshold | AO0 | 40101 |

## Sources
- [EN ISO 7027 Water Quality - Turbidity](https://www.iso.org/)
- [WHO Drinking Water Guidelines](https://www.who.int/)
- [EN 17294 pH Measurement](https://www.en-standard.eu/)
