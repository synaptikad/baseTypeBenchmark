# Points de Projector (Vidéoprojecteur)

## Synthèse
- **Total points mesure** : 9
- **Total points commande** : 8
- **Total points état** : 8

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Lamp Hours | sensor-point | h | 0-20000 | 1h | Heures lampe/laser |
| Lamp Brightness | sensor-point | % | 0-100% | 1min | Luminosité lampe |
| Filter Hours | sensor-point | h | 0-5000 | 1h | Heures filtre |
| Temperature Intake | sensor-temp-point | °C | 0-50°C | 30s | Température aspiration |
| Temperature Exhaust | sensor-temp-point | °C | 0-80°C | 30s | Température échappement |
| Power Consumption | sensor-power-point | W | 0-2000 | 1min | Consommation |
| Fan Speed | sensor-point | RPM | 0-5000 | 30s | Vitesse ventilateur |
| Input Resolution | sensor-point | pixels | Various | 1s | Résolution entrée |
| Operating Hours | sensor-point | h | 0-99999 | 1h | Heures fonctionnement total |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Power Enable | cmd-point | - | ON/OFF | Binaire | Mise sous tension |
| Input Select | cmd-sp-point | - | HDMI1/HDMI2/DP/HDBaseT | Enum | Sélection entrée |
| Shutter | cmd-point | - | OPEN/CLOSE | Binaire | Obturateur |
| Brightness | cmd-sp-point | % | 0-100% | Analog | Luminosité |
| Contrast | cmd-sp-point | % | 0-100% | Analog | Contraste |
| Lens Zoom | cmd-sp-point | % | 0-100% | Analog | Zoom optique |
| Lens Focus | cmd-sp-point | % | 0-100% | Analog | Mise au point |
| Lamp Mode | cmd-sp-point | - | NORMAL/ECO/LONG_LIFE | Enum | Mode lampe |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Projector Status | status-point | Enum | ON/STANDBY/WARMING/COOLING/FAULT | État général |
| Lamp Status | status-point | Enum | OK/WARNING/END_OF_LIFE | État lampe |
| Filter Status | status-point | Enum | OK/CLEAN_REQUIRED/BLOCKED | État filtre |
| Signal Status | status-point | Enum | ACTIVE/NO_SIGNAL/UNSUPPORTED | État signal |
| Thermal Status | status-point | Enum | OK/WARNING/OVERHEAT | État thermique |
| Shutter Status | status-point | Enum | OPEN/CLOSED | État obturateur |
| Current Input | status-point | Enum | HDMI1/HDMI2/DP/HDBaseT | Entrée active |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | PJLink/RS-232 |
|-------|---------------|-----------------|---------------|
| Lamp Hours | AI0 | 30001 | %1LAMP ? |
| Temperature Intake | AI1 | 30002 | - |
| Projector Status | MSV0 | 40001 | %1POWR ? |
| Lamp Status | MSV1 | 40002 | %1LAMP ? |
| Power Enable | BO0 | 00001 | %1POWR 1/0 |
| Input Select | MSV2 | 40003 | %1INPT |
| Shutter | BO1 | 00002 | %1AVMT |

## Sources
- [PJLink Protocol](https://pjlink.jbmia.or.jp/)
- [AMX/Crestron Control](https://www.crestron.com/)
- [HDBaseT Alliance](https://hdbaset.org/)
