# Points de Digital Signage Player (Lecteur affichage dynamique)

## Synthèse
- **Total points mesure** : 7
- **Total points commande** : 6
- **Total points état** : 6

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| CPU Usage | sensor-point | % | 0-100% | 30s | Utilisation CPU |
| Memory Usage | sensor-point | % | 0-100% | 30s | Utilisation mémoire |
| Storage Used | sensor-point | % | 0-100% | 5min | Stockage utilisé |
| Temperature | sensor-temp-point | °C | 0-80°C | 30s | Température interne |
| Network Bandwidth | sensor-point | Mbps | 0-1000 | 30s | Bande passante |
| Content Play Count | sensor-point | count | 0-999999 | 1h | Lectures contenu |
| Uptime | sensor-point | h | 0-99999 | 1h | Temps fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Power Enable | cmd-point | - | ON/OFF | Binaire | Mise sous tension |
| Playlist Select | cmd-sp-point | - | Playlist ID | Analog | Sélection playlist |
| Content Sync | cmd-point | - | TRIGGER | Binaire | Synchronisation contenu |
| Volume | cmd-sp-point | % | 0-100% | Analog | Volume audio |
| Display Output | cmd-point | - | ON/OFF | Binaire | Sortie affichage |
| System Reboot | cmd-point | - | TRIGGER | Binaire | Redémarrage |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Player Status | status-point | Enum | OK/WARNING/FAULT | État général |
| Playback Status | status-point | Enum | PLAYING/PAUSED/STOPPED/ERROR | État lecture |
| Sync Status | status-point | Enum | SYNCED/SYNCING/OUTDATED | État synchronisation |
| Network Status | status-point | Enum | OK/DEGRADED/FAULT | État réseau |
| Display Status | status-point | Enum | CONNECTED/DISCONNECTED | État affichage |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | HTTP API |
|-------|---------------|-----------------|----------|
| CPU Usage | AI0 | 30001 | /api/status |
| Temperature | AI1 | 30002 | /api/status |
| Player Status | MSV0 | 40001 | /api/status |
| Playback Status | MSV1 | 40002 | /api/playback |
| Playlist Select | AO0 | 40101 | /api/playlist |
| Power Enable | BO0 | 00001 | /api/power |

## Sources
- [SMIL 3.0 Specification](https://www.w3.org/)
- [POPAI Digital Signage](https://www.popai.com/)
