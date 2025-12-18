# Points de Firewall

## Synthèse
- **Total points mesure** : 12
- **Total points commande** : 6
- **Total points état** : 11

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| CPU Usage | sensor-point | % | 0-100% | 30s | Utilisation processeur |
| Memory Usage | sensor-point | % | 0-100% | 30s | Utilisation mémoire |
| Temperature | sensor-temp-point | °C | 20-70°C | 1min | Température interne |
| Power Consumption | sensor-elec-power-point | W | 100-2000 W | 1min | Consommation électrique |
| Throughput | sensor-point | Gbps | 0-100 | 10s | Débit total filtré |
| Connections Per Second | sensor-point | conn/s | 0-500000 | 10s | Nouvelles connexions/s |
| Active Sessions | sensor-point | count | 0-10000000 | 30s | Sessions actives |
| Blocked Threats | sensor-point | count/h | 0-100000 | 1h | Menaces bloquées/heure |
| VPN Tunnels Active | sensor-point | count | 0-10000 | 1min | Tunnels VPN actifs |
| SSL Inspection Rate | sensor-point | Mbps | 0-10000 | 30s | Débit inspection SSL |
| IPS Events | sensor-point | events/h | 0-100000 | 1h | Événements IPS/heure |
| Uptime | sensor-point | h | 0-999999 | 1h | Temps fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Interface Enable | cmd-point | - | ENABLE/DISABLE | Binaire | Activation interface |
| Policy Enable | cmd-point | - | ENABLE/DISABLE | Binaire | Activation politique |
| IPS Enable | cmd-point | - | ENABLE/DISABLE | Binaire | Activation IPS |
| SSL Inspection | cmd-point | - | ENABLE/DISABLE | Binaire | Activation inspection SSL |
| HA Failover | cmd-point | - | TRIGGER | Binaire | Forçage basculement HA |
| Reboot | cmd-point | - | REBOOT | Binaire | Redémarrage firewall |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Firewall Status | status-point | Enum | OK/WARNING/CRITICAL/OFFLINE | État général |
| HA Status | status-point | Enum | ACTIVE/STANDBY/STANDALONE | État haute disponibilité |
| HA Sync Status | status-point | Enum | SYNCED/OUT_OF_SYNC | État synchronisation HA |
| Interface Status | status-point | Enum | UP/DOWN/DISABLED | État interface (par IF) |
| VPN Status | status-point | Enum | ALL_UP/PARTIAL/ALL_DOWN | État global VPN |
| IPS Status | status-point | Enum | ACTIVE/DISABLED/FAULT | État IPS |
| License Status | status-point | Enum | VALID/EXPIRING/EXPIRED | État licence |
| Signature Update | status-point | Enum | CURRENT/OUTDATED | État signatures menaces |
| PSU1 Status | status-point | Enum | OK/FAULT/ABSENT | État alimentation 1 |
| PSU2 Status | status-point | Enum | OK/FAULT/ABSENT | État alimentation 2 |
| Cluster Status | status-point | Enum | HEALTHY/DEGRADED/FAULT | État cluster |

## Mappings Protocoles
| Point | SNMP OID | Modbus |
|-------|----------|--------|
| CPU Usage | fgSysCpuUsage (.1.3.6.1.4.1.12356.101.4.1.3) | - |
| Memory Usage | fgSysMemUsage (.1.3.6.1.4.1.12356.101.4.1.4) | - |
| Active Sessions | fgSysSesCount | - |
| Throughput | - | 40001-40002 |
| HA Status | fgHaSystemMode | - |
| Firewall Status | fgSystemStatus | 40010 |
| VPN Tunnels Active | fgVpnTunNum | - |
| Uptime | sysUpTime | - |

## Sources
- [FortiGate MIB Reference](https://docs.fortinet.com/)
- [Palo Alto PAN-OS MIB](https://docs.paloaltonetworks.com/)
- [Check Point SNMP MIB](https://supportcenter.checkpoint.com/)
