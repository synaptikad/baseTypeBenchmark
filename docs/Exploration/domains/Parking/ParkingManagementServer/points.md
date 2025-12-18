# Points de Parking Management Server

## Synthèse
- **Total points mesure** : 12
- **Total points commande** : 7
- **Total points état** : 10

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Total Parking Capacity | sensor-point | count | 0-10000 | Sur demande | Capacité totale parking |
| Total Occupied | sensor-point | count | 0-10000 | 30s | Nombre total places occupées |
| Total Available | sensor-point | count | 0-10000 | 30s | Nombre total places disponibles |
| Occupancy Rate | sensor-point | % | 0-100% | 1min | Taux d'occupation global |
| Revenue Today | sensor-point | € | 0-999999 | 5min | Revenu journalier |
| Transactions Today | sensor-point | count | 0-10000 | 5min | Nombre transactions jour |
| Average Stay Duration | sensor-point | min | 0-720 min | 15min | Durée moyenne stationnement |
| Server CPU Usage | sensor-point | % | 0-100% | 30s | Utilisation CPU serveur |
| Server Memory Usage | sensor-point | % | 0-100% | 30s | Utilisation mémoire serveur |
| Database Response Time | sensor-point | ms | 1-1000 ms | 1min | Temps réponse base données |
| API Request Rate | sensor-point | req/s | 0-1000 | 1min | Taux requêtes API |
| Connected Devices | sensor-point | count | 0-500 | 1min | Nombre équipements connectés |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| System Enable | cmd-point | - | ENABLE/DISABLE | Binaire | Activation système complet |
| Tariff Profile | cmd-point | - | PROFILE_ID | String | Profil tarifaire actif |
| Emergency Mode | cmd-point | - | ENABLE/DISABLE | Binaire | Mode urgence (barrières ouvertes) |
| Database Backup | cmd-point | - | BACKUP | Binaire | Lancement sauvegarde BD |
| Report Generation | cmd-point | - | GENERATE | Binaire | Génération rapport |
| Notification Send | cmd-point | - | SEND | Binaire | Envoi notification système |
| Integration Sync | cmd-point | - | SYNC | Binaire | Synchronisation systèmes tiers |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Server Status | status-point | Enum | RUNNING/STOPPED/ERROR/MAINTENANCE | État serveur principal |
| Database Status | status-point | Enum | CONNECTED/DISCONNECTED/ERROR | État base de données |
| BMS Integration Status | status-point | Enum | CONNECTED/DISCONNECTED | État intégration BMS |
| Payment Gateway Status | status-point | Enum | ONLINE/OFFLINE/ERROR | État passerelle paiement |
| OCPP Backend Status | status-point | Enum | RUNNING/STOPPED | État backend OCPP (EV) |
| Cluster Status | status-point | Enum | HEALTHY/DEGRADED/FAULT | État cluster HA |
| Backup Status | status-point | Enum | OK/IN_PROGRESS/FAILED | État dernière sauvegarde |
| License Status | status-point | Enum | VALID/EXPIRING/EXPIRED | État licence logicielle |
| Security Alert | status-point | Boolean | TRUE/FALSE | Alerte sécurité active |
| Last Backup Time | status-point | Timestamp | ISO8601 | Horodatage dernière sauvegarde |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| Server Status | MSV0 | 40001 |
| Total Occupied | AI0 | 40002 |
| Total Available | AI1 | 40003 |
| Occupancy Rate | AI2 | 40004 |
| Server CPU Usage | AI3 | 40005 |
| Server Memory Usage | AI4 | 40006 |
| System Enable | BO0 | 00001 |
| Emergency Mode | BO1 | 00002 |

## Sources
- [BACnet Protocol Specifications](https://www.bacnet.org/)
- [OCPP Protocol Documentation](https://www.openchargealliance.org/)
- [Parking Management System Architecture](https://www.parking-net.com/)
- [MQTT IoT Protocol](https://mqtt.org/)
