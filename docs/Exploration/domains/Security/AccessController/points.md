# Points de Access Controller (Contrôleur d'accès)

## Synthèse
- **Total points mesure** : 6
- **Total points commande** : 5
- **Total points état** : 7

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Doors Managed | sensor-point | count | 1-16 | 1min | Nombre portes gérées |
| Active Cardholders | sensor-point | count | 0-50000 | 1h | Badges actifs en base |
| Daily Transactions | sensor-point | count | 0-10000 | 1h | Transactions journalières |
| Failed Access Attempts | sensor-point | count | 0-1000 | 1h | Tentatives échouées |
| Battery Level | sensor-point | % | 0-100% | 1h | Niveau batterie secours |
| Memory Usage | sensor-point | % | 0-100% | 5min | Utilisation mémoire |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Global Unlock | cmd-point | - | TRIGGER | Binaire | Déverrouillage global |
| Global Lockdown | cmd-point | - | TRIGGER | Binaire | Verrouillage global |
| Mode Select | cmd-sp-point | - | NORMAL/LOCKDOWN/FREE_ACCESS | Enum | Mode fonctionnement |
| Time Sync | cmd-point | - | TRIGGER | Binaire | Synchronisation horloge |
| Database Sync | cmd-point | - | TRIGGER | Binaire | Synchronisation base |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Controller Status | status-point | Enum | ONLINE/OFFLINE/FAULT | État général |
| Operating Mode | status-point | Enum | NORMAL/LOCKDOWN/FREE_ACCESS | Mode actuel |
| Database Status | status-point | Enum | OK/SYNC/FAULT | État base données |
| Network Status | status-point | Enum | OK/DEGRADED/FAULT | État réseau |
| Tamper Status | status-point | Boolean | FALSE/TRUE | Sabotage détecté |
| Power Status | status-point | Enum | MAINS/BATTERY/FAULT | État alimentation |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | OSDP Protocol |
|-------|---------------|-----------------|---------------|
| Controller Status | MSV0 | 40001 | Status Poll |
| Operating Mode | MSV1 | 40002 | Mode Status |
| Tamper Status | BI0 | 10001 | Tamper Event |
| Global Unlock | BO0 | 00001 | Command 0x0200 |
| Global Lockdown | BO1 | 00002 | Command 0x0201 |

## Sources
- [EN 60839-11 Access Control](https://www.en-standard.eu/)
- [OSDP Standard](https://www.securityindustry.org/osdp/)
- [ONVIF Profile C](https://www.onvif.org/)
