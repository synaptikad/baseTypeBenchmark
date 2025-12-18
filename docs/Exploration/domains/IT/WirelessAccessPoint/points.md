# Points de Wireless Access Point

## Synthèse
- **Total points mesure** : 11
- **Total points commande** : 6
- **Total points état** : 9

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| CPU Usage | sensor-point | % | 0-100% | 30s | Utilisation processeur |
| Memory Usage | sensor-point | % | 0-100% | 30s | Utilisation mémoire |
| Client Count | sensor-point | count | 0-500 | 30s | Clients WiFi connectés |
| Throughput 2.4GHz | sensor-point | Mbps | 0-1000 | 10s | Débit bande 2.4 GHz |
| Throughput 5GHz | sensor-point | Mbps | 0-5000 | 10s | Débit bande 5 GHz |
| Throughput 6GHz | sensor-point | Mbps | 0-10000 | 10s | Débit bande 6 GHz (Wi-Fi 6E) |
| Channel Utilization | sensor-point | % | 0-100% | 1min | Utilisation canal (par radio) |
| Noise Floor | sensor-point | dBm | -100 à -60 | 1min | Plancher de bruit |
| Power Consumption | sensor-elec-power-point | W | 10-50 W | 1min | Consommation électrique |
| Temperature | sensor-temp-point | °C | 20-60°C | 1min | Température interne |
| Uptime | sensor-point | h | 0-999999 | 1h | Temps fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Radio Enable | cmd-point | - | ENABLE/DISABLE | Binaire | Activation radio (par bande) |
| TX Power | cmd-sp-point | dBm | 0-30 | Analog | Puissance émission |
| Channel | cmd-point | - | AUTO/1-165 | Enum | Canal (par radio) |
| SSID Enable | cmd-point | - | ENABLE/DISABLE | Binaire | Activation SSID |
| Client Disconnect | cmd-point | - | DISCONNECT | Binaire | Déconnexion client |
| Reboot | cmd-point | - | REBOOT | Binaire | Redémarrage AP |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| AP Status | status-point | Enum | OK/WARNING/CRITICAL/OFFLINE | État général |
| Radio Status 2.4GHz | status-point | Enum | UP/DOWN/DFS | État radio 2.4 GHz |
| Radio Status 5GHz | status-point | Enum | UP/DOWN/DFS | État radio 5 GHz |
| Radio Status 6GHz | status-point | Enum | UP/DOWN/AFC | État radio 6 GHz |
| Ethernet Status | status-point | Enum | UP/DOWN | État port Ethernet |
| PoE Status | status-point | Enum | OK/INSUFFICIENT/NOT_SUPPORTED | État PoE |
| Controller Connection | status-point | Enum | CONNECTED/DISCONNECTED | État connexion WLC |
| Mesh Status | status-point | Enum | ROOT/MESH/STANDALONE | État mesh |
| Rogue AP Detected | status-point | Boolean | TRUE/FALSE | AP pirate détecté |

## Mappings Protocoles
| Point | SNMP OID | Modbus |
|-------|----------|--------|
| CPU Usage | bsnAPCpuUsagePercent (.1.3.6.1.4.1.14179) | - |
| Memory Usage | bsnAPMemoryUsagePercent | - |
| Client Count | bsnAPNumOfUsers | 40001 |
| Channel Utilization | bsnAPIfChannelUtilization | - |
| AP Status | bsnAPOperationStatus | 40010 |
| Radio Status 5GHz | bsnAPIfOperStatus | - |
| Temperature | bsnAPInternalTemperature | 40002 |
| Uptime | sysUpTime | - |

## Sources
- [Cisco Wireless MIB Reference](https://www.cisco.com/)
- [Aruba AOS MIB](https://www.arubanetworks.com/)
- [IEEE 802.11ax (Wi-Fi 6)](https://www.ieee802.org/11/)
