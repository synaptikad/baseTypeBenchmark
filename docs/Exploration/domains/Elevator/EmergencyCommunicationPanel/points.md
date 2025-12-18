# Points de Emergency Communication Panel

## Synthèse
- **Total points mesure** : 6
- **Total points commande** : 5
- **Total points état** : 8

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Call Duration | sensor-point | s | 0-3600 | Sur événement | Durée appel en cours |
| Call Count | sensor-point | count | 0-999999 | Sur événement | Appels cumulés |
| Audio Level Mic | sensor-point | dB | -60 à 0 | 100ms | Niveau microphone |
| Audio Level Speaker | sensor-point | dB | -60 à 0 | 100ms | Niveau haut-parleur |
| Battery Voltage | sensor-elec-volt-point | V | 10-15 V | 5min | Tension batterie secours |
| Panel Temperature | sensor-temp-point | °C | 10-50°C | 5min | Température panneau |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Test Call | cmd-point | - | TRIGGER | Binaire | Test appel |
| Volume Adjust | cmd-sp-point | % | 0-100% | Analog | Réglage volume |
| Mic Mute | cmd-point | - | MUTE/UNMUTE | Binaire | Coupure microphone |
| Answer Call | cmd-point | - | ANSWER | Binaire | Décrocher appel |
| End Call | cmd-point | - | END | Binaire | Terminer appel |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Panel Status | status-point | Enum | OK/FAULT/OFFLINE | État général |
| Call Status | status-point | Enum | IDLE/RINGING/CONNECTED/FAILED | État appel |
| Line Status | status-point | Enum | OK/NO_LINE/FAULT | État ligne téléphonique |
| Battery Status | status-point | Enum | OK/LOW/CHARGING/FAULT | État batterie |
| Microphone Status | status-point | Enum | OK/FAULT | État microphone |
| Speaker Status | status-point | Enum | OK/FAULT | État haut-parleur |
| Emergency Button | status-point | Boolean | FALSE/TRUE | Bouton urgence activé |
| Last Test Result | status-point | Enum | PASS/FAIL | Résultat dernier test |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | SIP |
|-------|---------------|-----------------|-----|
| Panel Status | MSV0 | 40001 | - |
| Call Status | MSV1 | 40002 | Session State |
| Battery Voltage | AI0 | 40003 | - |
| Emergency Button | BI0 | 10001 | - |
| Test Call | BO0 | 00001 | INVITE |
| Volume Adjust | AO0 | 40101 | - |
| Line Status | MSV2 | 40010 | REGISTER |

## Sources
- [EN 81-28 Remote Alarm](https://www.en-standard.eu/)
- [EN 81-70 Accessibility](https://www.en-standard.eu/)
- [ASME A17.1 Emergency Communications](https://www.asme.org/)
