# Points de NVR (Enregistreur vidéo réseau)

## Synthèse
- **Total points mesure** : 9
- **Total points commande** : 6
- **Total points état** : 8

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Cameras Connected | sensor-point | count | 0-128 | 1min | Caméras connectées |
| Cameras Recording | sensor-point | count | 0-128 | 1min | Caméras enregistrant |
| Total Bitrate | sensor-point | Mbps | 0-500 | 30s | Débit total |
| Storage Used | sensor-point | % | 0-100% | 5min | Stockage utilisé |
| Storage Available | sensor-point | TB | 0-500 | 5min | Stockage disponible |
| CPU Usage | sensor-point | % | 0-100% | 30s | Utilisation CPU |
| Memory Usage | sensor-point | % | 0-100% | 30s | Utilisation mémoire |
| Network Throughput | sensor-point | Mbps | 0-10000 | 30s | Débit réseau |
| Uptime | sensor-point | h | 0-99999 | 1h | Temps fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Recording Enable | cmd-point | - | ON/OFF | Binaire | Activation enregistrement |
| Camera Enable | cmd-sp-point | - | Camera bitmask | Analog | Activation caméras |
| Retention Days | cmd-sp-point | days | 1-365 | Analog | Durée rétention |
| Failover Enable | cmd-point | - | ON/OFF | Binaire | Activation basculement |
| Export Trigger | cmd-point | - | TRIGGER | Binaire | Export vidéo |
| Reboot | cmd-point | - | TRIGGER | Binaire | Redémarrage |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| System Status | status-point | Enum | OK/WARNING/FAULT | État général |
| Recording Status | status-point | Enum | RECORDING/STOPPED/FAULT | État enregistrement |
| Storage Status | status-point | Enum | OK/LOW/FULL/FAULT | État stockage |
| RAID Status | status-point | Enum | OK/DEGRADED/REBUILDING/FAULT | État RAID |
| Failover Status | status-point | Enum | PRIMARY/SECONDARY/FAILED | État basculement |
| Network Status | status-point | Enum | OK/DEGRADED/FAULT | État réseau |
| Fan Status | status-point | Enum | OK/FAULT | État ventilateur |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | ONVIF |
|-------|---------------|-----------------|-------|
| Cameras Connected | AI0 | 30001 | GetRecordingSummary |
| Storage Used | AI1 | 30002 | GetStorageConfiguration |
| Total Bitrate | AI2 | 30003 | - |
| System Status | MSV0 | 40001 | GetDeviceStatus |
| Recording Status | MSV1 | 40002 | GetRecordingStatus |
| Recording Enable | BO0 | 00001 | CreateRecording |

## Sources
- [ONVIF Recording Control](https://www.onvif.org/)
- [EN 62676 Video Surveillance](https://www.en-standard.eu/)
