# Points de Display (Écran)

## Synthèse
- **Total points mesure** : 7
- **Total points commande** : 7
- **Total points état** : 6

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Brightness | sensor-point | % | 0-100% | 1min | Luminosité actuelle |
| Backlight Hours | sensor-point | h | 0-100000 | 1h | Heures rétroéclairage |
| Temperature | sensor-temp-point | °C | 0-80°C | 30s | Température panneau |
| Power Consumption | sensor-power-point | W | 0-500 | 1min | Consommation |
| Input Resolution | sensor-point | pixels | Various | 1s | Résolution entrée |
| Signal Level | sensor-point | % | 0-100% | 1s | Niveau signal |
| Operating Hours | sensor-point | h | 0-99999 | 1h | Heures fonctionnement total |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Power Enable | cmd-point | - | ON/OFF | Binaire | Mise sous tension |
| Input Select | cmd-sp-point | - | HDMI1/HDMI2/DP/USB-C | Enum | Sélection entrée |
| Brightness Set | cmd-sp-point | % | 0-100% | Analog | Réglage luminosité |
| Contrast | cmd-sp-point | % | 0-100% | Analog | Réglage contraste |
| Volume | cmd-sp-point | % | 0-100% | Analog | Volume haut-parleur |
| Mute | cmd-point | - | ON/OFF | Binaire | Sourdine |
| Picture Mode | cmd-sp-point | - | STANDARD/VIVID/CINEMA | Enum | Mode image |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Display Status | status-point | Enum | ON/STANDBY/OFF/FAULT | État général |
| Signal Status | status-point | Enum | ACTIVE/NO_SIGNAL/UNSUPPORTED | État signal |
| Current Input | status-point | Enum | HDMI1/HDMI2/DP/USB-C | Entrée active |
| Thermal Status | status-point | Enum | OK/WARNING/OVERHEAT | État thermique |
| Panel Status | status-point | Enum | OK/DEGRADED/FAULT | État panneau |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | RS-232/LAN |
|-------|---------------|-----------------|------------|
| Brightness | AI0 | 30001 | Query BRT |
| Temperature | AI1 | 30002 | Query TEMP |
| Display Status | MSV0 | 40001 | Query PWR |
| Power Enable | BO0 | 00001 | PWR ON/OFF |
| Input Select | MSV1 | 40002 | INPUT x |
| Brightness Set | AO0 | 40101 | BRT x |

## Sources
- [VESA DDC/CI Standard](https://vesa.org/)
- [CEC HDMI Control](https://www.hdmi.org/)
- [RS-232 Control Protocol](https://www.infocomm.org/)
