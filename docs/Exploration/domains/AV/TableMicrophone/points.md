# Points de Table Microphone (Microphone de table)

## Synthèse
- **Total points mesure** : 5
- **Total points commande** : 4
- **Total points état** : 5

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Input Level | sensor-point | dBFS | -60 à 0 | 100ms | Niveau entrée |
| SPL | sensor-point | dB | 0-130 | 100ms | Niveau pression sonore |
| Ambient Noise | sensor-point | dB | 0-80 | 1s | Bruit ambiant |
| Battery Level | sensor-point | % | 0-100% | 1min | Niveau batterie (sans fil) |
| Operating Hours | sensor-point | h | 0-99999 | 1h | Heures fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Mute | cmd-point | - | ON/OFF | Binaire | Sourdine |
| Gain | cmd-sp-point | dB | -20 à +20 | Analog | Gain |
| LED Mode | cmd-sp-point | - | OFF/ON_AIR/MUTE_INDICATOR | Enum | Mode LED |
| Phantom Power | cmd-point | - | ON/OFF | Binaire | Alimentation fantôme |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Microphone Status | status-point | Enum | OK/FAULT | État général |
| Mute Status | status-point | Boolean | FALSE/TRUE | Sourdine active |
| Clipping Status | status-point | Boolean | FALSE/TRUE | Écrêtage |
| Voice Activity | status-point | Boolean | FALSE/TRUE | Activité vocale |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | Dante/USB |
|-------|---------------|-----------------|-----------|
| Input Level | AI0 | 30001 | Level Meter |
| SPL | AI1 | 30002 | - |
| Microphone Status | MSV0 | 40001 | Status |
| Mute Status | BI0 | 10001 | Mute Status |
| Gain | AO0 | 40101 | Gain Set |
| Mute | BO0 | 00001 | Mute |

## Sources
- [AES42 Digital Microphone](https://www.aes.org/)
- [Dante Protocol](https://www.audinate.com/)
- [USB Audio Class](https://www.usb.org/)
