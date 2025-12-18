# Points de Heat Detector (Détecteur de chaleur)

## Synthèse
- **Total points mesure** : 3
- **Total points commande** : 2
- **Total points état** : 5

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Temperature | sensor-temp-point | °C | -10 à +80°C | 5s | Température mesurée |
| Rate of Rise | sensor-point | °C/min | 0-30 | 5s | Vitesse montée température |
| Operating Hours | sensor-point | h | 0-999999 | 1h | Heures fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Sensitivity | cmd-sp-point | - | LOW/MEDIUM/HIGH | Enum | Sensibilité détection |
| Test Mode | cmd-point | - | ON/OFF | Binaire | Mode test |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Detector Status | status-point | Enum | NORMAL/ALARM/FAULT | État général |
| Alarm Status | status-point | Boolean | FALSE/TRUE | Alarme active |
| Fixed Temp Alarm | status-point | Boolean | FALSE/TRUE | Alarme température fixe |
| Rate of Rise Alarm | status-point | Boolean | FALSE/TRUE | Alarme vitesse montée |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | SIA/CEI Protocol |
|-------|---------------|-----------------|------------------|
| Temperature | AI0 | 30001 | Analog 0x30 |
| Rate of Rise | AI1 | 30002 | - |
| Detector Status | MSV0 | 40001 | Status 0x00 |
| Alarm Status | BI0 | 10001 | Event FA |
| Sensitivity | MSV1 | 40002 | Config 0x40 |

## Sources
- [EN 54-5 Heat Detectors](https://www.en-standard.eu/)
- [NFPA 72 National Fire Alarm Code](https://www.nfpa.org/)
- [UL 521 Heat Detectors](https://www.ul.com/)
