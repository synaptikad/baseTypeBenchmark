# Points de Recording Server (Serveur enregistrement)

## Synthèse
- **Total points mesure** : 9
- **Total points commande** : 6
- **Total points état** : 7

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Active Recordings | sensor-point | count | 0-100 | 1s | Enregistrements actifs |
| Total Bitrate | sensor-point | Mbps | 0-1000 | 30s | Débit total |
| Storage Used | sensor-point | % | 0-100% | 5min | Stockage utilisé |
| Storage Available | sensor-point | TB | 0-100 | 5min | Stockage disponible |
| CPU Usage | sensor-point | % | 0-100% | 30s | Utilisation CPU |
| Memory Usage | sensor-point | % | 0-100% | 30s | Utilisation mémoire |
| Network Throughput | sensor-point | Mbps | 0-10000 | 30s | Débit réseau |
| Daily Recording Hours | sensor-point | h | 0-2400 | 1h | Heures enregistrées/jour |
| Uptime | sensor-point | h | 0-99999 | 1h | Temps fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Recording Enable | cmd-point | - | ON/OFF | Binaire | Activation enregistrement |
| Schedule Enable | cmd-point | - | ON/OFF | Binaire | Activation planification |
| Retention Days | cmd-sp-point | days | 1-365 | Analog | Durée rétention |
| Export Trigger | cmd-point | - | TRIGGER | Binaire | Export enregistrement |
| Storage Cleanup | cmd-point | - | TRIGGER | Binaire | Nettoyage stockage |
| System Restart | cmd-point | - | TRIGGER | Binaire | Redémarrage |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Server Status | status-point | Enum | OK/WARNING/FAULT | État général |
| Recording Status | status-point | Enum | RECORDING/SCHEDULED/STOPPED/FAULT | État enregistrement |
| Storage Status | status-point | Enum | OK/LOW/CRITICAL/FAULT | État stockage |
| Archive Status | status-point | Enum | OK/ARCHIVING/FAULT | État archivage |
| Network Status | status-point | Enum | OK/DEGRADED/FAULT | État réseau |
| RAID Status | status-point | Enum | OK/DEGRADED/REBUILDING/FAULT | État RAID |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | HTTP API |
|-------|---------------|-----------------|----------|
| Active Recordings | AI0 | 30001 | /api/recordings |
| Storage Used | AI1 | 30002 | /api/storage |
| Total Bitrate | AI2 | 30003 | /api/status |
| Server Status | MSV0 | 40001 | /api/status |
| Recording Status | MSV1 | 40002 | /api/recording |
| Recording Enable | BO0 | 00001 | /api/recording/start |

## Sources
- [SMPTE ST 2110](https://www.smpte.org/)
- [NDI Recording](https://www.ndi.tv/)
- [ONVIF Recording](https://www.onvif.org/)
