# Points de NAS (Network Attached Storage)

## Synthèse
- **Total points mesure** : 12
- **Total points commande** : 5
- **Total points état** : 10

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| CPU Usage | sensor-point | % | 0-100% | 30s | Utilisation processeur |
| Memory Usage | sensor-point | % | 0-100% | 30s | Utilisation mémoire |
| System Temperature | sensor-temp-point | °C | 25-50°C | 1min | Température système |
| Disk Temperature | sensor-temp-point | °C | 25-55°C | 1min | Température disques (moyenne) |
| Power Consumption | sensor-elec-power-point | W | 50-500 W | 1min | Consommation électrique |
| Storage Capacity | sensor-point | TB | 0-1000 | 1h | Capacité totale |
| Storage Used | sensor-point | % | 0-100% | 5min | Utilisation stockage |
| Network Throughput | sensor-point | MBps | 0-10000 | 10s | Débit réseau |
| Disk IOPS | sensor-point | IOPS | 0-500000 | 30s | Opérations I/O disque |
| Disk Latency | sensor-point | ms | 0-100 | 30s | Latence I/O |
| Fan Speed | sensor-point | RPM | 0-5000 | 1min | Vitesse ventilateurs |
| Uptime | sensor-point | h | 0-999999 | 1h | Temps fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Power Control | cmd-point | - | ON/OFF/RESTART | Enum | Contrôle alimentation |
| Disk Spin Down | cmd-point | - | SPIN_DOWN | Binaire | Mise en veille disques |
| Volume Enable | cmd-point | - | ENABLE/DISABLE | Binaire | Activation volume |
| Scrub Start | cmd-point | - | START | Binaire | Lancement vérification RAID |
| LED Identify | cmd-point | - | ON/OFF | Binaire | LED identification |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| NAS Status | status-point | Enum | OK/WARNING/CRITICAL/OFFLINE | État général |
| Volume Status | status-point | Enum | HEALTHY/DEGRADED/FAILED | État volume (par vol) |
| RAID Status | status-point | Enum | OPTIMAL/DEGRADED/REBUILDING/FAILED | État RAID |
| Disk Status | status-point | Enum | OK/PREDICTIVE_FAIL/FAILED | État disque (par disque) |
| Network Status | status-point | Enum | OK/DEGRADED/FAILED | État réseau |
| PSU Status | status-point | Enum | OK/FAULT/REDUNDANCY_LOST | État alimentation |
| Fan Status | status-point | Enum | OK/DEGRADED/FAILED | État ventilation |
| Backup Status | status-point | Enum | OK/IN_PROGRESS/FAILED | État sauvegarde |
| Replication Status | status-point | Enum | SYNCED/SYNCING/FAILED | État réplication |
| UPS Status | status-point | Enum | OK/ON_BATTERY/LOW_BATTERY | État UPS connecté |

## Mappings Protocoles
| Point | SNMP OID | Modbus |
|-------|----------|--------|
| CPU Usage | synoCpuUsage (Synology) | - |
| Memory Usage | synoMemUsage | - |
| System Temperature | synoSystemTemperature | 40001 |
| Storage Used | synoStorageUsedPercent | 40002 |
| Volume Status | synoRaidStatus | - |
| Disk Status | synoDiskHealthStatus | - |
| NAS Status | synoSystemStatus | 40010 |
| Uptime | sysUpTime | - |

## Sources
- [Synology MIB Reference](https://www.synology.com/)
- [QNAP SNMP MIB](https://www.qnap.com/)
- [NetApp ONTAP API](https://docs.netapp.com/)
