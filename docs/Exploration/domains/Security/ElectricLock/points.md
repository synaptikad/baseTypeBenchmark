# Points de Electric Lock (Serrure électrique)

## Synthèse
- **Total points mesure** : 3
- **Total points commande** : 3
- **Total points état** : 5

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Cycle Count | sensor-point | count | 0-999999 | Sur événement | Compteur cycles |
| Lock Current | sensor-point | mA | 0-500 | 1s | Courant serrure |
| Operating Hours | sensor-point | h | 0-99999 | 1h | Heures fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Unlock Command | cmd-point | - | TRIGGER | Binaire | Déverrouillage |
| Lock Command | cmd-point | - | TRIGGER | Binaire | Verrouillage |
| Unlock Duration | cmd-sp-point | s | 1-30 | Analog | Durée déverrouillage |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Lock Status | status-point | Enum | LOCKED/UNLOCKED/FAULT | État général |
| Locked Position | status-point | Boolean | FALSE/TRUE | Position verrouillée |
| Bolt Status | status-point | Enum | EXTENDED/RETRACTED | État pêne |
| Power Status | status-point | Enum | OK/FAULT | État alimentation |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | OSDP Protocol |
|-------|---------------|-----------------|---------------|
| Lock Status | MSV0 | 40001 | Output Status |
| Locked Position | BI0 | 10001 | Input Status |
| Bolt Status | MSV1 | 40002 | - |
| Unlock Command | BO0 | 00001 | Output Control |
| Unlock Duration | AO0 | 40101 | Config |

## Sources
- [EN 14846 Electromechanical Locks](https://www.en-standard.eu/)
- [EN 12209 Mechanically Operated Locks](https://www.en-standard.eu/)
