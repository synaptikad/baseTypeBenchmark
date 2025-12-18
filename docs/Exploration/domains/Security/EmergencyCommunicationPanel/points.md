# Points de Emergency Communication Panel (Panneau communication urgence)

## Synthèse
- **Total points mesure** : 5
- **Total points commande** : 4
- **Total points état** : 6

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Call Count | sensor-point | count | 0-99999 | Sur événement | Compteur appels |
| Call Duration | sensor-point | s | 0-3600 | 1s | Durée appel en cours |
| Average Response Time | sensor-point | s | 0-300 | 1h | Temps réponse moyen |
| Audio Level | sensor-point | dB | 0-100 | 100ms | Niveau audio |
| Battery Level | sensor-point | % | 0-100% | 1h | Niveau batterie |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Initiate Call | cmd-point | - | TRIGGER | Binaire | Initier appel |
| End Call | cmd-point | - | TRIGGER | Binaire | Terminer appel |
| Volume | cmd-sp-point | % | 0-100% | Analog | Volume haut-parleur |
| Test Mode | cmd-point | - | ON/OFF | Binaire | Mode test |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Panel Status | status-point | Enum | READY/CALLING/CONNECTED/FAULT | État général |
| Call Status | status-point | Enum | IDLE/CALLING/CONNECTED | État appel |
| Network Status | status-point | Enum | OK/DEGRADED/FAULT | État réseau |
| Audio Status | status-point | Enum | OK/FAULT | État audio |
| Power Status | status-point | Enum | MAINS/BATTERY | État alimentation |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | SIP Protocol |
|-------|---------------|-----------------|--------------|
| Call Count | AI0 | 30001 | - |
| Audio Level | AI1 | 30002 | - |
| Panel Status | MSV0 | 40001 | REGISTER Status |
| Call Status | MSV1 | 40002 | Call State |
| Initiate Call | BO0 | 00001 | INVITE |
| Volume | AO0 | 40101 | - |

## Sources
- [EN 50849 Emergency Voice Comm](https://www.en-standard.eu/)
- [NFPA 72 Emergency Communication](https://www.nfpa.org/)
- [SIP RFC 3261](https://datatracker.ietf.org/)
