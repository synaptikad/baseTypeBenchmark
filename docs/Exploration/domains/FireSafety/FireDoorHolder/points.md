# Points de Fire Door Holder (Ventouse de porte coupe-feu)

## Synthèse
- **Total points mesure** : 2
- **Total points commande** : 3
- **Total points état** : 4

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Holding Force | sensor-point | N | 0-150 | 10s | Force maintien |
| Release Count | sensor-point | count | 0-99999 | Sur événement | Compteur libérations |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Release | cmd-point | - | TRIGGER | Binaire | Libération ventouse |
| Hold | cmd-point | - | ON/OFF | Binaire | Activation maintien |
| Test Mode | cmd-point | - | ON/OFF | Binaire | Mode test |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Holder Status | status-point | Enum | HOLDING/RELEASED/FAULT | État général |
| Door Present | status-point | Boolean | FALSE/TRUE | Porte présente |
| Power Status | status-point | Enum | OK/LOW/FAULT | État alimentation |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| Holding Force | AI0 | 30001 |
| Holder Status | MSV0 | 40001 |
| Door Present | BI0 | 10001 |
| Release | BO0 | 00001 |
| Hold | BO1 | 00002 |

## Sources
- [EN 14637 Electromagnetic Door Holders](https://www.en-standard.eu/)
- [EN 1155 Hold-open Devices](https://www.en-standard.eu/)
