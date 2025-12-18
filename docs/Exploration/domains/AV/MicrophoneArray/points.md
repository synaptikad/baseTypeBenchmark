# Points de Microphone Array (Réseau de microphones)

## Synthèse
- **Total points mesure** : 7
- **Total points commande** : 5
- **Total points état** : 6

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Pickup Zones | sensor-point | count | 1-16 | Config | Zones captation |
| Active Talkers | sensor-point | count | 0-10 | 100ms | Locuteurs actifs |
| Input Level | sensor-point | dBFS | -60 à 0 | 100ms | Niveau entrée |
| Ambient Noise | sensor-point | dB SPL | 0-100 | 1s | Bruit ambiant |
| Echo Return Loss | sensor-point | dB | 0-60 | 1s | Atténuation écho |
| Beam Direction | sensor-point | ° | 0-360 | 100ms | Direction faisceau actif |
| Operating Hours | sensor-point | h | 0-99999 | 1h | Heures fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Mute | cmd-point | - | ON/OFF | Binaire | Sourdine |
| Gain | cmd-sp-point | dB | -20 à +20 | Analog | Gain |
| Beam Steering Mode | cmd-sp-point | - | AUTO/MANUAL/ZONE | Enum | Mode orientation |
| Zone Enable | cmd-sp-point | - | Zone bitmask | Analog | Activation zones |
| AEC Enable | cmd-point | - | ON/OFF | Binaire | Activation AEC |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Array Status | status-point | Enum | OK/FAULT | État général |
| Mute Status | status-point | Boolean | FALSE/TRUE | Sourdine active |
| AEC Status | status-point | Enum | CONVERGED/CONVERGING/FAULT | État AEC |
| Voice Activity | status-point | Boolean | FALSE/TRUE | Activité vocale |
| Clipping Status | status-point | Boolean | FALSE/TRUE | Écrêtage |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | Dante/USB |
|-------|---------------|-----------------|-----------|
| Active Talkers | AI0 | 30001 | Status Query |
| Input Level | AI1 | 30002 | Level Meter |
| Array Status | MSV0 | 40001 | Status |
| Mute Status | BI0 | 10001 | Mute Status |
| Gain | AO0 | 40101 | Gain Set |
| Mute | BO0 | 00001 | Mute |

## Sources
- [AES67 Audio over IP](https://www.aes.org/)
- [Dante Protocol](https://www.audinate.com/)
- [USB Audio Class](https://www.usb.org/)
