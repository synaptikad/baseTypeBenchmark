# Points de Parking Guidance Controller

## Synthèse
- **Total points mesure** : 9
- **Total points commande** : 6
- **Total points état** : 9

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Total Sensors Connected | sensor-point | count | 0-500 | 1min | Nombre capteurs connectés |
| Occupied Spaces | sensor-point | count | 0-500 | 10s | Nombre places occupées |
| Free Spaces | sensor-point | count | 0-500 | 10s | Nombre places libres |
| Sensor Update Rate | sensor-point | Hz | 0-10 Hz | 1min | Fréquence mise à jour capteurs |
| CPU Usage | sensor-point | % | 0-100% | 30s | Utilisation processeur |
| Memory Usage | sensor-point | % | 0-100% | 30s | Utilisation mémoire |
| Network Bandwidth | sensor-point | kbps | 0-1000 kbps | 1min | Bande passante réseau utilisée |
| Data Processing Rate | sensor-point | msg/s | 0-100 | 1min | Taux traitement messages |
| Controller Temperature | sensor-temp-point | °C | -20 à +60°C | 5min | Température interne contrôleur |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Controller Enable | cmd-point | - | ENABLE/DISABLE | Binaire | Activation/désactivation contrôleur |
| Sensor Polling Enable | cmd-point | - | ENABLE/DISABLE | Binaire | Activation polling capteurs |
| Display Update Enable | cmd-point | - | ENABLE/DISABLE | Binaire | Activation mise à jour afficheurs |
| Aggregation Interval | cmd-sp-point | s | 5-60 s | Analog | Intervalle agrégation données |
| Fault Detection Enable | cmd-point | - | ENABLE/DISABLE | Binaire | Détection anomalies capteurs |
| Reset Statistics | cmd-point | - | RESET | Binaire | Remise à zéro statistiques |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Controller Status | status-point | Enum | OK/DEGRADED/FAULT/OFFLINE | État général contrôleur |
| Communication Status | status-point | Enum | CONNECTED/DISCONNECTED | État connexion réseau |
| Sensor Faults Count | status-point | Number | 0-500 | Nombre capteurs en défaut |
| Display Faults Count | status-point | Number | 0-50 | Nombre afficheurs en défaut |
| Database Sync Status | status-point | Enum | SYNCED/SYNCING/ERROR | État synchronisation serveur |
| Last Update Time | status-point | Timestamp | ISO8601 | Horodatage dernière mise à jour |
| Occupancy Rate | status-point | Number | 0-100% | Taux occupation zone |
| Zone Status | status-point | Enum | AVAILABLE/FULL/RESERVED | État zone gérée |
| Alarm Active | status-point | Boolean | TRUE/FALSE | Alarme système active |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| Controller Status | MSV0 | 40001 |
| Occupied Spaces | AI0 | 40002 |
| Free Spaces | AI1 | 40003 |
| CPU Usage | AI2 | 40004 |
| Memory Usage | AI3 | 40005 |
| Controller Enable | BO0 | 00001 |
| Sensor Polling Enable | BO1 | 00002 |
| Sensor Faults Count | AI4 | 40011 |

## Sources
- [Modbus TCP/RTU Protocol](https://www.modbus.org/)
- [BACnet Protocol Standards](https://www.bacnet.org/)
- [Parking Guidance System Architecture](https://www.parking-guidance.com/)
