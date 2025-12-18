# Points de Video Management System (Système gestion vidéo)

## Synthèse
- **Total points mesure** : 12
- **Total points commande** : 7
- **Total points état** : 9

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Total Cameras | sensor-point | count | 0-10000 | 1min | Total caméras |
| Online Cameras | sensor-point | count | 0-10000 | 1min | Caméras en ligne |
| Recording Cameras | sensor-point | count | 0-10000 | 1min | Caméras enregistrant |
| Total Bitrate | sensor-point | Gbps | 0-100 | 30s | Débit total |
| Storage Used | sensor-point | % | 0-100% | 5min | Stockage utilisé |
| Storage Available | sensor-point | PB | 0-10 | 5min | Stockage disponible |
| Active Users | sensor-point | count | 0-1000 | 1min | Utilisateurs actifs |
| Active Streams | sensor-point | count | 0-10000 | 1min | Flux actifs |
| Events Per Hour | sensor-point | count | 0-10000 | 1h | Événements par heure |
| CPU Usage | sensor-point | % | 0-100% | 30s | Utilisation CPU serveur |
| Network Throughput | sensor-point | Gbps | 0-100 | 30s | Débit réseau |
| Uptime | sensor-point | h | 0-99999 | 1h | Temps fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Recording Global | cmd-point | - | ON/OFF | Binaire | Enregistrement global |
| Site Enable | cmd-sp-point | - | Site ID | Analog | Activation site |
| Retention Days | cmd-sp-point | days | 1-365 | Analog | Durée rétention |
| Analytics Enable | cmd-point | - | ON/OFF | Binaire | Activation analyse |
| Export Trigger | cmd-point | - | TRIGGER | Binaire | Export vidéo |
| Failover Trigger | cmd-point | - | TRIGGER | Binaire | Basculement manuel |
| System Restart | cmd-point | - | TRIGGER | Binaire | Redémarrage système |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| System Status | status-point | Enum | OK/WARNING/CRITICAL/FAULT | État général |
| Recording Status | status-point | Enum | OK/PARTIAL/STOPPED/FAULT | État enregistrement |
| Storage Status | status-point | Enum | OK/LOW/CRITICAL/FAULT | État stockage |
| Database Status | status-point | Enum | OK/WARNING/FAULT | État base données |
| License Status | status-point | Enum | VALID/WARNING/EXPIRED | État licence |
| Failover Status | status-point | Enum | PRIMARY/SECONDARY/FAILED | État basculement |
| Archive Status | status-point | Enum | OK/ARCHIVING/FAULT | État archivage |
| Health Score | status-point | Enum | HEALTHY/DEGRADED/CRITICAL | Score santé global |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | ONVIF |
|-------|---------------|-----------------|-------|
| Total Cameras | AI0 | 30001 | GetRecordingConfiguration |
| Online Cameras | AI1 | 30002 | - |
| Storage Used | AI2 | 30003 | GetStorageConfiguration |
| System Status | MSV0 | 40001 | GetServiceCapabilities |
| Recording Status | MSV1 | 40002 | GetRecordingStatus |
| Storage Status | MSV2 | 40003 | - |
| Recording Global | BO0 | 00001 | SetRecordingJobMode |

## Sources
- [ONVIF Recording Control](https://www.onvif.org/)
- [EN 62676 Video Surveillance](https://www.en-standard.eu/)
- [IEC 62676-2-3 Video Transmission](https://webstore.iec.ch/)
