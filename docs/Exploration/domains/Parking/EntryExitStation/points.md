# Points de Entry/Exit Station

## Synthèse
- **Total points mesure** : 6
- **Total points commande** : 7
- **Total points état** : 10

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Ticket Count | sensor-point | tickets | 0-5000 | Sur événement | Nombre de tickets restants |
| Transaction Count | sensor-point | count | 0-999999 | 1min | Nombre total de transactions |
| Vehicle Detection | sensor-point | - | PRESENT/ABSENT | Temps réel | Détection véhicule à la station |
| Card Reader Success Rate | sensor-point | % | 0-100% | 5min | Taux de succès lecture badge |
| Station Temperature | sensor-temp-point | °C | -30 à +60°C | 5min | Température interne station |
| Response Time | sensor-point | s | 0-10 s | Sur événement | Temps réponse système |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Barrier Gate Open | cmd-point | - | OPEN/CLOSE | Binaire | Commande ouverture barrière |
| Ticket Dispense | cmd-point | - | DISPENSE | Binaire | Distribution d'un ticket |
| Display Message | cmd-point | - | TEXT | String | Message affiché à l'usager |
| Intercom Call | cmd-point | - | CALL | Binaire | Appel vers poste central |
| LED Indicator Color | cmd-point | - | RED/GREEN/YELLOW | Enum | Couleur indicateur lumineux |
| Camera Snapshot | cmd-point | - | CAPTURE | Binaire | Capture photo contexte |
| Reader Mode | cmd-point | - | RFID/NFC/BARCODE | Enum | Mode du lecteur d'accès |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Station Status | status-point | Enum | OK/FAULT/MAINTENANCE/OFFLINE | État général station |
| Barrier Gate Status | status-point | Enum | OPEN/CLOSED/OPENING/CLOSING/FAULT | État barrière |
| Ticket Dispenser Status | status-point | Enum | OK/EMPTY/JAM/FAULT | État distributeur tickets |
| Card Reader Status | status-point | Enum | OK/FAULT/OFFLINE | État lecteur badges |
| Intercom Status | status-point | Enum | IDLE/CALLING/CONNECTED | État interphone |
| Camera Status | status-point | Enum | OK/FAULT/OFFLINE | État caméra intégrée |
| Last Card ID | status-point | String | Alphanumeric | Dernier badge lu |
| Last Transaction Time | status-point | Timestamp | ISO8601 | Horodatage dernière transaction |
| Alarm Active | status-point | Boolean | TRUE/FALSE | Alarme technique active |
| Network Connection | status-point | Enum | CONNECTED/DISCONNECTED | État connexion réseau |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| Station Status | MSV0 | 40001 |
| Ticket Count | AI0 | 40002 |
| Vehicle Detection | BI0 | 10001 |
| Station Temperature | AI1 | 40003 |
| Barrier Gate Open | BO0 | 00001 |
| Ticket Dispense | BO1 | 00002 |
| Barrier Gate Status | MSV1 | 40011 |
| Network Connection | MSV2 | 40012 |

## Sources
- [IPI Parking Standards](https://www.parking-mobility.org/)
- [Access Control System Documentation](https://www.access-control.com/)
