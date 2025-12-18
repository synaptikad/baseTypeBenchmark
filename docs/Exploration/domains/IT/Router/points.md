# Points de Router

## Synthèse
- **Total points mesure** : 11
- **Total points commande** : 5
- **Total points état** : 10

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| CPU Usage | sensor-point | % | 0-100% | 30s | Utilisation processeur |
| Memory Usage | sensor-point | % | 0-100% | 30s | Utilisation mémoire |
| Temperature | sensor-temp-point | °C | 20-70°C | 1min | Température interne |
| Power Consumption | sensor-elec-power-point | W | 50-500 W | 1min | Consommation électrique |
| WAN Throughput In | sensor-point | Mbps | 0-10000 | 10s | Débit entrant WAN |
| WAN Throughput Out | sensor-point | Mbps | 0-10000 | 10s | Débit sortant WAN |
| LAN Throughput | sensor-point | Gbps | 0-100 | 10s | Débit total LAN |
| Active Sessions | sensor-point | count | 0-1000000 | 30s | Sessions NAT actives |
| Packets Per Second | sensor-point | kpps | 0-5000 | 10s | Paquets routés/seconde |
| Routing Table Size | sensor-point | routes | 0-1000000 | 5min | Nombre routes BGP/OSPF |
| Uptime | sensor-point | h | 0-999999 | 1h | Temps fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Interface Enable | cmd-point | - | ENABLE/DISABLE | Binaire | Activation interface |
| Routing Enable | cmd-point | - | ENABLE/DISABLE | Binaire | Activation routage |
| LED Identify | cmd-point | - | ON/OFF | Binaire | LED identification |
| Config Backup | cmd-point | - | BACKUP | Binaire | Sauvegarde configuration |
| Reboot | cmd-point | - | REBOOT | Binaire | Redémarrage routeur |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Router Status | status-point | Enum | OK/WARNING/CRITICAL/OFFLINE | État général |
| WAN Status | status-point | Enum | UP/DOWN/DEGRADED | État liaison WAN |
| LAN Status | status-point | Enum | UP/DOWN/DEGRADED | État interfaces LAN |
| BGP Status | status-point | Enum | ESTABLISHED/IDLE/ACTIVE | État session BGP |
| OSPF Status | status-point | Enum | FULL/2WAY/DOWN | État voisins OSPF |
| VPN Status | status-point | Enum | UP/DOWN/ESTABLISHING | État tunnels VPN |
| HA Status | status-point | Enum | ACTIVE/STANDBY/STANDALONE | État haute disponibilité |
| PSU Status | status-point | Enum | OK/FAULT/REDUNDANCY_LOST | État alimentation |
| Fan Status | status-point | Enum | OK/DEGRADED/FAILED | État ventilation |
| Config Status | status-point | Enum | SAVED/UNSAVED | État configuration |

## Mappings Protocoles
| Point | SNMP OID | Modbus |
|-------|----------|--------|
| CPU Usage | cpmCPUTotal5min (.1.3.6.1.4.1.9.9.109) | - |
| Memory Usage | ciscoMemoryPoolUsed | - |
| Temperature | ciscoEnvMonTemperatureValue | 40001 |
| Router Status | entPhysicalOperStatus | 40010 |
| WAN Throughput In | ifHCInOctets | - |
| WAN Throughput Out | ifHCOutOctets | - |
| BGP Status | bgpPeerState (.1.3.6.1.2.1.15.3.1.2) | - |
| Uptime | sysUpTime | - |

## Sources
- [SNMP BGP4-MIB RFC 4273](https://tools.ietf.org/html/rfc4273)
- [Cisco IOS MIB](https://www.cisco.com/c/en/us/support/docs/ip/simple-network-management-protocol-snmp/9226-mibs-9226.html)
- [Juniper JUNOS MIB](https://www.juniper.net/documentation/)
