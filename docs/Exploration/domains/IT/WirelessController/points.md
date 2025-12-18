# Points de Wireless Controller (WLC)

## Synthèse
- **Total points mesure** : 12
- **Total points commande** : 6
- **Total points état** : 10

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| CPU Usage | sensor-point | % | 0-100% | 30s | Utilisation processeur |
| Memory Usage | sensor-point | % | 0-100% | 30s | Utilisation mémoire |
| Total AP Count | sensor-point | count | 0-10000 | 1min | APs gérés total |
| Active AP Count | sensor-point | count | 0-10000 | 1min | APs actifs |
| Total Client Count | sensor-point | count | 0-100000 | 30s | Clients WiFi totaux |
| Total Throughput | sensor-point | Gbps | 0-100 | 10s | Débit total WiFi |
| Authentication Rate | sensor-point | auth/s | 0-1000 | 1min | Authentifications/seconde |
| Roaming Events | sensor-point | events/min | 0-10000 | 1min | Événements roaming |
| Power Consumption | sensor-elec-power-point | W | 100-2000 W | 1min | Consommation électrique |
| Temperature | sensor-temp-point | °C | 20-50°C | 1min | Température interne |
| Rogue AP Count | sensor-point | count | 0-1000 | 5min | APs pirates détectés |
| Uptime | sensor-point | h | 0-999999 | 1h | Temps fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| AP Reboot | cmd-point | - | REBOOT | Binaire | Redémarrage AP (par AP) |
| WLAN Enable | cmd-point | - | ENABLE/DISABLE | Binaire | Activation WLAN |
| RF Profile Apply | cmd-point | - | APPLY | Binaire | Application profil RF |
| Client Disconnect | cmd-point | - | DISCONNECT | Binaire | Déconnexion client |
| HA Failover | cmd-point | - | TRIGGER | Binaire | Basculement HA |
| Reboot | cmd-point | - | REBOOT | Binaire | Redémarrage WLC |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| WLC Status | status-point | Enum | OK/WARNING/CRITICAL/OFFLINE | État général |
| HA Status | status-point | Enum | ACTIVE/STANDBY/STANDALONE | État haute disponibilité |
| HA Sync Status | status-point | Enum | SYNCED/OUT_OF_SYNC | Synchronisation HA |
| License Status | status-point | Enum | VALID/EXPIRING/EXPIRED | État licence |
| AP License Usage | status-point | Enum | OK/WARNING/EXCEEDED | Utilisation licences AP |
| RADIUS Status | status-point | Enum | ALL_UP/PARTIAL/ALL_DOWN | État serveurs RADIUS |
| DHCP Status | status-point | Enum | OK/POOL_LOW/EXHAUSTED | État pools DHCP |
| PSU Status | status-point | Enum | OK/FAULT/REDUNDANCY_LOST | État alimentation |
| Fan Status | status-point | Enum | OK/DEGRADED/FAILED | État ventilation |
| Cluster Status | status-point | Enum | HEALTHY/DEGRADED/PARTITIONED | État cluster WLC |

## Mappings Protocoles
| Point | SNMP OID | Modbus |
|-------|----------|--------|
| CPU Usage | clsCpuUsage (.1.3.6.1.4.1.9.9.618) | - |
| Memory Usage | clsMemoryUsage | - |
| Total AP Count | clsNumOfAPs | 40001 |
| Total Client Count | clsNumOfClients | 40002 |
| WLC Status | clsSystemStatus | 40010 |
| HA Status | cLHaPeerStatus (.1.3.6.1.4.1.9.9.843) | - |
| Total Throughput | clsTotalThroughput | 40003-40004 |
| Rogue AP Count | clsRogueAPCount | 40005 |

## Sources
- [Cisco WLC MIB Reference](https://www.cisco.com/)
- [Aruba Mobility Controller API](https://www.arubanetworks.com/)
- [Extreme Networks WiNG MIB](https://www.extremenetworks.com/)
