# Points de Intercom (Interphone)

## Synthèse
- **Total points mesure** : 5
- **Total points commande** : 5
- **Total points état** : 6

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Call Count | sensor-point | count | 0-99999 | Sur événement | Compteur appels |
| Call Duration | sensor-point | s | 0-300 | 1s | Durée appel en cours |
| Audio Level In | sensor-point | dB | 0-100 | 100ms | Niveau entrée audio |
| Audio Level Out | sensor-point | dB | 0-100 | 100ms | Niveau sortie audio |
| Operating Hours | sensor-point | h | 0-99999 | 1h | Heures fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Call Station | cmd-sp-point | - | Station ID | Analog | Appeler station |
| Answer Call | cmd-point | - | TRIGGER | Binaire | Répondre appel |
| End Call | cmd-point | - | TRIGGER | Binaire | Terminer appel |
| Door Release | cmd-point | - | TRIGGER | Binaire | Ouverture porte |
| Volume | cmd-sp-point | % | 0-100% | Analog | Volume |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Intercom Status | status-point | Enum | IDLE/CALLING/CONNECTED/FAULT | État général |
| Call Status | status-point | Enum | IDLE/RINGING/CONNECTED | État appel |
| Door Status | status-point | Enum | CLOSED/OPEN | État porte associée |
| Audio Status | status-point | Enum | OK/FAULT | État audio |
| Network Status | status-point | Enum | OK/FAULT | État réseau |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | SIP Protocol |
|-------|---------------|-----------------|--------------|
| Call Count | AI0 | 30001 | - |
| Audio Level In | AI1 | 30002 | - |
| Intercom Status | MSV0 | 40001 | REGISTER Status |
| Call Status | MSV1 | 40002 | Call State |
| Call Station | AO0 | 40101 | INVITE |
| Door Release | BO0 | 00001 | DTMF |

## Sources
- [SIP RFC 3261](https://datatracker.ietf.org/)
- [EN 50486 Intercom Systems](https://www.en-standard.eu/)
