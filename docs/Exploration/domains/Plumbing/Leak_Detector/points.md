# Points de Leak Detector (Détecteur de fuite)

## Synthèse
- **Total points mesure** : 5
- **Total points commande** : 3
- **Total points état** : 6

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Moisture Level | sensor-point | % | 0-100% | 1s | Niveau humidité détecté |
| Leak Detection Count | sensor-point | count | 0-999 | Sur événement | Détections cumulées |
| Cable Length Wet | sensor-point | m | 0-100 | Sur événement | Longueur câble mouillé |
| Sensor Temperature | sensor-temp-point | °C | -10 à +60°C | 1min | Température capteur |
| Battery Voltage | sensor-elec-volt-point | V | 2.5-3.6 V | 1h | Tension batterie (si applicable) |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Alarm Acknowledge | cmd-point | - | ACK | Binaire | Acquittement alarme |
| Sensitivity | cmd-sp-point | - | LOW/MEDIUM/HIGH | Enum | Sensibilité détection |
| Test Mode | cmd-point | - | ENABLE/DISABLE | Binaire | Mode test |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Detector Status | status-point | Enum | OK/ALARM/FAULT | État général |
| Leak Alarm | status-point | Boolean | FALSE/TRUE | Alarme fuite active |
| Leak Location | status-point | String | Zone/Position | Localisation fuite |
| Battery Status | status-point | Enum | OK/LOW/CRITICAL | État batterie |
| Cable Status | status-point | Enum | OK/BREAK/SHORT | État câble détection |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| Detector Status | MSV0 | 40001 |
| Moisture Level | AI0 | 30001 |
| Leak Alarm | BI0 | 10001 |
| Alarm Acknowledge | BO0 | 00001 |
| Battery Status | MSV1 | 40010 |
| Cable Length Wet | AI1 | 30002 |

## Sources
- [EN 54-1 Fire Detection](https://www.en-standard.eu/)
- [FM Approvals Leak Detection](https://www.fmapprovals.com/)
