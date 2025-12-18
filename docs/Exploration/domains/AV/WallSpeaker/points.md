# Points de Wall Speaker (Haut-parleur mural)

## Synthèse
- **Total points mesure** : 4
- **Total points commande** : 3
- **Total points état** : 4

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| SPL Output | sensor-point | dB | 0-110 | 100ms | Niveau pression sonore |
| Power Draw | sensor-point | W | 0-100 | 1min | Puissance consommée |
| Impedance | sensor-point | Ω | 4-100 | 10min | Impédance mesurée |
| Operating Hours | sensor-point | h | 0-99999 | 1h | Heures fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Volume | cmd-sp-point | dB | -80 à 0 | Analog | Volume |
| Mute | cmd-point | - | ON/OFF | Binaire | Sourdine |
| EQ Preset | cmd-sp-point | - | FLAT/SPEECH/MUSIC/PAGING | Enum | Preset égalisation |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Speaker Status | status-point | Enum | OK/FAULT | État général |
| Line Status | status-point | Enum | OK/OPEN/SHORT | État ligne |
| Mute Status | status-point | Boolean | FALSE/TRUE | Sourdine active |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | Dante |
|-------|---------------|-----------------|-------|
| SPL Output | AI0 | 30001 | Level Meter |
| Speaker Status | MSV0 | 40001 | Device Status |
| Line Status | MSV1 | 40002 | - |
| Volume | AO0 | 40101 | Gain |
| Mute | BO0 | 00001 | Mute |

## Sources
- [EN 54-24 Loudspeakers](https://www.en-standard.eu/)
- [IEC 60268-5 Loudspeakers](https://webstore.iec.ch/)
- [Dante Protocol](https://www.audinate.com/)
