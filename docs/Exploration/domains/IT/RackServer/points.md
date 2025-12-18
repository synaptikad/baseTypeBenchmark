# Points de Rack Server

## Synthèse
- **Total points mesure** : 14
- **Total points commande** : 6
- **Total points état** : 12

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| CPU Usage | sensor-point | % | 0-100% | 30s | Utilisation processeur moyenne |
| CPU Temperature | sensor-temp-point | °C | 30-95°C | 30s | Température processeur |
| Memory Usage | sensor-point | % | 0-100% | 30s | Utilisation mémoire RAM |
| Memory Temperature | sensor-temp-point | °C | 30-85°C | 1min | Température modules mémoire |
| Power Consumption | sensor-elec-power-point | W | 100-2000 W | 1min | Consommation électrique totale |
| Power Supply Voltage | sensor-elec-volt-point | V | 11.5-12.5 V | 1min | Tension alimentation interne |
| Fan Speed | sensor-point | RPM | 0-20000 | 30s | Vitesse ventilateurs |
| Inlet Temperature | sensor-temp-point | °C | 15-35°C | 1min | Température air entrée |
| Exhaust Temperature | sensor-temp-point | °C | 25-60°C | 1min | Température air sortie |
| Network Throughput | sensor-point | Mbps | 0-100000 | 30s | Débit réseau total |
| Disk I/O | sensor-point | IOPS | 0-1000000 | 30s | Opérations I/O disque |
| Storage Usage | sensor-point | % | 0-100% | 5min | Utilisation stockage |
| RAID Health Score | sensor-point | % | 0-100% | 5min | Score santé RAID |
| Uptime | sensor-point | h | 0-999999 | 1h | Temps fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Power Control | cmd-point | - | ON/OFF/RESET/CYCLE | Enum | Contrôle alimentation |
| LED Identify | cmd-point | - | ON/OFF/BLINK | Enum | LED identification |
| Fan Speed Override | cmd-sp-point | % | 0-100% | Analog | Forçage ventilateurs |
| Power Capping | cmd-sp-point | W | 200-2000 | Analog | Limitation puissance |
| Boot Device | cmd-point | - | HDD/SSD/PXE/USB/CD | Enum | Périphérique boot |
| BIOS Setup Enter | cmd-point | - | TRIGGER | Binaire | Entrer BIOS au reboot |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Server Status | status-point | Enum | RUNNING/STOPPED/STANDBY/FAULT | État général |
| Health Status | status-point | Enum | OK/WARNING/CRITICAL | Santé système |
| Power State | status-point | Enum | ON/OFF/STANDBY | État alimentation |
| PSU1 Status | status-point | Enum | OK/DEGRADED/FAILED/ABSENT | État alimentation 1 |
| PSU2 Status | status-point | Enum | OK/DEGRADED/FAILED/ABSENT | État alimentation 2 |
| CPU Status | status-point | Enum | OK/DEGRADED/FAILED | État processeur |
| Memory Status | status-point | Enum | OK/DEGRADED/FAILED | État mémoire |
| Storage Status | status-point | Enum | OK/DEGRADED/FAILED | État stockage |
| RAID Status | status-point | Enum | OPTIMAL/DEGRADED/FAILED | État RAID |
| Network Status | status-point | Enum | OK/DEGRADED/FAILED | État réseau |
| Thermal Status | status-point | Enum | OK/WARNING/CRITICAL | État thermique |
| BMC Connection | status-point | Enum | CONNECTED/DISCONNECTED | État BMC |

## Mappings Protocoles
| Point | SNMP OID | Redfish | IPMI |
|-------|----------|---------|------|
| CPU Usage | hrProcessorLoad | Processor/ProcessorStatistics | - |
| CPU Temperature | - | Thermal/Temperatures | Get Sensor Reading (0x01) |
| Power Consumption | - | Power/PowerControl/PowerConsumedWatts | Get Power Reading |
| Server Status | - | Systems/{id}/Status/State | Chassis Status |
| Health Status | - | Systems/{id}/Status/Health | - |
| Power Control | - | Systems/{id}/Actions/Reset | Chassis Control |
| RAID Status | - | Storage/Volumes | - |
| PSU1 Status | - | Chassis/Power/PowerSupplies | Get FRU |

## Sources
- [DMTF Redfish API Specification](https://www.dmtf.org/standards/redfish)
- [IPMI Specification v2.0](https://www.intel.com/content/www/us/en/servers/ipmi/ipmi-specifications.html)
- [SNMP MIB-II RFC 1213](https://tools.ietf.org/html/rfc1213)
