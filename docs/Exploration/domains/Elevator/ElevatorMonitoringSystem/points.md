# Points de Elevator Monitoring System

## Synthèse
- **Total points mesure** : 10
- **Total points commande** : 5
- **Total points état** : 9

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Total Trips Today | sensor-point | count | 0-10000 | 5min | Voyages aujourd'hui |
| Total Faults Today | sensor-point | count | 0-100 | 5min | Défauts aujourd'hui |
| Availability Rate | sensor-point | % | 0-100% | 1h | Taux disponibilité |
| MTBF | sensor-point | h | 0-10000 | 24h | Temps moyen entre pannes |
| MTTR | sensor-point | h | 0-100 | 24h | Temps moyen réparation |
| Energy Total | sensor-elec-energy-point | kWh | 0-999999 | 1h | Énergie totale groupe |
| Average Wait Time | sensor-point | s | 0-300 | 15min | Temps attente moyen |
| Server CPU Usage | sensor-point | % | 0-100% | 30s | Utilisation CPU serveur |
| Database Size | sensor-point | GB | 0-1000 | 1h | Taille base données |
| Connected Controllers | sensor-point | count | 0-100 | 1min | Contrôleurs connectés |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Generate Report | cmd-point | - | GENERATE | Binaire | Génération rapport |
| Reset Statistics | cmd-point | - | RESET | Binaire | RAZ statistiques |
| Acknowledge Alarm | cmd-point | - | ACK | Binaire | Acquittement alarme |
| Enable Notifications | cmd-point | - | ENABLE/DISABLE | Binaire | Activation notifications |
| Data Export | cmd-point | - | EXPORT | Binaire | Export données |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| System Status | status-point | Enum | OK/WARNING/CRITICAL | État général |
| Server Status | status-point | Enum | RUNNING/STOPPED/FAULT | État serveur |
| Database Status | status-point | Enum | OK/WARNING/FAULT | État base données |
| Network Status | status-point | Enum | OK/DEGRADED/FAULT | État réseau |
| BMS Integration | status-point | Enum | CONNECTED/DISCONNECTED | État BMS |
| Active Alarms | status-point | Number | 0-1000 | Alarmes actives |
| Unacknowledged Alarms | status-point | Number | 0-1000 | Alarmes non acquittées |
| License Status | status-point | Enum | VALID/EXPIRING/EXPIRED | État licence |
| Last Backup Status | status-point | Enum | OK/FAILED | État dernière sauvegarde |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | REST API |
|-------|---------------|-----------------|----------|
| System Status | MSV0 | 40001 | /api/status |
| Availability Rate | AI0 | 40002 | /api/metrics/availability |
| Energy Total | AI1 | 40003-40004 | /api/metrics/energy |
| Active Alarms | AI2 | 40005 | /api/alarms/active |
| Generate Report | BO0 | 00001 | /api/reports/generate |
| Acknowledge Alarm | BO1 | 00002 | /api/alarms/ack |
| Connected Controllers | AI3 | 40006 | /api/controllers/count |

## Sources
- [EN 81-28 Remote Alarm](https://www.en-standard.eu/)
- [ISO 22201 Data Logger](https://www.iso.org/)
- [BACnet Elevator Standard](https://www.bacnet.org/)
