# Points de Fire Extinguisher Cabinet (Armoire extincteur)

## Synthèse
- **Total points mesure** : 2
- **Total points commande** : 1
- **Total points état** : 4

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Door Open Duration | sensor-point | s | 0-3600 | 1s | Durée ouverture porte |
| Access Count | sensor-point | count | 0-9999 | Sur événement | Compteur accès |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Acknowledge Alarm | cmd-point | - | TRIGGER | Binaire | Acquittement alarme |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Cabinet Status | status-point | Enum | OK/OPEN/MISSING/FAULT | État général |
| Door Status | status-point | Enum | CLOSED/OPEN | État porte |
| Extinguisher Present | status-point | Boolean | FALSE/TRUE | Extincteur présent |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| Cabinet Status | MSV0 | 40001 |
| Door Status | BI0 | 10001 |
| Extinguisher Present | BI1 | 10002 |
| Acknowledge Alarm | BO0 | 00001 |

## Sources
- [EN 3 Portable Fire Extinguishers](https://www.en-standard.eu/)
- [NFPA 10 Portable Fire Extinguishers](https://www.nfpa.org/)
