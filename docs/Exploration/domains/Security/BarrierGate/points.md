# Points de Barrier Gate (Barrière levante)

## Synthèse
- **Total points mesure** : 5
- **Total points commande** : 5
- **Total points état** : 7

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Position | sensor-point | % | 0-100% | 500ms | Position barrière |
| Opening Time | sensor-point | s | 0-10 | Sur événement | Temps ouverture |
| Cycle Count | sensor-point | count | 0-999999 | Sur événement | Compteur cycles |
| Motor Current | sensor-point | A | 0-10 | 1s | Courant moteur |
| Operating Hours | sensor-point | h | 0-99999 | 1h | Heures fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Open Command | cmd-point | - | TRIGGER | Binaire | Ordre ouverture |
| Close Command | cmd-point | - | TRIGGER | Binaire | Ordre fermeture |
| Stop Command | cmd-point | - | TRIGGER | Binaire | Arrêt immédiat |
| Hold Open | cmd-point | - | ON/OFF | Binaire | Maintien ouvert |
| Mode Select | cmd-sp-point | - | AUTO/MANUAL/FREE | Enum | Mode fonctionnement |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Barrier Status | status-point | Enum | OPEN/CLOSED/MOVING/FAULT | État général |
| Open Position | status-point | Boolean | FALSE/TRUE | Position ouverte |
| Closed Position | status-point | Boolean | FALSE/TRUE | Position fermée |
| Obstacle Detected | status-point | Boolean | FALSE/TRUE | Obstacle détecté |
| Loop Detector | status-point | Boolean | FALSE/TRUE | Véhicule présent |
| Motor Status | status-point | Enum | OK/OVERLOAD/FAULT | État moteur |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| Position | AI0 | 30001 |
| Barrier Status | MSV0 | 40001 |
| Open Position | BI0 | 10001 |
| Closed Position | BI1 | 10002 |
| Obstacle Detected | BI2 | 10003 |
| Open Command | BO0 | 00001 |
| Close Command | BO1 | 00002 |

## Sources
- [EN 12453 Industrial Doors Safety](https://www.en-standard.eu/)
- [EN 12604 Mechanical Aspects](https://www.en-standard.eu/)
