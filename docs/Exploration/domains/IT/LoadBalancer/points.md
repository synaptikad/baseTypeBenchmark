# Points de Load Balancer

## Synthèse
- **Total points mesure** : 11
- **Total points commande** : 5
- **Total points état** : 9

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| CPU Usage | sensor-point | % | 0-100% | 30s | Utilisation processeur |
| Memory Usage | sensor-point | % | 0-100% | 30s | Utilisation mémoire |
| Temperature | sensor-temp-point | °C | 20-70°C | 1min | Température interne |
| Power Consumption | sensor-elec-power-point | W | 100-1000 W | 1min | Consommation électrique |
| Total Throughput | sensor-point | Gbps | 0-100 | 10s | Débit total balancé |
| Connections Per Second | sensor-point | conn/s | 0-1000000 | 10s | Nouvelles connexions/s |
| Active Connections | sensor-point | count | 0-10000000 | 30s | Connexions actives |
| HTTP Requests/s | sensor-point | req/s | 0-1000000 | 10s | Requêtes HTTP/seconde |
| SSL TPS | sensor-point | tps | 0-100000 | 10s | Transactions SSL/s |
| Backend Response Time | sensor-point | ms | 0-5000 | 30s | Temps réponse backends |
| Uptime | sensor-point | h | 0-999999 | 1h | Temps fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| VIP Enable | cmd-point | - | ENABLE/DISABLE | Binaire | Activation VIP |
| Pool Member Enable | cmd-point | - | ENABLE/DISABLE | Binaire | Activation membre pool |
| Force Offline | cmd-point | - | FORCE | Binaire | Forcer membre offline |
| HA Failover | cmd-point | - | TRIGGER | Binaire | Basculement HA manuel |
| Reboot | cmd-point | - | REBOOT | Binaire | Redémarrage |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| LB Status | status-point | Enum | OK/WARNING/CRITICAL/OFFLINE | État général |
| HA Status | status-point | Enum | ACTIVE/STANDBY/STANDALONE | État HA |
| HA Sync Status | status-point | Enum | SYNCED/OUT_OF_SYNC | Synchronisation HA |
| VIP Status | status-point | Enum | UP/DOWN/DISABLED | État VIP (par VIP) |
| Pool Status | status-point | Enum | UP/DEGRADED/DOWN | État pool (par pool) |
| Pool Member Status | status-point | Enum | UP/DOWN/MAINTENANCE | État membre pool |
| SSL Status | status-point | Enum | OK/CERT_EXPIRING/CERT_EXPIRED | État certificats |
| License Status | status-point | Enum | VALID/EXPIRING/EXPIRED | État licence |
| Fan Status | status-point | Enum | OK/DEGRADED/FAILED | État ventilation |

## Mappings Protocoles
| Point | SNMP OID | Modbus |
|-------|----------|--------|
| CPU Usage | sysGlobalHostCpuUsageRatio (.1.3.6.1.4.1.3375) | - |
| Memory Usage | sysGlobalHostMemUsedRatio | - |
| Active Connections | sysStatClientCurConns | - |
| Total Throughput | sysStatClientBytesIn/Out | 40001-40002 |
| VIP Status | ltmVirtualServStatus | - |
| Pool Status | ltmPoolStatus | - |
| LB Status | sysPlatformStatus | 40010 |
| Uptime | sysUpTime | - |

## Sources
- [F5 BIG-IP MIB Reference](https://techdocs.f5.com/)
- [Citrix NetScaler MIB](https://docs.citrix.com/)
- [HAProxy Statistics](https://www.haproxy.com/documentation/)
