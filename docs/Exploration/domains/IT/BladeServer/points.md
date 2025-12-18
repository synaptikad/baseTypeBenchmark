# Points de Blade Server

## Synthèse
- **Total points mesure** : 12
- **Total points commande** : 5
- **Total points état** : 10

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| CPU Usage | sensor-point | % | 0-100% | 30s | Utilisation processeur moyenne |
| CPU Temperature | sensor-temp-point | °C | 30-95°C | 30s | Température processeur |
| Memory Usage | sensor-point | % | 0-100% | 30s | Utilisation mémoire RAM |
| Memory Temperature | sensor-temp-point | °C | 30-85°C | 1min | Température modules mémoire |
| Power Consumption | sensor-elec-power-point | W | 50-500 W | 1min | Consommation électrique lame |
| Fan Speed | sensor-point | RPM | 0-15000 | 30s | Vitesse ventilateurs internes |
| Inlet Temperature | sensor-temp-point | °C | 15-35°C | 1min | Température air entrée |
| Exhaust Temperature | sensor-temp-point | °C | 25-55°C | 1min | Température air sortie |
| Network Throughput | sensor-point | Mbps | 0-100000 | 30s | Débit réseau total |
| Disk I/O | sensor-point | IOPS | 0-1000000 | 30s | Opérations I/O disque |
| Storage Usage | sensor-point | % | 0-100% | 5min | Utilisation stockage local |
| Uptime | sensor-point | h | 0-999999 | 1h | Temps fonctionnement depuis boot |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Power Control | cmd-point | - | ON/OFF/RESET | Enum | Contrôle alimentation |
| LED Identify | cmd-point | - | ON/OFF | Binaire | LED identification physique |
| Fan Speed Override | cmd-sp-point | % | 0-100% | Analog | Forçage vitesse ventilateurs |
| Power Capping | cmd-sp-point | W | 100-500 | Analog | Limitation puissance max |
| Boot Device | cmd-point | - | HDD/SSD/PXE/USB | Enum | Périphérique de démarrage |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Server Status | status-point | Enum | RUNNING/STOPPED/STANDBY/FAULT | État général serveur |
| Health Status | status-point | Enum | OK/WARNING/CRITICAL | Santé système globale |
| Power State | status-point | Enum | ON/OFF/STANDBY | État alimentation |
| CPU Status | status-point | Enum | OK/DEGRADED/FAILED | État processeur |
| Memory Status | status-point | Enum | OK/DEGRADED/FAILED | État mémoire |
| Storage Status | status-point | Enum | OK/DEGRADED/FAILED | État stockage |
| Network Status | status-point | Enum | OK/DEGRADED/FAILED | État réseau |
| Thermal Status | status-point | Enum | OK/WARNING/CRITICAL | État thermique |
| Fan Status | status-point | Enum | OK/DEGRADED/FAILED | État ventilateurs |
| BMC Connection | status-point | Enum | CONNECTED/DISCONNECTED | État connexion BMC/iLO/iDRAC |

## Mappings Protocoles
| Point | SNMP OID | Redfish | IPMI |
|-------|----------|---------|------|
| CPU Usage | hrProcessorLoad | Processor/ProcessorStatistics | - |
| CPU Temperature | - | Thermal/Temperatures | Get Sensor Reading |
| Power Consumption | - | Power/PowerControl | Get Power Reading |
| Server Status | - | Systems/Status | Chassis Status |
| Health Status | - | Systems/Status/Health | Get System GUID |
| Power Control | - | Systems/Actions/Reset | Chassis Control |
| Fan Speed | - | Thermal/Fans | Get Sensor Reading |
| LED Identify | - | Chassis/Actions/SetIndicatorLED | Chassis Identify |

## Sources
- [DMTF Redfish API Specification](https://www.dmtf.org/standards/redfish)
- [IPMI Specification v2.0](https://www.intel.com/content/www/us/en/servers/ipmi/ipmi-specifications.html)
- [SNMP MIB-II](https://tools.ietf.org/html/rfc1213)
