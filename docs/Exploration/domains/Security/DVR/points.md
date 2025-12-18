# Points de DVR (Enregistreur vidéo numérique)

## Synthèse
- **Total points mesure** : 8
- **Total points commande** : 5
- **Total points état** : 7

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Channels Active | sensor-point | count | 0-32 | 1min | Canaux actifs |
| Recording Bitrate | sensor-point | Mbps | 0-100 | 1min | Débit enregistrement |
| Storage Used | sensor-point | % | 0-100% | 5min | Stockage utilisé |
| Storage Available | sensor-point | TB | 0-100 | 5min | Stockage disponible |
| CPU Usage | sensor-point | % | 0-100% | 30s | Utilisation CPU |
| System Temperature | sensor-temp-point | °C | 0-80°C | 1min | Température système |
| Network Throughput | sensor-point | Mbps | 0-1000 | 30s | Débit réseau |
| Uptime | sensor-point | h | 0-99999 | 1h | Temps fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Recording Enable | cmd-point | - | ON/OFF | Binaire | Activation enregistrement |
| Channel Enable | cmd-sp-point | - | Channel bitmask | Analog | Activation canaux |
| Retention Days | cmd-sp-point | days | 1-365 | Analog | Durée rétention |
| Export Trigger | cmd-point | - | TRIGGER | Binaire | Export vidéo |
| Reboot | cmd-point | - | TRIGGER | Binaire | Redémarrage |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| System Status | status-point | Enum | OK/WARNING/FAULT | État général |
| Recording Status | status-point | Enum | RECORDING/STOPPED/FAULT | État enregistrement |
| Storage Status | status-point | Enum | OK/LOW/FULL/FAULT | État stockage |
| Network Status | status-point | Enum | OK/DEGRADED/FAULT | État réseau |
| Fan Status | status-point | Enum | OK/FAULT | État ventilateur |
| RAID Status | status-point | Enum | OK/DEGRADED/FAULT | État RAID |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | ONVIF |
|-------|---------------|-----------------|-------|
| Channels Active | AI0 | 30001 | GetRecordingStatus |
| Storage Used | AI1 | 30002 | GetStorageConfiguration |
| System Status | MSV0 | 40001 | GetDeviceStatus |
| Recording Status | MSV1 | 40002 | GetRecordingStatus |
| Recording Enable | BO0 | 00001 | StartRecording |

## Sources
- [ONVIF Recording Control](https://www.onvif.org/)
- [EN 62676-4 Video Surveillance](https://www.en-standard.eu/)
