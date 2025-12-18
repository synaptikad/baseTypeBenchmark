# Points de Room Scheduling Display (Écran réservation salle)

## Synthèse
- **Total points mesure** : 5
- **Total points commande** : 5
- **Total points état** : 5

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Meetings Today | sensor-point | count | 0-50 | 1min | Réunions aujourd'hui |
| Occupancy Time | sensor-point | % | 0-100% | 1h | Taux occupation |
| Touch Interactions | sensor-point | count | 0-9999 | 1h | Interactions tactiles |
| Ambient Light | sensor-point | lux | 0-10000 | 1min | Luminosité ambiante |
| Uptime | sensor-point | h | 0-99999 | 1h | Temps fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Display Brightness | cmd-sp-point | % | 0-100% | Analog | Luminosité écran |
| Quick Book | cmd-sp-point | min | 15/30/60 | Analog | Réservation rapide |
| End Meeting | cmd-point | - | TRIGGER | Binaire | Fin réunion |
| Check In | cmd-point | - | TRIGGER | Binaire | Confirmation présence |
| Display Mode | cmd-sp-point | - | AUTO/ON/OFF | Enum | Mode affichage |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Display Status | status-point | Enum | OK/FAULT | État général |
| Room Status | status-point | Enum | FREE/OCCUPIED/RESERVED | État salle |
| Calendar Sync | status-point | Enum | SYNCED/SYNCING/ERROR | État synchronisation |
| Current Meeting | status-point | String | Meeting name | Réunion en cours |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | REST API |
|-------|---------------|-----------------|----------|
| Meetings Today | AI0 | 30001 | /api/calendar |
| Occupancy Time | AI1 | 30002 | /api/stats |
| Display Status | MSV0 | 40001 | /api/status |
| Room Status | MSV1 | 40002 | /api/room |
| Quick Book | AO0 | 40101 | /api/book |
| Display Brightness | AO1 | 40102 | /api/display |

## Sources
- [Microsoft Graph API](https://docs.microsoft.com/graph/)
- [Google Calendar API](https://developers.google.com/calendar)
- [EWS Exchange Web Services](https://docs.microsoft.com/)
