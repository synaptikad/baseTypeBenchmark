# Points de SAN Switch (Fibre Channel)

## Synthèse
- **Total points mesure** : 10
- **Total points commande** : 5
- **Total points état** : 9

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| CPU Usage | sensor-point | % | 0-100% | 30s | Utilisation processeur |
| Memory Usage | sensor-point | % | 0-100% | 30s | Utilisation mémoire |
| Temperature | sensor-temp-point | °C | 20-60°C | 1min | Température interne |
| Power Consumption | sensor-elec-power-point | W | 100-1000 W | 1min | Consommation électrique |
| Total Throughput | sensor-point | Gbps | 0-1000 | 10s | Débit total fabric |
| Port Throughput | sensor-point | Gbps | 0-64 | 10s | Débit port (par port) |
| Frame Rate | sensor-point | Mfps | 0-500 | 10s | Trames/seconde |
| Port Errors | sensor-point | errors/s | 0-1000 | 1min | Erreurs port (par port) |
| CRC Errors | sensor-point | count | 0-999999 | 5min | Erreurs CRC cumulées |
| Uptime | sensor-point | h | 0-999999 | 1h | Temps fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Port Enable | cmd-point | - | ENABLE/DISABLE | Binaire | Activation port FC |
| Port Speed | cmd-point | - | AUTO/8G/16G/32G/64G | Enum | Vitesse port |
| Zone Enable | cmd-point | - | ENABLE/DISABLE | Binaire | Activation zone |
| LED Identify | cmd-point | - | ON/OFF | Binaire | LED identification |
| Reboot | cmd-point | - | REBOOT | Binaire | Redémarrage switch |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Switch Status | status-point | Enum | OK/WARNING/CRITICAL/OFFLINE | État général |
| Fabric Status | status-point | Enum | HEALTHY/DEGRADED/SEGMENTED | État fabric |
| Port Status | status-point | Enum | ONLINE/OFFLINE/BYPASS/DISABLED | État port (par port) |
| SFP Status | status-point | Enum | OK/NOT_PRESENT/FAULT | État SFP (par port) |
| ISL Status | status-point | Enum | UP/DOWN/DEGRADED | État liens inter-switch |
| PSU1 Status | status-point | Enum | OK/FAULT/ABSENT | État alimentation 1 |
| PSU2 Status | status-point | Enum | OK/FAULT/ABSENT | État alimentation 2 |
| Fan Status | status-point | Enum | OK/DEGRADED/FAILED | État ventilation |
| License Status | status-point | Enum | VALID/EXPIRING/EXPIRED | État licence |

## Mappings Protocoles
| Point | SNMP OID | Modbus |
|-------|----------|--------|
| CPU Usage | swCpuUsage (.1.3.6.1.4.1.1588.2.1.1.1.26) | - |
| Memory Usage | swMemUsage | - |
| Temperature | swSensorValue | 40001 |
| Port Status | swFCPortOpStatus | - |
| Switch Status | swOperStatus | 40010 |
| Total Throughput | swFCPortTxWords/RxWords | - |
| Frame Rate | swFCPortTxFrames/RxFrames | - |
| Port Errors | swFCPortCRCErrors | - |
| Uptime | sysUpTime | - |

## Sources
- [Brocade FOS MIB Reference](https://www.broadcom.com/)
- [Cisco MDS MIB Reference](https://www.cisco.com/)
- [FC-MI INCITS T11](https://www.t11.org/)
