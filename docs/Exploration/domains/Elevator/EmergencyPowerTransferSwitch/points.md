# Points de Emergency Power Transfer Switch

## Synthèse
- **Total points mesure** : 8
- **Total points commande** : 4
- **Total points état** : 9

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Normal Voltage | sensor-elec-volt-point | V | 380-415 V | 1s | Tension source normale |
| Emergency Voltage | sensor-elec-volt-point | V | 380-415 V | 1s | Tension source secours |
| Output Voltage | sensor-elec-volt-point | V | 380-415 V | 1s | Tension sortie |
| Output Current | sensor-elec-current-point | A | 0-500 A | 1s | Courant sortie |
| Transfer Time | sensor-point | ms | 0-500 | Sur événement | Temps de transfert |
| Transfer Count | sensor-point | count | 0-99999 | Sur événement | Nombre de transferts |
| Cabinet Temperature | sensor-temp-point | °C | 15-50°C | 5min | Température armoire |
| Operating Hours | sensor-point | h | 0-999999 | 1h | Heures fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Manual Transfer | cmd-point | - | NORMAL/EMERGENCY | Enum | Transfert manuel |
| Test Mode | cmd-point | - | ENABLE/DISABLE | Binaire | Mode test |
| Auto Transfer Enable | cmd-point | - | ENABLE/DISABLE | Binaire | Transfert auto |
| Reset | cmd-point | - | RESET | Binaire | Réinitialisation |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Switch Status | status-point | Enum | OK/FAULT/OFFLINE | État général |
| Position | status-point | Enum | NORMAL/EMERGENCY/TRANSITION | Position actuelle |
| Normal Source Status | status-point | Enum | AVAILABLE/UNAVAILABLE/FAULT | État source normale |
| Emergency Source Status | status-point | Enum | AVAILABLE/UNAVAILABLE/FAULT | État source secours |
| Transfer Mode | status-point | Enum | AUTO/MANUAL/TEST | Mode transfert |
| Last Transfer Cause | status-point | Enum | VOLTAGE_LOSS/FREQUENCY/MANUAL/TEST | Cause dernier transfert |
| Transfer Inhibit | status-point | Boolean | FALSE/TRUE | Transfert bloqué |
| Maintenance Required | status-point | Boolean | FALSE/TRUE | Maintenance requise |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| Switch Status | MSV0 | 40001 |
| Position | MSV1 | 40002 |
| Normal Voltage | AI0 | 40003 |
| Emergency Voltage | AI1 | 40004 |
| Output Voltage | AI2 | 40005 |
| Output Current | AI3 | 40006 |
| Manual Transfer | MSV2 | 40101 |
| Normal Source Status | MSV3 | 40010 |

## Sources
- [EN 81-20/50 Elevator Safety](https://www.en-standard.eu/)
- [IEC 60947-6-1 Transfer Switch](https://webstore.iec.ch/)
- [NFPA 110 Emergency Power](https://www.nfpa.org/)
