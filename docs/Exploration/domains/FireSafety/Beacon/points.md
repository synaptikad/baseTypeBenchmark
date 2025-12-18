# Points de Beacon (Balise lumineuse)

## Synthèse
- **Total points mesure** : 2
- **Total points commande** : 3
- **Total points état** : 4

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Flash Count | sensor-point | count | 0-999999 | Sur événement | Compteur flashs |
| Operating Hours | sensor-point | h | 0-99999 | 1h | Heures fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Activate | cmd-point | - | ON/OFF | Binaire | Activation balise |
| Flash Pattern | cmd-sp-point | - | STEADY/SLOW/FAST/STROBE | Enum | Motif clignotement |
| Test Mode | cmd-point | - | ON/OFF | Binaire | Mode test |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Device Status | status-point | Enum | OK/FAULT | État général |
| Active Status | status-point | Boolean | FALSE/TRUE | Balise active |
| Lamp Status | status-point | Enum | OK/DEGRADED/FAILED | État lampe/LED |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | SIA/CEI Protocol |
|-------|---------------|-----------------|------------------|
| Activate | BO0 | 00001 | Command 0x01 |
| Device Status | MSV0 | 40001 | Status 0x10 |
| Active Status | BI0 | 10001 | Status 0x11 |
| Lamp Status | MSV1 | 40002 | Diagnostic 0x20 |

## Sources
- [EN 54-23 Fire Detection Visual Alarm](https://www.en-standard.eu/)
- [NFPA 72 National Fire Alarm Code](https://www.nfpa.org/)
