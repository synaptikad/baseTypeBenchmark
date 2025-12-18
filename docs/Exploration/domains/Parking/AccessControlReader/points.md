# Points de Access Control Reader

## Synthèse
- **Total points mesure** : 6
- **Total points commande** : 5
- **Total points état** : 8

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Read Count | sensor-point | count | 0-999999 | Sur événement | Nombre total de lectures badge |
| Success Rate | sensor-point | % | 0-100% | 1h | Taux de lectures réussies |
| Transaction Count Today | sensor-point | count | 0-10000 | 5min | Transactions du jour |
| Reader Temperature | sensor-temp-point | °C | -25 à +70°C | 5min | Température lecteur |
| Signal Strength | sensor-point | dBm | -70 à -10 dBm | 30s | Force signal RFID/NFC |
| Response Time | sensor-point | ms | 50-500 ms | Sur événement | Temps de réponse lecture |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Reader Enable | cmd-point | - | ENABLE/DISABLE | Binaire | Activation/désactivation lecteur |
| LED Color | cmd-point | - | RED/GREEN/AMBER/OFF | Enum | Couleur LED indicatrice |
| Buzzer Enable | cmd-point | - | ENABLE/DISABLE | Binaire | Activation buzzer sonore |
| Read Mode | cmd-point | - | RFID/NFC/BOTH | Enum | Mode de lecture actif |
| Antipassback Reset | cmd-point | - | RESET | Binaire | Remise à zéro antipassback |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Reader Status | status-point | Enum | OK/FAULT/OFFLINE | État général lecteur |
| Communication Status | status-point | Enum | CONNECTED/DISCONNECTED | État connexion contrôleur |
| Last Card ID | status-point | String | Alphanumeric | Dernier badge lu |
| Access Result | status-point | Enum | GRANTED/DENIED/PENDING | Résultat dernier accès |
| Tamper Status | status-point | Boolean | TRUE/FALSE | Détection sabotage |
| Door Status | status-point | Enum | OPEN/CLOSED/FORCED | État porte associée |
| Power Status | status-point | Enum | OK/LOW/FAULT | État alimentation |
| Last Read Time | status-point | Timestamp | ISO8601 | Horodatage dernière lecture |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | OSDP |
|-------|---------------|-----------------|------|
| Reader Status | MSV0 | 40001 | osdp_POLL |
| Read Count | AI0 | 40002-40003 | - |
| Reader Temperature | AI1 | 40004 | - |
| Reader Enable | BO0 | 00001 | osdp_OUT |
| LED Color | MSV1 | 40101 | osdp_LED |
| Buzzer Enable | BO1 | 00002 | osdp_BUZ |
| Access Result | MSV2 | 40011 | osdp_RAW |
| Tamper Status | BI0 | 10001 | osdp_ISTAT |

## Sources
- [OSDP v2 Specification](https://www.securityindustry.org/industry-standards/open-supervised-device-protocol/)
- [ISO 14443 RFID Standards](https://www.iso.org/)
- [NFC Forum Specifications](https://nfc-forum.org/)
