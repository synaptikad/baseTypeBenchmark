# Points de Sounder (Sirène d'alarme)

## Synthèse
- **Total points mesure** : 3
- **Total points commande** : 4
- **Total points état** : 4

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Sound Level | sensor-point | dB | 0-120 | Sur activation | Niveau sonore |
| Activation Count | sensor-point | count | 0-99999 | Sur événement | Compteur activations |
| Operating Hours | sensor-point | h | 0-99999 | 1h | Heures fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Activate | cmd-point | - | ON/OFF | Binaire | Activation sirène |
| Tone Select | cmd-sp-point | - | EVACUATION/ALERT/TEST | Enum | Sélection tonalité |
| Volume | cmd-sp-point | % | 0-100% | Analog | Volume sonore |
| Test Mode | cmd-point | - | ON/OFF | Binaire | Mode test |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Device Status | status-point | Enum | OK/ACTIVE/FAULT | État général |
| Active Status | status-point | Boolean | FALSE/TRUE | Sirène active |
| Speaker Status | status-point | Enum | OK/DEGRADED/FAULT | État haut-parleur |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | SIA/CEI Protocol |
|-------|---------------|-----------------|------------------|
| Activate | BO0 | 00001 | Command 0x01 |
| Tone Select | MSV0 | 40001 | Config 0x40 |
| Volume | AO0 | 40101 | Config 0x41 |
| Device Status | MSV1 | 40002 | Status 0x10 |
| Active Status | BI0 | 10001 | Status 0x11 |

## Sources
- [EN 54-3 Fire Alarm Sounders](https://www.en-standard.eu/)
- [NFPA 72 National Fire Alarm Code](https://www.nfpa.org/)
- [ISO 7731 Danger Signals](https://www.iso.org/)
