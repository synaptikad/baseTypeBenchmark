# Points de PIR Detector (Détecteur infrarouge passif)

## Synthèse
- **Total points mesure** : 4
- **Total points commande** : 3
- **Total points état** : 5

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Signal Level | sensor-point | % | 0-100% | 100ms | Niveau signal |
| Temperature | sensor-temp-point | °C | -10 à +50°C | 1min | Température ambiante |
| Detection Count | sensor-point | count | 0-99999 | Sur événement | Compteur détections |
| Battery Level | sensor-point | % | 0-100% | 1h | Niveau batterie |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Sensitivity | cmd-sp-point | - | LOW/MEDIUM/HIGH | Enum | Sensibilité |
| Pet Immunity | cmd-point | - | ON/OFF | Binaire | Immunité animaux |
| LED Enable | cmd-point | - | ON/OFF | Binaire | Activation LED |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Detector Status | status-point | Enum | OK/ALARM/FAULT | État général |
| Alarm Status | status-point | Boolean | FALSE/TRUE | Alarme active |
| Masked Status | status-point | Boolean | FALSE/TRUE | Détecteur masqué |
| Tamper Status | status-point | Boolean | FALSE/TRUE | Sabotage détecté |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | SIA Protocol |
|-------|---------------|-----------------|--------------|
| Signal Level | AI0 | 30001 | - |
| Temperature | AI1 | 30002 | - |
| Detector Status | MSV0 | 40001 | Zone Status |
| Alarm Status | BI0 | 10001 | Event BA |
| Tamper Status | BI1 | 10002 | Event TA |
| Sensitivity | MSV1 | 40002 | Config |

## Sources
- [EN 50131-2-2 Passive Infrared Detectors](https://www.en-standard.eu/)
- [UL 639 Intrusion Detection Units](https://www.ul.com/)
