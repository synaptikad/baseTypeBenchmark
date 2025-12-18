# Points de Water Meter (Compteur d'eau)

## Synthèse
- **Total points mesure** : 8
- **Total points commande** : 3
- **Total points état** : 6

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Volume Total | sensor-volume-point | m³ | 0-999999 | 1min | Volume total cumulé |
| Flow Rate | sensor-flow-point | L/min | 0-500 | 10s | Débit instantané |
| Flow Rate Max | sensor-flow-point | L/min | 0-500 | 1h | Débit maximum période |
| Water Temperature | sensor-temp-point | °C | 5-80°C | 1min | Température eau |
| Water Pressure | sensor-pressure-point | bar | 0-16 | 1min | Pression eau |
| Daily Consumption | sensor-volume-point | m³ | 0-1000 | 1h | Consommation journalière |
| Monthly Consumption | sensor-volume-point | m³ | 0-10000 | 24h | Consommation mensuelle |
| Reverse Flow Volume | sensor-volume-point | m³ | 0-1000 | 1h | Volume reflux (si applicable) |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| High Flow Threshold | cmd-sp-point | L/min | 0-500 | Analog | Seuil alarme débit |
| Reset Daily Counter | cmd-point | - | RESET | Binaire | RAZ compteur journalier |
| Valve Control | cmd-point | - | OPEN/CLOSE | Binaire | Vanne télécommandée (si équipé) |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Meter Status | status-point | Enum | OK/WARNING/FAULT | État général |
| Battery Status | status-point | Enum | OK/LOW/CRITICAL | État batterie (si applicable) |
| High Flow Alarm | status-point | Boolean | FALSE/TRUE | Alarme débit élevé |
| Leak Alarm | status-point | Boolean | FALSE/TRUE | Alarme fuite potentielle |
| Reverse Flow Alarm | status-point | Boolean | FALSE/TRUE | Alarme reflux |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | M-Bus |
|-------|---------------|-----------------|-------|
| Volume Total | AI0 | 30001-30002 | VIF_VOLUME |
| Flow Rate | AI1 | 30003 | VIF_VOLUME_FLOW |
| Water Temperature | AI2 | 30004 | VIF_TEMPERATURE |
| Meter Status | MSV0 | 40001 | DIB_STATUS |
| High Flow Alarm | BI0 | 10001 | - |
| Leak Alarm | BI1 | 10002 | - |
| High Flow Threshold | AO0 | 40101 | - |

## Sources
- [EN ISO 4064 Water Meters](https://www.iso.org/)
- [M-Bus Protocol EN 13757](https://m-bus.com/)
- [OIML R 49 Water Meters](https://www.oiml.org/)
