# Points de Badge Reader (Lecteur de badge)

## Synthèse
- **Total points mesure** : 4
- **Total points commande** : 3
- **Total points état** : 5

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Read Count | sensor-point | count | 0-999999 | Sur événement | Compteur lectures |
| Failed Reads | sensor-point | count | 0-9999 | Sur événement | Lectures échouées |
| Signal Strength | sensor-point | % | 0-100% | 10s | Force signal RFID |
| Operating Hours | sensor-point | h | 0-99999 | 1h | Heures fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| LED Mode | cmd-sp-point | - | OFF/GREEN/RED/AMBER | Enum | Mode LED indicateur |
| Beeper Enable | cmd-point | - | ON/OFF | Binaire | Activation buzzer |
| Reader Enable | cmd-point | - | ON/OFF | Binaire | Activation lecteur |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Reader Status | status-point | Enum | OK/FAULT | État général |
| Card Present | status-point | Boolean | FALSE/TRUE | Badge détecté |
| Tamper Status | status-point | Boolean | FALSE/TRUE | Sabotage détecté |
| LED Status | status-point | Enum | OFF/GREEN/RED/AMBER | État LED |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | OSDP Protocol |
|-------|---------------|-----------------|---------------|
| Reader Status | MSV0 | 40001 | Status Poll |
| Card Present | BI0 | 10001 | Card Read Event |
| Tamper Status | BI1 | 10002 | Tamper Event |
| LED Mode | MSV1 | 40002 | LED Command |
| Reader Enable | BO0 | 00001 | Enable/Disable |

## Sources
- [ISO 14443 RFID Cards](https://www.iso.org/)
- [OSDP Standard](https://www.securityindustry.org/osdp/)
- [EN 60839-11 Access Control](https://www.en-standard.eu/)
