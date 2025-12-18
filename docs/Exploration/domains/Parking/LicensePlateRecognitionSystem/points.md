# Points de License Plate Recognition System

## Synthèse
- **Total points mesure** : 10
- **Total points commande** : 6
- **Total points état** : 9

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Recognition Rate | sensor-point | % | 0-100% | 1min | Taux de reconnaissance réussie |
| Processing Time | sensor-point | ms | 50-1000 ms | Sur événement | Temps traitement OCR |
| Confidence Score | sensor-point | % | 0-100% | Sur événement | Score confiance reconnaissance |
| Total Recognitions | sensor-point | count | 0-999999 | 5min | Nombre total reconnaissances |
| Database Query Time | sensor-point | ms | 1-500 ms | Sur événement | Temps requête base de données |
| Camera Count Active | sensor-point | count | 0-50 | 1min | Nombre caméras actives |
| Server CPU Usage | sensor-point | % | 0-100% | 30s | Utilisation CPU serveur |
| Server Memory Usage | sensor-point | % | 0-100% | 30s | Utilisation mémoire serveur |
| Database Size | sensor-point | GB | 0-1000 GB | 1h | Taille base de données |
| API Response Time | sensor-point | ms | 10-500 ms | 1min | Temps réponse API |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Recognition Enable | cmd-point | - | ENABLE/DISABLE | Binaire | Activation/désactivation OCR |
| Recognition Mode | cmd-point | - | FAST/ACCURATE/BALANCED | Enum | Mode de reconnaissance |
| Database Sync | cmd-point | - | SYNC | Binaire | Synchronisation base données |
| Whitelist Update | cmd-point | - | UPDATE | Binaire | Mise à jour liste autorisées |
| Barrier Auto-Open | cmd-point | - | ENABLE/DISABLE | Binaire | Ouverture automatique barrière |
| Image Retention Days | cmd-sp-point | days | 1-365 | Analog | Durée conservation images |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| System Status | status-point | Enum | OK/DEGRADED/FAULT/OFFLINE | État général système LPR |
| OCR Engine Status | status-point | Enum | RUNNING/STOPPED/ERROR | État moteur OCR |
| Database Status | status-point | Enum | CONNECTED/DISCONNECTED/ERROR | État base de données |
| Last Plate Recognized | status-point | String | Alphanumeric | Dernière plaque reconnue |
| Last Recognition Time | status-point | Timestamp | ISO8601 | Horodatage dernière reconnaissance |
| Plate Authorized | status-point | Boolean | TRUE/FALSE | Plaque autorisée dans base |
| Camera Connection Count | status-point | Number | 0-50 | Nombre caméras connectées |
| Cloud Sync Status | status-point | Enum | SYNCED/SYNCING/ERROR | État synchronisation cloud |
| Storage Warning | status-point | Boolean | TRUE/FALSE | Alerte stockage faible |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| System Status | MSV0 | 40001 |
| Recognition Rate | AI0 | 40002 |
| Server CPU Usage | AI1 | 40003 |
| Server Memory Usage | AI2 | 40004 |
| Total Recognitions | AI3 | 40005-40006 |
| Recognition Enable | BO0 | 00001 |
| Database Sync | BO1 | 00002 |
| OCR Engine Status | MSV1 | 40011 |

## Sources
- [ONVIF Specifications](https://www.onvif.org/)
- [Deep Learning OCR Documentation](https://github.com/openalpr/openalpr)
- [GDPR Data Privacy Guidelines](https://gdpr.eu/)
