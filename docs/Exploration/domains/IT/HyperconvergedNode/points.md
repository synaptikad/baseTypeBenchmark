# Points de Hyperconverged Node

## Synthèse
- **Total points mesure** : 14
- **Total points commande** : 6
- **Total points état** : 11

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| CPU Usage | sensor-point | % | 0-100% | 30s | Utilisation CPU totale |
| Memory Usage | sensor-point | % | 0-100% | 30s | Utilisation mémoire |
| vCPU Ratio | sensor-point | ratio | 1:1-20:1 | 5min | Ratio vCPU/pCPU |
| Storage Used | sensor-point | % | 0-100% | 5min | Utilisation stockage local |
| Deduplication Ratio | sensor-point | ratio | 1:1-10:1 | 1h | Ratio déduplication |
| Compression Ratio | sensor-point | ratio | 1:1-5:1 | 1h | Ratio compression |
| IOPS | sensor-point | IOPS | 0-500000 | 30s | Opérations I/O |
| Network Throughput | sensor-point | Gbps | 0-100 | 10s | Débit réseau total |
| vMotion Traffic | sensor-point | Gbps | 0-25 | 1min | Trafic migration VM |
| Power Consumption | sensor-elec-power-point | W | 200-1500 W | 1min | Consommation électrique |
| Temperature | sensor-temp-point | °C | 25-50°C | 1min | Température interne |
| Fan Speed | sensor-point | RPM | 0-15000 | 1min | Vitesse ventilateurs |
| VM Count | sensor-point | count | 0-200 | 5min | Nombre VMs hébergées |
| Uptime | sensor-point | h | 0-999999 | 1h | Temps fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Maintenance Mode | cmd-point | - | ENTER/EXIT | Enum | Mode maintenance |
| Power Control | cmd-point | - | ON/OFF/RESTART | Enum | Contrôle alimentation |
| LED Identify | cmd-point | - | ON/OFF | Binaire | LED identification |
| DRS Enable | cmd-point | - | ENABLE/DISABLE | Binaire | Activation DRS |
| HA Enable | cmd-point | - | ENABLE/DISABLE | Binaire | Activation HA |
| Evacuate VMs | cmd-point | - | TRIGGER | Binaire | Migration toutes VMs |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Node Status | status-point | Enum | OK/WARNING/CRITICAL/OFFLINE | État général |
| Cluster Status | status-point | Enum | HEALTHY/DEGRADED/PARTITIONED | État cluster HCI |
| Witness Status | status-point | Enum | OK/ABSENT/FAULT | État witness |
| Storage Status | status-point | Enum | HEALTHY/DEGRADED/REBUILDING | État stockage |
| Network Status | status-point | Enum | OK/DEGRADED/FAULT | État réseau |
| PSU Status | status-point | Enum | OK/FAULT/REDUNDANCY_LOST | État alimentation |
| Fan Status | status-point | Enum | OK/DEGRADED/FAILED | État ventilation |
| VM Health | status-point | Enum | ALL_OK/SOME_ISSUES/CRITICAL | Santé VMs |
| Replication Status | status-point | Enum | SYNCED/SYNCING/FAILED | État réplication |
| Maintenance Status | status-point | Boolean | TRUE/FALSE | En maintenance |
| License Status | status-point | Enum | VALID/EXPIRING/EXPIRED | État licence |

## Mappings Protocoles
| Point | Redfish | vSphere API |
|-------|---------|-------------|
| CPU Usage | Processor/ProcessorStatistics | HostSystem.summary.quickStats.overallCpuUsage |
| Memory Usage | Memory/MemoryStatistics | HostSystem.summary.quickStats.overallMemoryUsage |
| Temperature | Thermal/Temperatures | HostSystem.runtime.healthSystemRuntime |
| Node Status | Systems/Status | HostSystem.overallStatus |
| Cluster Status | - | ClusterComputeResource.summary |
| VM Count | - | HostSystem.vm.length |
| Power Control | Systems/Actions/Reset | HostSystem.RebootHost_Task |
| Maintenance Mode | - | HostSystem.EnterMaintenanceMode_Task |

## Sources
- [VMware vSphere API Reference](https://developer.vmware.com/apis/vsphere-automation/latest/)
- [Nutanix Prism API](https://www.nutanix.dev/)
- [DMTF Redfish Specification](https://www.dmtf.org/standards/redfish)
