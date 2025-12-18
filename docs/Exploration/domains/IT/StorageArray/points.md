# Points de Storage Array

## Synthèse
- **Total points mesure** : 14
- **Total points commande** : 6
- **Total points état** : 12

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Controller CPU Usage | sensor-point | % | 0-100% | 30s | Utilisation CPU contrôleur |
| Controller Memory Usage | sensor-point | % | 0-100% | 30s | Utilisation mémoire contrôleur |
| Cache Hit Rate | sensor-point | % | 0-100% | 1min | Taux hit cache |
| Total Capacity | sensor-point | TB | 0-10000 | 1h | Capacité totale |
| Used Capacity | sensor-point | % | 0-100% | 5min | Utilisation capacité |
| IOPS | sensor-point | IOPS | 0-5000000 | 10s | Opérations I/O/seconde |
| Throughput | sensor-point | GBps | 0-100 | 10s | Débit total |
| Read Latency | sensor-point | ms | 0-50 | 30s | Latence lecture |
| Write Latency | sensor-point | ms | 0-50 | 30s | Latence écriture |
| Power Consumption | sensor-elec-power-point | W | 500-5000 W | 1min | Consommation électrique |
| Temperature | sensor-temp-point | °C | 20-40°C | 1min | Température interne |
| Fan Speed | sensor-point | RPM | 0-10000 | 1min | Vitesse ventilateurs |
| SSD Wear Level | sensor-point | % | 0-100% | 1h | Niveau usure SSD |
| Uptime | sensor-point | h | 0-999999 | 1h | Temps fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Controller Failover | cmd-point | - | TRIGGER | Binaire | Basculement contrôleur |
| Volume Enable | cmd-point | - | ENABLE/DISABLE | Binaire | Activation volume |
| Snapshot Create | cmd-point | - | CREATE | Binaire | Création snapshot |
| Rebuild Start | cmd-point | - | START | Binaire | Lancement reconstruction |
| LED Identify | cmd-point | - | ON/OFF | Binaire | LED identification |
| Power Control | cmd-point | - | ON/OFF | Binaire | Contrôle alimentation |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Array Status | status-point | Enum | OK/WARNING/CRITICAL/OFFLINE | État général |
| Controller A Status | status-point | Enum | ACTIVE/STANDBY/FAULT | État contrôleur A |
| Controller B Status | status-point | Enum | ACTIVE/STANDBY/FAULT | État contrôleur B |
| Volume Status | status-point | Enum | ONLINE/DEGRADED/OFFLINE | État volume (par vol) |
| Disk Group Status | status-point | Enum | OPTIMAL/DEGRADED/FAILED | État groupe disques |
| Disk Status | status-point | Enum | OK/PREDICTIVE_FAIL/FAILED | État disque (par slot) |
| PSU Status | status-point | Enum | OK/FAULT/ABSENT | État alimentation |
| Battery Status | status-point | Enum | OK/CHARGING/FAILED/EXPIRED | État batterie cache |
| Enclosure Status | status-point | Enum | OK/WARNING/CRITICAL | État boîtier |
| Replication Status | status-point | Enum | SYNCED/SYNCING/FAILED | État réplication |
| Connectivity Status | status-point | Enum | ALL_PATHS/DEGRADED/FAILED | État chemins SAN |
| License Status | status-point | Enum | VALID/EXPIRING/EXPIRED | État licence |

## Mappings Protocoles
| Point | SMI-S/WBEM | Redfish Storage |
|-------|------------|-----------------|
| Controller CPU Usage | CIM_ComputerSystem | Systems/Storage |
| IOPS | CIM_BlockStatisticalData | StorageControllers/Statistics |
| Array Status | CIM_StorageSystem.OperationalStatus | Storage/Status |
| Volume Status | CIM_StorageVolume.OperationalStatus | Volumes/Status |
| Disk Status | CIM_DiskDrive.OperationalStatus | Drives/Status |
| Throughput | CIM_BlockStatisticalData.KBytesTransferred | - |
| Cache Hit Rate | CIM_BlockStatisticalData.ReadHitIOTimeCounter | - |
| Replication Status | CIM_StorageSynchronized.SyncState | - |

## Sources
- [SNIA SMI-S Specification](https://www.snia.org/tech_activities/standards/curr_standards/smi)
- [DMTF Redfish Storage](https://www.dmtf.org/standards/redfish)
- [Dell EMC Unity API](https://www.dell.com/support/kbdoc/)
