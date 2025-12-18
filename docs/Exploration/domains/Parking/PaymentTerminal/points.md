# Points de Payment Terminal

## Synthèse
- **Total points mesure** : 9
- **Total points commande** : 6
- **Total points état** : 10

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Transactions Today | sensor-point | count | 0-1000 | 5min | Nombre transactions journée |
| Revenue Today | sensor-point | € | 0-50000 | 5min | Revenu total journée |
| Cash Level | sensor-point | € | 0-5000 | Sur événement | Montant espèces dans terminal |
| Card Transaction Rate | sensor-point | % | 0-100% | 1h | Taux transactions carte |
| Average Transaction Time | sensor-point | s | 10-120 s | 1h | Durée moyenne transaction |
| Paper Roll Level | sensor-point | % | 0-100% | Sur événement | Niveau papier imprimante |
| Terminal Temperature | sensor-temp-point | °C | -20 à +60°C | 5min | Température interne terminal |
| Network Latency | sensor-point | ms | 10-500 ms | 1min | Latence réseau bancaire |
| Card Reader Success Rate | sensor-point | % | 0-100% | 1h | Taux succès lecture carte |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Terminal Enable | cmd-point | - | ENABLE/DISABLE | Binaire | Activation/désactivation terminal |
| Payment Mode | cmd-point | - | CARD/CASH/NFC/ALL | Enum | Modes paiement autorisés |
| Transaction Cancel | cmd-point | - | CANCEL | Binaire | Annulation transaction en cours |
| Receipt Print | cmd-point | - | PRINT | Binaire | Impression reçu |
| Cash Collection Notify | cmd-point | - | NOTIFY | Binaire | Notification besoin collecte |
| End of Day Report | cmd-point | - | GENERATE | Binaire | Rapport fin de journée |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Terminal Status | status-point | Enum | READY/BUSY/ERROR/OFFLINE | État général terminal |
| Transaction Status | status-point | Enum | IDLE/PROCESSING/APPROVED/DECLINED/ERROR | État transaction |
| Card Reader Status | status-point | Enum | OK/FAULT/OFFLINE | État lecteur carte |
| Cash Acceptor Status | status-point | Enum | OK/FULL/JAM/FAULT | État monnayeur |
| Printer Status | status-point | Enum | OK/NO_PAPER/JAM/FAULT | État imprimante |
| Payment Gateway Status | status-point | Enum | ONLINE/OFFLINE | État connexion bancaire |
| Last Transaction Amount | status-point | Number | 0-9999 | Montant dernière transaction |
| Last Transaction Time | status-point | Timestamp | ISO8601 | Horodatage dernière transaction |
| Security Alert | status-point | Boolean | TRUE/FALSE | Alerte sécurité active |
| Maintenance Required | status-point | Boolean | TRUE/FALSE | Maintenance nécessaire |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| Terminal Status | MSV0 | 40001 |
| Transactions Today | AI0 | 40002 |
| Revenue Today | AI1 | 40003-40004 (Float) |
| Cash Level | AI2 | 40005-40006 (Float) |
| Terminal Temperature | AI3 | 40007 |
| Terminal Enable | BO0 | 00001 |
| Transaction Cancel | BO1 | 00002 |
| Transaction Status | MSV1 | 40011 |

## Sources
- [PCI-DSS Standards](https://www.pcisecuritystandards.org/)
- [EMV Chip Card Specifications](https://www.emvco.com/)
- [Contactless Payment Specifications](https://www.nfc-forum.org/)
