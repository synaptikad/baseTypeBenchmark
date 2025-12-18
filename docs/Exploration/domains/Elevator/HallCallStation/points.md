# Points de Hall Call Station

## Synthèse
- **Total points mesure** : 5
- **Total points commande** : 4
- **Total points état** : 7

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Call Count Up | sensor-point | count | 0-999999 | Sur événement | Appels montée cumulés |
| Call Count Down | sensor-point | count | 0-999999 | Sur événement | Appels descente cumulés |
| Button Press Count | sensor-point | count | 0-9999999 | Sur événement | Nombre total appuis |
| Wait Time Current | sensor-point | s | 0-300 | 1s | Temps attente actuel |
| Station Temperature | sensor-temp-point | °C | 10-50°C | 5min | Température boîtier |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| LED Brightness | cmd-sp-point | % | 0-100% | Analog | Luminosité LEDs |
| Call Cancel | cmd-point | - | CANCEL | Binaire | Annulation appel |
| Station Disable | cmd-point | - | ENABLE/DISABLE | Binaire | Désactivation station |
| Test Mode | cmd-point | - | ENABLE/DISABLE | Binaire | Mode test LEDs |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Station Status | status-point | Enum | OK/FAULT/OFFLINE | État général |
| Up Call Status | status-point | Enum | INACTIVE/ACTIVE/ANSWERED | État appel montée |
| Down Call Status | status-point | Enum | INACTIVE/ACTIVE/ANSWERED | État appel descente |
| Button Status | status-point | Enum | OK/STUCK/FAULT | État bouton |
| LED Status | status-point | Enum | OK/FAULT | État LEDs |
| Communication Status | status-point | Enum | OK/FAULT | État communication |
| Fire Mode Display | status-point | Boolean | FALSE/TRUE | Affichage mode incendie |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | CAN |
|-------|---------------|-----------------|-----|
| Station Status | MSV0 | 40001 | 0x100 |
| Up Call Status | MSV1 | 40002 | 0x101 |
| Down Call Status | MSV2 | 40003 | 0x102 |
| Wait Time Current | AI0 | 40004 | 0x200 |
| LED Brightness | AO0 | 40101 | 0x300 |
| Call Cancel | BO0 | 00001 | 0x400 |
| Communication Status | MSV3 | 40010 | 0x500 |

## Sources
- [EN 81-70 Accessibility](https://www.en-standard.eu/)
- [ADA Elevator Requirements](https://www.ada.gov/)
- [CiA 417 CANopen Lifts](https://www.can-cia.org/)
