# Points de Video Analytics Server (Serveur analyse vidéo)

## Synthèse
- **Total points mesure** : 10
- **Total points commande** : 5
- **Total points état** : 7

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Cameras Analyzed | sensor-point | count | 0-128 | 1min | Caméras analysées |
| Events Detected | sensor-point | count | 0-99999 | 1h | Événements détectés |
| Processing Rate | sensor-point | fps | 0-1000 | 30s | Taux traitement |
| CPU Usage | sensor-point | % | 0-100% | 30s | Utilisation CPU |
| GPU Usage | sensor-point | % | 0-100% | 30s | Utilisation GPU |
| Memory Usage | sensor-point | % | 0-100% | 30s | Utilisation mémoire |
| Network Throughput | sensor-point | Mbps | 0-10000 | 30s | Débit réseau |
| Average Latency | sensor-point | ms | 0-5000 | 1min | Latence moyenne |
| False Alarm Rate | sensor-point | % | 0-100% | 1h | Taux fausses alarmes |
| Uptime | sensor-point | h | 0-99999 | 1h | Temps fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Analytics Enable | cmd-point | - | ON/OFF | Binaire | Activation analyse |
| Rule Enable | cmd-sp-point | - | Rule bitmask | Analog | Activation règles |
| Sensitivity | cmd-sp-point | - | LOW/MEDIUM/HIGH | Enum | Sensibilité globale |
| Export Events | cmd-point | - | TRIGGER | Binaire | Export événements |
| Reboot | cmd-point | - | TRIGGER | Binaire | Redémarrage |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Server Status | status-point | Enum | OK/WARNING/FAULT | État général |
| Analytics Status | status-point | Enum | RUNNING/STOPPED/FAULT | État analyse |
| Motion Detection | status-point | Boolean | FALSE/TRUE | Mouvement détecté |
| Intrusion Detection | status-point | Boolean | FALSE/TRUE | Intrusion détectée |
| Face Detection | status-point | Boolean | FALSE/TRUE | Visage détecté |
| License Mode | status-point | Enum | VALID/EXPIRING/EXPIRED | État licence |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | ONVIF |
|-------|---------------|-----------------|-------|
| Cameras Analyzed | AI0 | 30001 | GetAnalyticsModules |
| Events Detected | AI1 | 30002 | - |
| Processing Rate | AI2 | 30003 | - |
| Server Status | MSV0 | 40001 | GetDeviceStatus |
| Motion Detection | BI0 | 10001 | MotionRegionDetector |
| Intrusion Detection | BI1 | 10002 | LineDetector |
| Analytics Enable | BO0 | 00001 | SetAnalyticsState |

## Sources
- [ONVIF Analytics Service](https://www.onvif.org/)
- [EN 62676 Video Content Analytics](https://www.en-standard.eu/)
