# Points de Wireless Presentation Gateway (Passerelle présentation sans fil)

## Synthèse
- **Total points mesure** : 7
- **Total points commande** : 5
- **Total points état** : 6

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Connected Devices | sensor-point | count | 0-32 | 1s | Appareils connectés |
| Active Presenters | sensor-point | count | 0-4 | 1s | Présentateurs actifs |
| Network Bandwidth | sensor-point | Mbps | 0-1000 | 30s | Bande passante utilisée |
| Stream Latency | sensor-point | ms | 0-500 | 1s | Latence flux |
| Session Duration | sensor-point | s | 0-86400 | 1s | Durée session |
| Daily Sessions | sensor-point | count | 0-100 | 1h | Sessions journalières |
| Uptime | sensor-point | h | 0-99999 | 1h | Temps fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Moderator Mode | cmd-point | - | ON/OFF | Binaire | Mode modérateur |
| Allow Connections | cmd-point | - | ON/OFF | Binaire | Autoriser connexions |
| Disconnect All | cmd-point | - | TRIGGER | Binaire | Déconnecter tous |
| Output Resolution | cmd-sp-point | - | 720p/1080p/4K | Enum | Résolution sortie |
| System Reboot | cmd-point | - | TRIGGER | Binaire | Redémarrage |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Gateway Status | status-point | Enum | OK/WARNING/FAULT | État général |
| Presentation Status | status-point | Enum | IDLE/PRESENTING/WAITING | État présentation |
| WiFi Status | status-point | Enum | OK/DEGRADED/FAULT | État WiFi |
| Output Status | status-point | Enum | CONNECTED/DISCONNECTED | État sortie |
| Security Status | status-point | Enum | SECURED/OPEN | État sécurité |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | HTTP API |
|-------|---------------|-----------------|----------|
| Connected Devices | AI0 | 30001 | /api/devices |
| Active Presenters | AI1 | 30002 | /api/presenters |
| Network Bandwidth | AI2 | 30003 | /api/stats |
| Gateway Status | MSV0 | 40001 | /api/status |
| Presentation Status | MSV1 | 40002 | /api/presentation |
| Moderator Mode | BO0 | 00001 | /api/moderator |
| Disconnect All | BO1 | 00002 | /api/disconnect |

## Sources
- [Miracast Specification](https://www.wi-fi.org/)
- [AirPlay Protocol](https://developer.apple.com/)
- [Google Cast SDK](https://developers.google.com/cast)
