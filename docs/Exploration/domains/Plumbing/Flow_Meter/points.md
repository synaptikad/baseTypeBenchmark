# Points de Flow Meter (Débitmètre)

## Synthèse
- **Total points mesure** : 7
- **Total points commande** : 3
- **Total points état** : 5

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Flow Rate | sensor-flow-point | L/min | 0-1000 | 1s | Débit instantané |
| Total Volume | sensor-volume-point | m³ | 0-999999 | 1min | Volume total cumulé |
| Velocity | sensor-point | m/s | 0-10 | 1s | Vitesse écoulement |
| Temperature | sensor-temp-point | °C | 0-100°C | 30s | Température fluide |
| Flow Rate Max | sensor-flow-point | L/min | 0-1000 | 1h | Débit maximum période |
| Daily Volume | sensor-volume-point | m³ | 0-1000 | 1h | Volume journalier |
| Reverse Flow | sensor-flow-point | L/min | 0-100 | 10s | Débit inverse |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| High Flow Threshold | cmd-sp-point | L/min | 0-1000 | Analog | Seuil alarme débit haut |
| Low Flow Threshold | cmd-sp-point | L/min | 0-100 | Analog | Seuil alarme débit bas |
| Reset Totalizer | cmd-point | - | RESET | Binaire | RAZ totalisateur |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Meter Status | status-point | Enum | OK/WARNING/FAULT | État général |
| High Flow Alarm | status-point | Boolean | FALSE/TRUE | Alarme débit élevé |
| Low Flow Alarm | status-point | Boolean | FALSE/TRUE | Alarme débit bas |
| Reverse Flow Alarm | status-point | Boolean | FALSE/TRUE | Alarme écoulement inverse |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| Flow Rate | AI0 | 30001 |
| Total Volume | AI1 | 30002-30003 |
| Temperature | AI2 | 30004 |
| Meter Status | MSV0 | 40001 |
| High Flow Alarm | BI0 | 10001 |
| High Flow Threshold | AO0 | 40101 |

## Sources
- [ISO 5167 Flow Measurement](https://www.iso.org/)
- [EN 1434 Heat Meters](https://www.en-standard.eu/)
