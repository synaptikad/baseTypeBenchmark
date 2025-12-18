# Points de Magnetic Lock (Ventouse magnétique)

## Synthèse
- **Total points mesure** : 4
- **Total points commande** : 3
- **Total points état** : 5

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Holding Force | sensor-point | kg | 0-600 | 10s | Force maintien |
| Lock Current | sensor-point | mA | 0-500 | 1s | Courant ventouse |
| Cycle Count | sensor-point | count | 0-999999 | Sur événement | Compteur cycles |
| Operating Hours | sensor-point | h | 0-99999 | 1h | Heures fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Release Command | cmd-point | - | TRIGGER | Binaire | Libération ventouse |
| Hold Command | cmd-point | - | ON/OFF | Binaire | Maintien ventouse |
| Release Duration | cmd-sp-point | s | 1-30 | Analog | Durée libération |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Lock Status | status-point | Enum | LOCKED/RELEASED/FAULT | État général |
| Door Bond Status | status-point | Boolean | FALSE/TRUE | Porte collée |
| Door Position | status-point | Enum | CLOSED/OPEN | Position porte |
| Power Status | status-point | Enum | OK/FAULT | État alimentation |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | OSDP Protocol |
|-------|---------------|-----------------|---------------|
| Holding Force | AI0 | 30001 | - |
| Lock Current | AI1 | 30002 | - |
| Lock Status | MSV0 | 40001 | Output Status |
| Door Bond Status | BI0 | 10001 | Input Status |
| Release Command | BO0 | 00001 | Output Control |

## Sources
- [EN 13637 Electrically Controlled Exit Systems](https://www.en-standard.eu/)
- [UL 294 Access Control System Units](https://www.ul.com/)
