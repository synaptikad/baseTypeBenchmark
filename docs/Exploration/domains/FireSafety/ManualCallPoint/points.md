# Points de Manual Call Point (Déclencheur manuel)

## Synthèse
- **Total points mesure** : 2
- **Total points commande** : 2
- **Total points état** : 4

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Activation Count | sensor-point | count | 0-9999 | Sur événement | Compteur activations |
| Last Activation Time | sensor-point | timestamp | - | Sur événement | Horodatage dernière activation |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Reset | cmd-point | - | TRIGGER | Binaire | Réarmement |
| Test Mode | cmd-point | - | ON/OFF | Binaire | Mode test |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Device Status | status-point | Enum | NORMAL/ACTIVATED/FAULT | État général |
| Activated | status-point | Boolean | FALSE/TRUE | Déclenché |
| Cover Status | status-point | Enum | CLOSED/OPEN | État capot protection |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | SIA/CEI Protocol |
|-------|---------------|-----------------|------------------|
| Device Status | MSV0 | 40001 | Status 0x00 |
| Activated | BI0 | 10001 | Event MA |
| Cover Status | BI1 | 10002 | Event TC |
| Reset | BO0 | 00001 | Command RR |

## Sources
- [EN 54-11 Manual Call Points](https://www.en-standard.eu/)
- [NFPA 72 National Fire Alarm Code](https://www.nfpa.org/)
