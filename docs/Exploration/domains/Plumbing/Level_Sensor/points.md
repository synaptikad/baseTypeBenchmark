# Points de Level Sensor (Capteur de niveau)

## Synthèse
- **Total points mesure** : 6
- **Total points commande** : 4
- **Total points état** : 5

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Level | sensor-level-point | % | 0-100% | 1s | Niveau en pourcentage |
| Level Absolute | sensor-level-point | m | 0-20 | 1s | Niveau absolu |
| Volume | sensor-volume-point | L | 0-100000 | 1min | Volume calculé |
| Level Rate of Change | sensor-point | %/h | -100 à +100 | 5min | Vitesse variation niveau |
| Sensor Temperature | sensor-temp-point | °C | -40 à +80°C | 1min | Température capteur |
| Operating Hours | sensor-point | h | 0-999999 | 1h | Heures fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| High Level Threshold | cmd-sp-point | % | 70-100% | Analog | Seuil alarme niveau haut |
| Low Level Threshold | cmd-sp-point | % | 0-30% | Analog | Seuil alarme niveau bas |
| Calibration Offset | cmd-sp-point | mm | -100 à +100 | Analog | Offset calibration |
| Reset Min/Max | cmd-point | - | RESET | Binaire | RAZ min/max |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Sensor Status | status-point | Enum | OK/WARNING/FAULT | État général |
| High Level Alarm | status-point | Boolean | FALSE/TRUE | Alarme niveau haut |
| Low Level Alarm | status-point | Boolean | FALSE/TRUE | Alarme niveau bas |
| Calibration Status | status-point | Enum | OK/REQUIRED | État calibration |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| Level | AI0 | 30001 |
| Level Absolute | AI1 | 30002 |
| Volume | AI2 | 30003-30004 |
| Sensor Status | MSV0 | 40001 |
| High Level Alarm | BI0 | 10001 |
| Low Level Alarm | BI1 | 10002 |
| High Level Threshold | AO0 | 40101 |

## Sources
- [IEC 60770 Level Transmitters](https://webstore.iec.ch/)
- [EN 61010 Safety Requirements](https://www.en-standard.eu/)
