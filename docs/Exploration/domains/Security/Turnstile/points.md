# Points de Turnstile (Tourniquet)

## Synthèse
- **Total points mesure** : 5
- **Total points commande** : 5
- **Total points état** : 7

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Passage Count Entry | sensor-point | count | 0-999999 | Sur événement | Compteur entrées |
| Passage Count Exit | sensor-point | count | 0-999999 | Sur événement | Compteur sorties |
| Passage Rate | sensor-point | /min | 0-30 | 1min | Taux passage |
| Cycle Count | sensor-point | count | 0-999999 | Sur événement | Compteur cycles |
| Operating Hours | sensor-point | h | 0-99999 | 1h | Heures fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Unlock Entry | cmd-point | - | TRIGGER | Binaire | Déverrouillage entrée |
| Unlock Exit | cmd-point | - | TRIGGER | Binaire | Déverrouillage sortie |
| Free Rotation | cmd-point | - | ON/OFF | Binaire | Rotation libre |
| Lock All | cmd-point | - | ON/OFF | Binaire | Verrouillage total |
| Mode Select | cmd-sp-point | - | NORMAL/FREE/LOCKED/ONE_WAY | Enum | Mode fonctionnement |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Turnstile Status | status-point | Enum | LOCKED/UNLOCKED_ENTRY/UNLOCKED_EXIT/FREE/FAULT | État général |
| Entry Unlocked | status-point | Boolean | FALSE/TRUE | Entrée déverrouillée |
| Exit Unlocked | status-point | Boolean | FALSE/TRUE | Sortie déverrouillée |
| Rotation Detected | status-point | Enum | NONE/ENTRY/EXIT | Rotation détectée |
| Tailgate Attempt | status-point | Boolean | FALSE/TRUE | Tentative talonnage |
| Forced Rotation | status-point | Boolean | FALSE/TRUE | Rotation forcée |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | OSDP Protocol |
|-------|---------------|-----------------|---------------|
| Passage Count Entry | AI0 | 30001 | - |
| Passage Count Exit | AI1 | 30002 | - |
| Turnstile Status | MSV0 | 40001 | Status Poll |
| Tailgate Attempt | BI0 | 10001 | Event |
| Unlock Entry | BO0 | 00001 | Output Control |
| Unlock Exit | BO1 | 00002 | Output Control |

## Sources
- [EN 60839-11 Access Control](https://www.en-standard.eu/)
- [EN 13637 Electrically Controlled Exit](https://www.en-standard.eu/)
