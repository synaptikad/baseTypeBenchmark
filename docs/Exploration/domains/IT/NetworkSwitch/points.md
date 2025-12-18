# Points de Network Switch

## Synthèse
- **Total points mesure** : 10
- **Total points commande** : 5
- **Total points état** : 9

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| CPU Usage | sensor-point | % | 0-100% | 30s | Utilisation processeur switch |
| Memory Usage | sensor-point | % | 0-100% | 30s | Utilisation mémoire |
| Temperature | sensor-temp-point | °C | 20-70°C | 1min | Température interne |
| Power Consumption | sensor-elec-power-point | W | 20-1000 W | 1min | Consommation électrique |
| Total Throughput | sensor-point | Gbps | 0-400 | 10s | Débit total agrégé |
| Packets Per Second | sensor-point | Mpps | 0-500 | 10s | Paquets traités/seconde |
| Port Utilization Avg | sensor-point | % | 0-100% | 1min | Utilisation moyenne ports |
| Uptime | sensor-point | h | 0-999999 | 1h | Temps fonctionnement |
| Error Rate | sensor-point | errors/s | 0-1000 | 1min | Taux d'erreurs réseau |
| Fan Speed | sensor-point | RPM | 0-10000 | 1min | Vitesse ventilateurs |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Port Enable | cmd-point | - | ENABLE/DISABLE | Binaire | Activation/désactivation port |
| PoE Enable | cmd-point | - | ENABLE/DISABLE | Binaire | Activation PoE sur port |
| VLAN Assignment | cmd-point | - | VLAN_ID | Analog | Affectation VLAN |
| LED Identify | cmd-point | - | ON/OFF | Binaire | LED identification |
| Reboot | cmd-point | - | REBOOT | Binaire | Redémarrage switch |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Switch Status | status-point | Enum | OK/WARNING/CRITICAL/OFFLINE | État général switch |
| Stack Status | status-point | Enum | MASTER/MEMBER/STANDALONE | Rôle dans le stack |
| Port Status | status-point | Enum | UP/DOWN/DISABLED | État port (par port) |
| SFP Status | status-point | Enum | OK/NOT_PRESENT/FAULT | État module SFP |
| PoE Status | status-point | Enum | DELIVERING/DISABLED/FAULT | État PoE port |
| PSU1 Status | status-point | Enum | OK/FAULT/ABSENT | État alimentation 1 |
| PSU2 Status | status-point | Enum | OK/FAULT/ABSENT | État alimentation 2 |
| Fan Status | status-point | Enum | OK/DEGRADED/FAILED | État ventilation |
| Config Sync Status | status-point | Enum | SYNCED/OUT_OF_SYNC | État synchronisation config |

## Mappings Protocoles
| Point | SNMP OID | Modbus |
|-------|----------|--------|
| CPU Usage | .1.3.6.1.4.1.x.cpu | - |
| Memory Usage | .1.3.6.1.4.1.x.memory | - |
| Temperature | .1.3.6.1.4.1.x.temp | 40001 |
| Power Consumption | .1.3.6.1.4.1.x.power | 40002 |
| Port Status | ifOperStatus (.1.3.6.1.2.1.2.2.1.8) | - |
| Total Throughput | ifHCInOctets/ifHCOutOctets | - |
| Switch Status | entPhysicalStatus | 40010 |
| Uptime | sysUpTime (.1.3.6.1.2.1.1.3) | - |

## Sources
- [SNMP IF-MIB RFC 2863](https://tools.ietf.org/html/rfc2863)
- [IEEE 802.3 Ethernet](https://www.ieee802.org/3/)
- [Cisco IOS MIB Reference](https://www.cisco.com/c/en/us/support/docs/ip/simple-network-management-protocol-snmp/9226-mibs-9226.html)
