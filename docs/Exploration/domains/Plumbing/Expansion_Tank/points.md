# Points de Expansion Tank (Vase d'expansion)

## Synthèse
- **Total points mesure** : 5
- **Total points commande** : 2
- **Total points état** : 5

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| System Pressure | sensor-pressure-point | bar | 0-10 | 10s | Pression système |
| Pre-charge Pressure | sensor-pressure-point | bar | 0-6 | 1h | Pression précharge azote |
| Water Temperature | sensor-temp-point | °C | 10-90°C | 1min | Température eau système |
| Expansion Volume | sensor-volume-point | L | 0-500 | 5min | Volume expansion actuel |
| Operating Hours | sensor-point | h | 0-999999 | 1h | Heures fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| High Pressure Threshold | cmd-sp-point | bar | 2-8 | Analog | Seuil alarme haute |
| Low Pressure Threshold | cmd-sp-point | bar | 0.5-3 | Analog | Seuil alarme basse |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Tank Status | status-point | Enum | OK/WARNING/FAULT | État général |
| Membrane Status | status-point | Enum | OK/LEAK/FAILED | État membrane |
| High Pressure Alarm | status-point | Boolean | FALSE/TRUE | Alarme haute pression |
| Low Pressure Alarm | status-point | Boolean | FALSE/TRUE | Alarme basse pression |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| System Pressure | AI0 | 30001 |
| Pre-charge Pressure | AI1 | 30002 |
| Water Temperature | AI2 | 30003 |
| Tank Status | MSV0 | 40001 |
| High Pressure Alarm | BI0 | 10001 |
| Low Pressure Alarm | BI1 | 10002 |

## Sources
- [EN 13831 Expansion Vessels](https://www.en-standard.eu/)
- [ASME Section VIII Pressure Vessels](https://www.asme.org/)
