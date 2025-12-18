# Points de Door Controller (Contrôleur de porte)

## Synthèse
- **Total points mesure** : 5
- **Total points commande** : 6
- **Total points état** : 8

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Access Count | sensor-point | count | 0-999999 | Sur événement | Compteur accès |
| Denied Count | sensor-point | count | 0-9999 | Sur événement | Accès refusés |
| Door Open Time | sensor-point | s | 0-300 | 1s | Temps porte ouverte |
| Unlock Duration | sensor-point | s | 1-30 | Config | Durée déverrouillage |
| Operating Hours | sensor-point | h | 0-99999 | 1h | Heures fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Unlock Command | cmd-point | - | TRIGGER | Binaire | Déverrouillage |
| Lock Command | cmd-point | - | TRIGGER | Binaire | Verrouillage |
| Hold Open | cmd-point | - | ON/OFF | Binaire | Maintien ouvert |
| Mode Select | cmd-sp-point | - | NORMAL/LOCKED/UNLOCKED | Enum | Mode porte |
| Unlock Time | cmd-sp-point | s | 1-30 | Analog | Temps déverrouillage |
| Relock Delay | cmd-sp-point | s | 0-60 | Analog | Délai reverrouillage |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Controller Status | status-point | Enum | OK/FAULT | État général |
| Door Status | status-point | Enum | CLOSED/OPEN/FORCED/HELD | État porte |
| Lock Status | status-point | Enum | LOCKED/UNLOCKED | État verrou |
| Request to Exit | status-point | Boolean | FALSE/TRUE | Demande sortie |
| Door Forced | status-point | Boolean | FALSE/TRUE | Porte forcée |
| Door Held Open | status-point | Boolean | FALSE/TRUE | Porte maintenue ouverte |
| REX Active | status-point | Boolean | FALSE/TRUE | REX actif |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | OSDP Protocol |
|-------|---------------|-----------------|---------------|
| Controller Status | MSV0 | 40001 | Status Poll |
| Door Status | MSV1 | 40002 | Input Status |
| Lock Status | MSV2 | 40003 | Output Status |
| Request to Exit | BI0 | 10001 | REX Event |
| Door Forced | BI1 | 10002 | Forced Event |
| Unlock Command | BO0 | 00001 | Output Ctrl |
| Unlock Time | AO0 | 40101 | Config |

## Sources
- [EN 60839-11 Access Control](https://www.en-standard.eu/)
- [OSDP Standard](https://www.securityindustry.org/osdp/)
