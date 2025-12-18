# Points de Wireless Microphone System (Système microphone sans fil)

## Synthèse
- **Total points mesure** : 8
- **Total points commande** : 5
- **Total points état** : 7

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Channels Active | sensor-point | count | 0-32 | 1s | Canaux actifs |
| RF Level | sensor-point | dBm | -100 à 0 | 100ms | Niveau RF |
| Audio Level | sensor-point | dBFS | -60 à 0 | 100ms | Niveau audio |
| Battery Level | sensor-point | % | 0-100% | 1min | Niveau batterie émetteur |
| Battery Time Remaining | sensor-point | min | 0-600 | 1min | Autonomie restante |
| Frequency | sensor-point | MHz | 470-698 | Config | Fréquence utilisée |
| Diversity Antenna | sensor-point | - | A/B | 100ms | Antenne active |
| Operating Hours | sensor-point | h | 0-99999 | 1h | Heures fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Mute | cmd-point | - | ON/OFF | Binaire | Sourdine |
| Gain | cmd-sp-point | dB | -20 à +20 | Analog | Gain |
| Frequency Set | cmd-sp-point | MHz | 470-698 | Analog | Configuration fréquence |
| Squelch | cmd-sp-point | dB | -90 à -30 | Analog | Seuil squelch |
| IR Sync | cmd-point | - | TRIGGER | Binaire | Synchronisation IR |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Receiver Status | status-point | Enum | OK/WARNING/FAULT | État général |
| RF Status | status-point | Enum | EXCELLENT/GOOD/WEAK/DROPOUT | État RF |
| Link Status | status-point | Enum | LINKED/SEARCHING/NOT_LINKED | État liaison |
| Mute Status | status-point | Boolean | FALSE/TRUE | Sourdine active |
| Battery Status | status-point | Enum | OK/LOW/CRITICAL | État batterie |
| Interference Detected | status-point | Boolean | FALSE/TRUE | Interférence détectée |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | Proprietary |
|-------|---------------|-----------------|-------------|
| RF Level | AI0 | 30001 | Query RF |
| Audio Level | AI1 | 30002 | Query Audio |
| Battery Level | AI2 | 30003 | Query Battery |
| Receiver Status | MSV0 | 40001 | Query Status |
| RF Status | MSV1 | 40002 | Query RF |
| Gain | AO0 | 40101 | Set Gain |
| Mute | BO0 | 00001 | Set Mute |

## Sources
- [ETSI EN 300 422 Wireless Microphones](https://www.etsi.org/)
- [FCC Part 74 Wireless Microphones](https://www.fcc.gov/)
- [Dante Protocol](https://www.audinate.com/)
