# Points de PTZ Camera (Caméra PTZ)

## Synthèse
- **Total points mesure** : 10
- **Total points commande** : 10
- **Total points état** : 7

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Pan Position | sensor-point | ° | -180 à +180 | 100ms | Position pan |
| Tilt Position | sensor-point | ° | -90 à +90 | 100ms | Position tilt |
| Zoom Position | sensor-point | x | 1-30 | 100ms | Position zoom |
| Resolution | sensor-point | MP | 1-12 | Config | Résolution |
| Frame Rate | sensor-point | fps | 1-60 | 1s | Images par seconde |
| Bitrate | sensor-point | Mbps | 0-50 | 1s | Débit flux |
| Light Level | sensor-point | lux | 0-100000 | 1s | Niveau luminosité |
| Motor Hours Pan | sensor-point | h | 0-50000 | 1h | Heures moteur pan |
| Motor Hours Tilt | sensor-point | h | 0-50000 | 1h | Heures moteur tilt |
| Uptime | sensor-point | h | 0-99999 | 1h | Temps fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Pan Set | cmd-sp-point | ° | -180 à +180 | Analog | Consigne pan |
| Tilt Set | cmd-sp-point | ° | -90 à +90 | Analog | Consigne tilt |
| Zoom Set | cmd-sp-point | x | 1-30 | Analog | Consigne zoom |
| Preset Recall | cmd-sp-point | - | 1-255 | Analog | Rappel preset |
| Preset Save | cmd-sp-point | - | 1-255 | Analog | Sauvegarde preset |
| Home Position | cmd-point | - | TRIGGER | Binaire | Retour position home |
| Auto Tracking | cmd-point | - | ON/OFF | Binaire | Suivi automatique |
| Stream Enable | cmd-point | - | ON/OFF | Binaire | Activation flux |
| IR Mode | cmd-sp-point | - | AUTO/ON/OFF | Enum | Mode infrarouge |
| Focus Mode | cmd-sp-point | - | AUTO/MANUAL | Enum | Mode mise au point |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Camera Status | status-point | Enum | OK/FAULT | État général |
| PTZ Status | status-point | Enum | IDLE/MOVING/PRESET/FAULT | État PTZ |
| Stream Status | status-point | Enum | STREAMING/STOPPED/FAULT | État flux |
| Tracking Status | status-point | Enum | IDLE/TRACKING/LOST | État suivi |
| Focus Status | status-point | Enum | FOCUSED/FOCUSING | État mise au point |
| Motor Status | status-point | Enum | OK/WARNING/FAULT | État moteurs |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | VISCA/NDI |
|-------|---------------|-----------------|-----------|
| Pan Position | AI0 | 30001 | CAM_PanTiltPosInq |
| Tilt Position | AI1 | 30002 | CAM_PanTiltPosInq |
| Zoom Position | AI2 | 30003 | CAM_ZoomPosInq |
| Camera Status | MSV0 | 40001 | Status |
| Pan Set | AO0 | 40101 | CAM_PanTiltDrive |
| Tilt Set | AO1 | 40102 | CAM_PanTiltDrive |
| Preset Recall | AO2 | 40103 | CAM_Memory |

## Sources
- [VISCA Protocol](https://pro.sony/)
- [NDI Protocol](https://www.ndi.tv/)
- [ONVIF PTZ](https://www.onvif.org/)
