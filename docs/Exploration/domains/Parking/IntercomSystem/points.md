# Points de Intercom System

## Synthèse
- **Total points mesure** : 6
- **Total points commande** : 6
- **Total points état** : 8

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Audio Level Input | sensor-point | dB | -60 à 0 dB | 100ms | Niveau audio entrée (microphone) |
| Audio Level Output | sensor-point | dB | -60 à 0 dB | 100ms | Niveau audio sortie (haut-parleur) |
| Call Count | sensor-point | count | 0-999999 | Sur événement | Nombre total d'appels |
| Average Call Duration | sensor-point | s | 0-600 s | 1h | Durée moyenne des appels |
| Network Latency | sensor-point | ms | 0-500 ms | 10s | Latence réseau VoIP |
| Camera Frame Rate | sensor-point | fps | 0-30 fps | 5s | Fréquence images caméra vidéo |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Call Answer | cmd-point | - | ANSWER/REJECT | Binaire | Répondre/rejeter appel entrant |
| Call Hangup | cmd-point | - | HANGUP | Binaire | Terminer appel en cours |
| Volume Control | cmd-sp-point | % | 0-100% | Analog | Volume haut-parleur |
| Microphone Mute | cmd-point | - | MUTE/UNMUTE | Binaire | Couper/activer microphone |
| Camera Enable | cmd-point | - | ENABLE/DISABLE | Binaire | Activation caméra vidéo |
| Call Destination | cmd-point | - | EXTENSION | String | Numéro/extension destination |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Intercom Status | status-point | Enum | OK/FAULT/OFFLINE | État général interphone |
| Call Status | status-point | Enum | IDLE/RINGING/CONNECTED/BUSY | État appel |
| Audio Status | status-point | Enum | OK/NO_AUDIO/DISTORTED | État audio |
| Camera Status | status-point | Enum | OK/FAULT/OFFLINE | État caméra vidéo |
| SIP Connection | status-point | Enum | REGISTERED/UNREGISTERED | État connexion SIP |
| Button Pressed | status-point | Boolean | TRUE/FALSE | Bouton d'appel actionné |
| Network Connection | status-point | Enum | CONNECTED/DISCONNECTED | État connexion réseau |
| Last Call Time | status-point | Timestamp | ISO8601 | Horodatage dernier appel |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | SIP |
|-------|---------------|-----------------|-----|
| Intercom Status | MSV0 | 40001 | - |
| Audio Level Input | AI0 | 40002 | - |
| Audio Level Output | AI1 | 40003 | - |
| Call Count | AI2 | 40004-40005 | - |
| Call Answer | BO0 | 00001 | INVITE 200 OK |
| Volume Control | AO0 | 40101 | - |
| Call Status | MSV1 | 40011 | Session State |
| SIP Connection | MSV2 | 40012 | REGISTER |

## Sources
- [SIP Protocol RFC 3261](https://tools.ietf.org/html/rfc3261)
- [VoIP Intercom System Documentation](https://www.voip-info.org/)
