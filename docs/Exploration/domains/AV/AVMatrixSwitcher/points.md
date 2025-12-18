# Points de AV Matrix Switcher (Matrice AV)

## Synthèse
- **Total points mesure** : 6
- **Total points commande** : 5
- **Total points état** : 6

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Inputs Count | sensor-point | count | 0-256 | Config | Nombre entrées |
| Outputs Count | sensor-point | count | 0-256 | Config | Nombre sorties |
| Active Routes | sensor-point | count | 0-256 | 1s | Routes actives |
| Temperature | sensor-temp-point | °C | 0-70°C | 30s | Température interne |
| Power Consumption | sensor-power-point | W | 0-500 | 1min | Consommation |
| Uptime | sensor-point | h | 0-99999 | 1h | Temps fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Route Set | cmd-sp-point | - | InxOut format | String | Configuration route |
| Preset Recall | cmd-sp-point | - | 1-100 | Analog | Rappel preset |
| Preset Save | cmd-sp-point | - | 1-100 | Analog | Sauvegarde preset |
| All Outputs Mute | cmd-point | - | ON/OFF | Binaire | Sourdine globale |
| System Reboot | cmd-point | - | TRIGGER | Binaire | Redémarrage |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Matrix Status | status-point | Enum | OK/WARNING/FAULT | État général |
| Current Routing | status-point | String | Route map | Routage actuel |
| Input Signal Status | status-point | Bitmask | Per input | Signaux entrée |
| Output Signal Status | status-point | Bitmask | Per output | Signaux sortie |
| HDCP Status | status-point | Enum | OK/FAULT | État HDCP |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | TCP/IP |
|-------|---------------|-----------------|--------|
| Active Routes | AI0 | 30001 | Query Routes |
| Temperature | AI1 | 30002 | Query Temp |
| Matrix Status | MSV0 | 40001 | Query Status |
| Route Set | MSV1 | 40002 | ROUTE In Out |
| Preset Recall | AO0 | 40101 | PRESET x |
| All Outputs Mute | BO0 | 00001 | MUTE ALL |

## Sources
- [HDMI 2.1 Specification](https://www.hdmi.org/)
- [HDBaseT Alliance](https://hdbaset.org/)
- [SMPTE ST 2110](https://www.smpte.org/)
