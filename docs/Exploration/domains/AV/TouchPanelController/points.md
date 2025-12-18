# Points de Touch Panel Controller (Contrôleur panneau tactile)

## Synthèse
- **Total points mesure** : 6
- **Total points commande** : 5
- **Total points état** : 5

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Touch Count | sensor-point | count | 0-999999 | Sur événement | Compteur touches |
| Ambient Light | sensor-point | lux | 0-10000 | 1min | Luminosité ambiante |
| Proximity Detected | sensor-point | count | 0-999999 | Sur événement | Détections proximité |
| CPU Usage | sensor-point | % | 0-100% | 30s | Utilisation CPU |
| Memory Usage | sensor-point | % | 0-100% | 30s | Utilisation mémoire |
| Uptime | sensor-point | h | 0-99999 | 1h | Temps fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Page Navigate | cmd-sp-point | - | Page ID | Analog | Navigation page |
| Brightness | cmd-sp-point | % | 0-100% | Analog | Luminosité |
| Sleep Enable | cmd-point | - | ON/OFF | Binaire | Mode veille |
| System Reboot | cmd-point | - | TRIGGER | Binaire | Redémarrage |
| Project Load | cmd-sp-point | - | Project ID | Analog | Chargement projet |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Panel Status | status-point | Enum | OK/FAULT | État général |
| Display Status | status-point | Enum | ON/SLEEP/OFF | État affichage |
| Current Page | status-point | String | Page name | Page actuelle |
| Network Status | status-point | Enum | OK/FAULT | État réseau |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | TCP/IP |
|-------|---------------|-----------------|--------|
| Touch Count | AI0 | 30001 | Query |
| Ambient Light | AI1 | 30002 | Query |
| Panel Status | MSV0 | 40001 | Query |
| Current Page | MSV1 | 40002 | Query |
| Page Navigate | AO0 | 40101 | PAGE x |
| Brightness | AO1 | 40102 | BRT x |

## Sources
- [Crestron SIMPL](https://www.crestron.com/)
- [AMX NetLinx](https://www.amx.com/)
- [Extron Control](https://www.extron.com/)
