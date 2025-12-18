# Points de Speed Gate (Portillon rapide)

## Synthèse
- **Total points mesure** : 6
- **Total points commande** : 5
- **Total points état** : 8

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Passage Count Entry | sensor-point | count | 0-999999 | Sur événement | Compteur entrées |
| Passage Count Exit | sensor-point | count | 0-999999 | Sur événement | Compteur sorties |
| Passage Rate | sensor-point | /min | 0-60 | 1min | Taux passage |
| Opening Time | sensor-point | ms | 0-2000 | Config | Temps ouverture |
| Cycle Count | sensor-point | count | 0-999999 | Sur événement | Compteur cycles |
| Operating Hours | sensor-point | h | 0-99999 | 1h | Heures fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Open Entry | cmd-point | - | TRIGGER | Binaire | Ouverture entrée |
| Open Exit | cmd-point | - | TRIGGER | Binaire | Ouverture sortie |
| Emergency Open | cmd-point | - | TRIGGER | Binaire | Ouverture urgence |
| Mode Select | cmd-sp-point | - | NORMAL/FREE_ENTRY/FREE_EXIT/LOCKED | Enum | Mode fonctionnement |
| Speed Setting | cmd-sp-point | - | SLOW/NORMAL/FAST | Enum | Vitesse ouverture |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Gate Status | status-point | Enum | CLOSED/OPEN_ENTRY/OPEN_EXIT/FAULT | État général |
| Entry Lane Status | status-point | Enum | FREE/OCCUPIED/BLOCKED | État voie entrée |
| Exit Lane Status | status-point | Enum | FREE/OCCUPIED/BLOCKED | État voie sortie |
| Tailgate Detected | status-point | Boolean | FALSE/TRUE | Talonnage détecté |
| Forced Entry | status-point | Boolean | FALSE/TRUE | Entrée forcée |
| Person Present | status-point | Boolean | FALSE/TRUE | Personne présente |
| Emergency Mode | status-point | Boolean | FALSE/TRUE | Mode urgence actif |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | OSDP Protocol |
|-------|---------------|-----------------|---------------|
| Passage Count Entry | AI0 | 30001 | - |
| Passage Count Exit | AI1 | 30002 | - |
| Gate Status | MSV0 | 40001 | Status Poll |
| Tailgate Detected | BI0 | 10001 | Event |
| Forced Entry | BI1 | 10002 | Event |
| Open Entry | BO0 | 00001 | Output Control |
| Open Exit | BO1 | 00002 | Output Control |

## Sources
- [EN 60839-11 Access Control](https://www.en-standard.eu/)
- [EN 16005 Pedestrian Doorsets](https://www.en-standard.eu/)
