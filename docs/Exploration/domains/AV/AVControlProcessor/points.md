# Points de AV Control Processor (Processeur contrôle AV)

## Synthèse
- **Total points mesure** : 6
- **Total points commande** : 6
- **Total points état** : 6

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Controlled Devices | sensor-point | count | 0-256 | 1min | Équipements contrôlés |
| Active Programs | sensor-point | count | 0-50 | 1min | Programmes actifs |
| CPU Usage | sensor-point | % | 0-100% | 30s | Utilisation CPU |
| Memory Usage | sensor-point | % | 0-100% | 30s | Utilisation mémoire |
| Network Connections | sensor-point | count | 0-100 | 30s | Connexions réseau |
| Uptime | sensor-point | h | 0-99999 | 1h | Temps fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Power Enable | cmd-point | - | ON/OFF | Binaire | Mise sous tension |
| Scene Recall | cmd-sp-point | - | 1-100 | Analog | Rappel scène |
| Room Mode | cmd-sp-point | - | PRESENTATION/VIDEO/AUDIO/OFF | Enum | Mode salle |
| System Reboot | cmd-point | - | TRIGGER | Binaire | Redémarrage |
| Program Load | cmd-sp-point | - | Program ID | Analog | Chargement programme |
| Debug Mode | cmd-point | - | ON/OFF | Binaire | Mode debug |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Processor Status | status-point | Enum | OK/WARNING/FAULT | État général |
| Program Status | status-point | Enum | RUNNING/STOPPED/ERROR | État programme |
| Network Status | status-point | Enum | OK/DEGRADED/FAULT | État réseau |
| Current Scene | status-point | Enum | Scene name | Scène active |
| Current Mode | status-point | Enum | PRESENTATION/VIDEO/AUDIO/OFF | Mode actuel |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | TCP/IP |
|-------|---------------|-----------------|--------|
| Controlled Devices | AI0 | 30001 | Query |
| CPU Usage | AI1 | 30002 | Query |
| Processor Status | MSV0 | 40001 | Query |
| Scene Recall | AO0 | 40101 | SCENE x |
| Room Mode | MSV1 | 40002 | MODE x |
| Power Enable | BO0 | 00001 | POWER |

## Sources
- [Crestron SIMPL](https://www.crestron.com/)
- [AMX NetLinx](https://www.amx.com/)
- [SMPTE ST 2110](https://www.smpte.org/)
