# Points de Video Conference Codec (Codec visioconférence)

## Synthèse
- **Total points mesure** : 10
- **Total points commande** : 8
- **Total points état** : 8

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Call Duration | sensor-point | s | 0-86400 | 1s | Durée appel en cours |
| Daily Calls | sensor-point | count | 0-100 | 1h | Appels aujourd'hui |
| Network Bandwidth Used | sensor-point | Mbps | 0-50 | 1s | Bande passante utilisée |
| Packet Loss | sensor-point | % | 0-100% | 1s | Perte paquets |
| Jitter | sensor-point | ms | 0-500 | 1s | Gigue réseau |
| Audio Level Rx | sensor-point | dBFS | -60 à 0 | 100ms | Niveau audio reçu |
| Audio Level Tx | sensor-point | dBFS | -60 à 0 | 100ms | Niveau audio transmis |
| Video Resolution Tx | sensor-point | pixels | Various | 1s | Résolution transmise |
| Frame Rate Tx | sensor-point | fps | 0-60 | 1s | FPS transmis |
| Uptime | sensor-point | h | 0-99999 | 1h | Temps fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Call Dial | cmd-sp-point | - | URI/Number | String | Appeler |
| Call Disconnect | cmd-point | - | TRIGGER | Binaire | Raccrocher |
| Mute Mic | cmd-point | - | ON/OFF | Binaire | Sourdine micro |
| Mute Video | cmd-point | - | ON/OFF | Binaire | Désactiver vidéo |
| Volume | cmd-sp-point | % | 0-100% | Analog | Volume |
| Camera Preset | cmd-sp-point | - | 1-10 | Analog | Preset caméra |
| Content Share | cmd-point | - | ON/OFF | Binaire | Partage contenu |
| Do Not Disturb | cmd-point | - | ON/OFF | Binaire | Ne pas déranger |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Codec Status | status-point | Enum | OK/WARNING/FAULT | État général |
| Call Status | status-point | Enum | IDLE/RINGING/CONNECTED/ON_HOLD | État appel |
| Mic Mute Status | status-point | Boolean | FALSE/TRUE | Micro muet |
| Video Mute Status | status-point | Boolean | FALSE/TRUE | Vidéo désactivée |
| Content Sharing | status-point | Boolean | FALSE/TRUE | Partage actif |
| Network Quality | status-point | Enum | EXCELLENT/GOOD/FAIR/POOR | Qualité réseau |
| Registration Status | status-point | Enum | REGISTERED/UNREGISTERED/ERROR | État enregistrement |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | xAPI/SIP |
|-------|---------------|-----------------|----------|
| Call Duration | AI0 | 30001 | xStatus Call |
| Network Bandwidth Used | AI1 | 30002 | xStatus Network |
| Codec Status | MSV0 | 40001 | xStatus SystemUnit |
| Call Status | MSV1 | 40002 | xStatus Call |
| Call Dial | MSV2 | 40003 | xCommand Dial |
| Mute Mic | BO0 | 00001 | xCommand Audio |
| Volume | AO0 | 40101 | xCommand Audio |

## Sources
- [SIP RFC 3261](https://datatracker.ietf.org/)
- [H.323 ITU-T](https://www.itu.int/)
- [Cisco xAPI](https://roomos.cisco.com/)
- [Zoom Rooms API](https://developers.zoom.us/)
