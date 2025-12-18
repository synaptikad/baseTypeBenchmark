# Points de Ticket Dispenser

## Synthèse
- **Total points mesure** : 7
- **Total points commande** : 5
- **Total points état** : 9

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Ticket Count Remaining | sensor-point | tickets | 0-5000 | Sur événement | Tickets restants dans rouleau |
| Tickets Dispensed Today | sensor-point | count | 0-1000 | 5min | Tickets distribués aujourd'hui |
| Tickets Dispensed Total | sensor-point | count | 0-999999 | 1h | Total tickets distribués |
| Dispense Time | sensor-point | s | 0.5-5 s | Sur événement | Temps distribution ticket |
| Printer Temperature | sensor-temp-point | °C | -20 à +60°C | 5min | Température tête impression |
| Vehicle Detection Rate | sensor-point | count/h | 0-200 | 1h | Taux détection véhicules |
| Error Rate | sensor-point | % | 0-100% | 1h | Taux d'erreurs distribution |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Dispenser Enable | cmd-point | - | ENABLE/DISABLE | Binaire | Activation/désactivation distributeur |
| Ticket Dispense Manual | cmd-point | - | DISPENSE | Binaire | Distribution manuelle ticket |
| Printer Feed | cmd-point | - | FEED | Binaire | Avance papier imprimante |
| Reset Counter | cmd-point | - | RESET | Binaire | Remise à zéro compteur |
| Auto Dispense Mode | cmd-point | - | ENABLE/DISABLE | Binaire | Distribution automatique |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Dispenser Status | status-point | Enum | OK/EMPTY/JAM/FAULT/OFFLINE | État général distributeur |
| Printer Status | status-point | Enum | OK/NO_PAPER/JAM/HEAD_HOT/FAULT | État imprimante thermique |
| Vehicle Present | status-point | Boolean | TRUE/FALSE | Véhicule détecté devant |
| Ticket Roll Status | status-point | Enum | OK/LOW/EMPTY | État rouleau tickets |
| Ticket Dispensed | status-point | Boolean | TRUE/FALSE | Ticket en cours distribution |
| Last Ticket Number | status-point | String | Alphanumeric | Numéro dernier ticket émis |
| Last Dispense Time | status-point | Timestamp | ISO8601 | Horodatage dernière distribution |
| Communication Status | status-point | Enum | CONNECTED/DISCONNECTED | État connexion réseau |
| Maintenance Alert | status-point | Boolean | TRUE/FALSE | Alerte maintenance requise |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| Dispenser Status | MSV0 | 40001 |
| Ticket Count Remaining | AI0 | 40002 |
| Tickets Dispensed Today | AI1 | 40003 |
| Tickets Dispensed Total | AI2 | 40004-40005 |
| Printer Temperature | AI3 | 40006 |
| Dispenser Enable | BO0 | 00001 |
| Ticket Dispense Manual | BO1 | 00002 |
| Vehicle Present | BI0 | 10001 |

## Sources
- [Parking Access Control Standards](https://www.parking-mobility.org/)
- [Thermal Printer Specifications](https://www.thermal-printer.com/)
