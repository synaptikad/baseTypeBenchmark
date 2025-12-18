# Points de Media Server (Serveur média)

## Synthèse
- **Total points mesure** : 9
- **Total points commande** : 6
- **Total points état** : 7

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Active Outputs | sensor-point | count | 0-16 | 1s | Sorties actives |
| CPU Usage | sensor-point | % | 0-100% | 30s | Utilisation CPU |
| GPU Usage | sensor-point | % | 0-100% | 30s | Utilisation GPU |
| Memory Usage | sensor-point | % | 0-100% | 30s | Utilisation mémoire |
| Storage Used | sensor-point | % | 0-100% | 5min | Stockage utilisé |
| Network Throughput | sensor-point | Mbps | 0-10000 | 30s | Débit réseau |
| Frame Rate Output | sensor-point | fps | 0-60 | 1s | FPS sortie |
| Dropped Frames | sensor-point | count | 0-999999 | 1min | Images perdues |
| Uptime | sensor-point | h | 0-99999 | 1h | Temps fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Show Load | cmd-sp-point | - | Show ID | Analog | Chargement show |
| Show Play | cmd-point | - | ON/OFF | Binaire | Lecture show |
| Cue Trigger | cmd-sp-point | - | Cue ID | Analog | Déclenchement cue |
| Output Enable | cmd-sp-point | - | Output bitmask | Analog | Activation sorties |
| Content Sync | cmd-point | - | TRIGGER | Binaire | Synchronisation contenu |
| System Restart | cmd-point | - | TRIGGER | Binaire | Redémarrage |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Server Status | status-point | Enum | OK/WARNING/FAULT | État général |
| Playback Status | status-point | Enum | PLAYING/PAUSED/STOPPED | État lecture |
| Render Status | status-point | Enum | OK/DROPPED/OVERLOAD | État rendu |
| Sync Status | status-point | Enum | MASTER/SLAVE/SYNCED | État synchronisation |
| GPU Status | status-point | Enum | OK/WARNING/FAULT | État GPU |
| Storage Status | status-point | Enum | OK/LOW/FAULT | État stockage |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | OSC/TCP |
|-------|---------------|-----------------|---------|
| Active Outputs | AI0 | 30001 | /status/outputs |
| CPU Usage | AI1 | 30002 | /status/cpu |
| Server Status | MSV0 | 40001 | /status |
| Playback Status | MSV1 | 40002 | /playback/status |
| Show Load | AO0 | 40101 | /show/load |
| Cue Trigger | AO1 | 40102 | /cue/go |

## Sources
- [SMPTE ST 2110](https://www.smpte.org/)
- [NDI Protocol](https://www.ndi.tv/)
- [OSC Protocol](https://opensoundcontrol.stanford.edu/)
