# Points de Video Intercom (Visiophone)

## Synthèse
- **Total points mesure** : 6
- **Total points commande** : 6
- **Total points état** : 7

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Call Count | sensor-point | count | 0-99999 | Sur événement | Compteur appels |
| Call Duration | sensor-point | s | 0-600 | 1s | Durée appel en cours |
| Door Opens | sensor-point | count | 0-99999 | Sur événement | Compteur ouvertures |
| Audio Level | sensor-point | dB | 0-100 | 100ms | Niveau audio |
| Light Level | sensor-point | lux | 0-10000 | 1s | Luminosité ambiante |
| Operating Hours | sensor-point | h | 0-99999 | 1h | Heures fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Call Station | cmd-sp-point | - | Station ID | Analog | Appeler station |
| Answer Call | cmd-point | - | TRIGGER | Binaire | Répondre appel |
| End Call | cmd-point | - | TRIGGER | Binaire | Terminer appel |
| Door Release | cmd-point | - | TRIGGER | Binaire | Ouverture porte |
| Volume | cmd-sp-point | % | 0-100% | Analog | Volume |
| Night Mode | cmd-point | - | ON/OFF | Binaire | Mode nuit (IR) |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Intercom Status | status-point | Enum | IDLE/CALLING/CONNECTED/FAULT | État général |
| Call Status | status-point | Enum | IDLE/RINGING/CONNECTED | État appel |
| Video Status | status-point | Enum | OK/FAULT | État vidéo |
| Audio Status | status-point | Enum | OK/FAULT | État audio |
| Door Status | status-point | Enum | CLOSED/OPEN | État porte |
| Tamper Status | status-point | Boolean | FALSE/TRUE | Sabotage détecté |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | SIP Protocol |
|-------|---------------|-----------------|--------------|
| Call Count | AI0 | 30001 | - |
| Audio Level | AI1 | 30002 | - |
| Intercom Status | MSV0 | 40001 | REGISTER Status |
| Call Status | MSV1 | 40002 | Call State |
| Video Status | MSV2 | 40003 | - |
| Call Station | AO0 | 40101 | INVITE |
| Door Release | BO0 | 00001 | DTMF |

## Sources
- [SIP RFC 3261](https://datatracker.ietf.org/)
- [ONVIF Door Control](https://www.onvif.org/)
- [EN 50486 Intercom Systems](https://www.en-standard.eu/)
