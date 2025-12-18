# Points de Bollard (Borne escamotable)

## Synthèse
- **Total points mesure** : 4
- **Total points commande** : 4
- **Total points état** : 6

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Position | sensor-point | % | 0-100% | 500ms | Position borne |
| Cycle Count | sensor-point | count | 0-999999 | Sur événement | Compteur cycles |
| Hydraulic Pressure | sensor-pressure-point | bar | 0-200 | 1s | Pression hydraulique |
| Operating Hours | sensor-point | h | 0-99999 | 1h | Heures fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Raise Command | cmd-point | - | TRIGGER | Binaire | Ordre montée |
| Lower Command | cmd-point | - | TRIGGER | Binaire | Ordre descente |
| Emergency Lower | cmd-point | - | TRIGGER | Binaire | Descente urgence |
| Mode Select | cmd-sp-point | - | AUTO/MANUAL/EMERGENCY | Enum | Mode fonctionnement |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Bollard Status | status-point | Enum | RAISED/LOWERED/TRANSIT/FAULT | État général |
| Raised Position | status-point | Boolean | FALSE/TRUE | Position haute |
| Lowered Position | status-point | Boolean | FALSE/TRUE | Position basse |
| Obstacle Detected | status-point | Boolean | FALSE/TRUE | Obstacle détecté |
| Hydraulic Status | status-point | Enum | OK/LOW/FAULT | État hydraulique |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| Position | AI0 | 30001 |
| Hydraulic Pressure | AI1 | 30002 |
| Bollard Status | MSV0 | 40001 |
| Raised Position | BI0 | 10001 |
| Lowered Position | BI1 | 10002 |
| Raise Command | BO0 | 00001 |
| Lower Command | BO1 | 00002 |

## Sources
- [PAS 68 Vehicle Security Barriers](https://www.bsigroup.com/)
- [IWA 14 Vehicle Security Barriers](https://www.iso.org/)
- [EN 12453 Industrial Doors](https://www.en-standard.eu/)
