# Points de Electric Strike (Gâche électrique)

## Synthèse
- **Total points mesure** : 3
- **Total points commande** : 3
- **Total points état** : 5

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Cycle Count | sensor-point | count | 0-999999 | Sur événement | Compteur cycles |
| Strike Current | sensor-point | mA | 0-500 | 1s | Courant gâche |
| Operating Hours | sensor-point | h | 0-99999 | 1h | Heures fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Release Command | cmd-point | - | TRIGGER | Binaire | Libération gâche |
| Hold Open | cmd-point | - | ON/OFF | Binaire | Maintien ouvert |
| Release Duration | cmd-sp-point | s | 1-30 | Analog | Durée libération |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Strike Status | status-point | Enum | LOCKED/RELEASED/FAULT | État général |
| Released Position | status-point | Boolean | FALSE/TRUE | Gâche libérée |
| Door Sense | status-point | Boolean | FALSE/TRUE | Porte détectée |
| Power Status | status-point | Enum | OK/FAULT | État alimentation |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | OSDP Protocol |
|-------|---------------|-----------------|---------------|
| Strike Status | MSV0 | 40001 | Output Status |
| Released Position | BI0 | 10001 | Input Status |
| Door Sense | BI1 | 10002 | - |
| Release Command | BO0 | 00001 | Output Control |
| Release Duration | AO0 | 40101 | Config |

## Sources
- [EN 12209 Electric Strikes](https://www.en-standard.eu/)
- [UL 1034 Burglary Resistant Electric Locking](https://www.ul.com/)
