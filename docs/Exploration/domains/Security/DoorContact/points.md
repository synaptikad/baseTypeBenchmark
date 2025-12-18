# Points de Door Contact (Contact de porte)

## Synthèse
- **Total points mesure** : 3
- **Total points commande** : 1
- **Total points état** : 4

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Open Duration | sensor-point | s | 0-3600 | 1s | Durée ouverture |
| Open Count | sensor-point | count | 0-999999 | Sur événement | Compteur ouvertures |
| Battery Level | sensor-point | % | 0-100% | 1h | Niveau batterie (sans fil) |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Bypass Enable | cmd-point | - | ON/OFF | Binaire | Bypass capteur |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Contact Status | status-point | Enum | CLOSED/OPEN/FAULT | État contact |
| Door Open | status-point | Boolean | FALSE/TRUE | Porte ouverte |
| Tamper Status | status-point | Boolean | FALSE/TRUE | Sabotage détecté |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | SIA Protocol |
|-------|---------------|-----------------|--------------|
| Contact Status | MSV0 | 40001 | Zone Status |
| Door Open | BI0 | 10001 | Event OP |
| Tamper Status | BI1 | 10002 | Event TA |
| Bypass Enable | BO0 | 00001 | Bypass Cmd |

## Sources
- [EN 50131-2-6 Opening Contacts](https://www.en-standard.eu/)
- [UL 634 Burglar Alarm Units](https://www.ul.com/)
