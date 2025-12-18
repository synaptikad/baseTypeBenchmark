# Points de Soundbar (Barre de son)

## Synthèse
- **Total points mesure** : 5
- **Total points commande** : 6
- **Total points état** : 5

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Output Level | sensor-point | dB | 0-100 | 100ms | Niveau sortie |
| Input Signal Level | sensor-point | dBFS | -60 à 0 | 100ms | Niveau signal entrée |
| Temperature | sensor-temp-point | °C | 0-60°C | 30s | Température interne |
| Power Consumption | sensor-power-point | W | 0-100 | 1min | Consommation |
| Operating Hours | sensor-point | h | 0-99999 | 1h | Heures fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Power Enable | cmd-point | - | ON/OFF | Binaire | Mise sous tension |
| Volume | cmd-sp-point | % | 0-100% | Analog | Volume |
| Mute | cmd-point | - | ON/OFF | Binaire | Sourdine |
| Input Select | cmd-sp-point | - | HDMI/OPTICAL/BLUETOOTH/USB | Enum | Sélection entrée |
| Sound Mode | cmd-sp-point | - | MUSIC/MOVIE/VOICE/STANDARD | Enum | Mode son |
| Bass Level | cmd-sp-point | dB | -10 à +10 | Analog | Niveau basses |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Soundbar Status | status-point | Enum | ON/STANDBY/FAULT | État général |
| Signal Status | status-point | Enum | ACTIVE/NO_SIGNAL | État signal |
| Current Input | status-point | Enum | HDMI/OPTICAL/BLUETOOTH/USB | Entrée active |
| Mute Status | status-point | Boolean | FALSE/TRUE | Sourdine active |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | CEC/IR |
|-------|---------------|-----------------|--------|
| Output Level | AI0 | 30001 | - |
| Temperature | AI1 | 30002 | - |
| Soundbar Status | MSV0 | 40001 | Power Query |
| Power Enable | BO0 | 00001 | Power On/Off |
| Volume | AO0 | 40101 | Volume Set |
| Mute | BO1 | 00002 | Mute |
| Input Select | MSV1 | 40002 | Input |

## Sources
- [CEC HDMI Control](https://www.hdmi.org/)
- [Bluetooth A2DP](https://www.bluetooth.org/)
- [TOSLINK Optical Audio](https://www.toshiba.com/)
