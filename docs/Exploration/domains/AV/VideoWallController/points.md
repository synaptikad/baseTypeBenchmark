# Points de Video Wall Controller (Contrôleur mur vidéo)

## Synthèse
- **Total points mesure** : 8
- **Total points commande** : 7
- **Total points état** : 6

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Displays Count | sensor-point | count | 1-100 | Config | Nombre écrans |
| Active Inputs | sensor-point | count | 0-32 | 1s | Entrées actives |
| Total Resolution | sensor-point | pixels | Various | Config | Résolution totale |
| Processing Load | sensor-point | % | 0-100% | 30s | Charge traitement |
| Temperature | sensor-temp-point | °C | 0-70°C | 30s | Température interne |
| Network Bandwidth | sensor-point | Mbps | 0-10000 | 30s | Bande passante |
| Frame Rate | sensor-point | fps | 0-60 | 1s | FPS sortie |
| Uptime | sensor-point | h | 0-99999 | 1h | Temps fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Layout Recall | cmd-sp-point | - | 1-100 | Analog | Rappel layout |
| Layout Save | cmd-sp-point | - | 1-100 | Analog | Sauvegarde layout |
| Window Create | cmd-sp-point | - | Input/Position | String | Création fenêtre |
| Window Close | cmd-sp-point | - | Window ID | Analog | Fermeture fenêtre |
| All Displays On | cmd-point | - | TRIGGER | Binaire | Allumer tous écrans |
| All Displays Off | cmd-point | - | TRIGGER | Binaire | Éteindre tous écrans |
| System Reboot | cmd-point | - | TRIGGER | Binaire | Redémarrage |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Controller Status | status-point | Enum | OK/WARNING/FAULT | État général |
| Processing Status | status-point | Enum | OK/OVERLOAD/FAULT | État traitement |
| Current Layout | status-point | Analog | 1-100 | Layout actif |
| Displays Status | status-point | Bitmask | Per display | État écrans |
| Inputs Status | status-point | Bitmask | Per input | État entrées |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | TCP/IP |
|-------|---------------|-----------------|--------|
| Displays Count | AI0 | 30001 | Query |
| Active Inputs | AI1 | 30002 | Query |
| Processing Load | AI2 | 30003 | Query |
| Controller Status | MSV0 | 40001 | Query |
| Current Layout | MSV1 | 40002 | Query |
| Layout Recall | AO0 | 40101 | LAYOUT x |

## Sources
- [HDMI 2.1 Specification](https://www.hdmi.org/)
- [DisplayPort MST](https://www.displayport.org/)
- [NDI Protocol](https://www.ndi.tv/)
