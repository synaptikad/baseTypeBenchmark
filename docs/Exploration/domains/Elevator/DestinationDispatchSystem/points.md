# Points de Destination Dispatch System

## Synthèse
- **Total points mesure** : 12
- **Total points commande** : 6
- **Total points état** : 10

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Average Wait Time | sensor-point | s | 0-120 | 1min | Temps attente moyen |
| Average Travel Time | sensor-point | s | 0-180 | 1min | Temps trajet moyen |
| Average System Time | sensor-point | s | 0-300 | 1min | Temps système total |
| Handling Capacity | sensor-point | persons/5min | 0-500 | 5min | Capacité de handling |
| Traffic Volume | sensor-point | persons/h | 0-5000 | 1h | Volume trafic horaire |
| Call Queue Size | sensor-point | count | 0-500 | 1s | Appels en file |
| Efficiency Score | sensor-point | % | 0-100% | 15min | Score efficacité |
| Energy Consumption | sensor-elec-energy-point | kWh | 0-999999 | 1h | Consommation groupe |
| Active Kiosks | sensor-point | count | 0-100 | 1min | Bornes actives |
| Card Reads | sensor-point | count/h | 0-5000 | 1h | Lectures cartes/heure |
| Recognition Rate | sensor-point | % | 0-100% | 1h | Taux reconnaissance |
| Uptime | sensor-point | h | 0-999999 | 1h | Temps fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Traffic Mode | cmd-point | - | NORMAL/UP_PEAK/DOWN_PEAK/LUNCH | Enum | Mode trafic |
| VIP Mode | cmd-point | - | ENABLE/DISABLE | Binaire | Mode VIP |
| Floor Restriction | cmd-point | floors | BITMASK | Binaire | Restriction étages |
| Algorithm Select | cmd-point | - | STANDARD/OPTIMIZED/ENERGY | Enum | Algorithme |
| Emergency Recall | cmd-point | floor | -5 à 100 | Analog | Rappel d'urgence |
| System Reset | cmd-point | - | RESET | Binaire | Réinitialisation |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| System Status | status-point | Enum | OK/DEGRADED/FAULT | État général |
| Server Status | status-point | Enum | RUNNING/STOPPED/FAULT | État serveur |
| Database Status | status-point | Enum | OK/SYNC_ERROR/OFFLINE | État base données |
| Access Control Status | status-point | Enum | CONNECTED/DISCONNECTED | État contrôle accès |
| Fire Mode Status | status-point | Enum | INACTIVE/PHASE1/PHASE2 | Mode incendie |
| Traffic Mode Active | status-point | Enum | NORMAL/UP_PEAK/DOWN_PEAK/LUNCH | Mode actif |
| Kiosk Status | status-point | Enum | ALL_OK/PARTIAL/ALL_DOWN | État bornes |
| Network Status | status-point | Enum | OK/DEGRADED/FAULT | État réseau |
| BMS Integration | status-point | Enum | CONNECTED/DISCONNECTED | État BMS |
| License Status | status-point | Enum | VALID/EXPIRING/EXPIRED | État licence |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | REST API |
|-------|---------------|-----------------|----------|
| System Status | MSV0 | 40001 | /api/status |
| Average Wait Time | AI0 | 40002 | /api/metrics/waitTime |
| Traffic Volume | AI1 | 40003 | /api/metrics/traffic |
| Efficiency Score | AI2 | 40004 | /api/metrics/efficiency |
| Traffic Mode | MSV1 | 40101 | /api/config/trafficMode |
| Fire Mode Status | MSV2 | 40010 | /api/status/fire |
| Call Queue Size | AI3 | 40005 | /api/queue/size |

## Sources
- [ASHRAE Guideline 20](https://www.ashrae.org/)
- [ISO 18738 Elevator Traffic](https://www.iso.org/)
- [Manufacturer APIs: Otis Compass, Schindler PORT, KONE DCS](https://www.elevatorworld.com/)
