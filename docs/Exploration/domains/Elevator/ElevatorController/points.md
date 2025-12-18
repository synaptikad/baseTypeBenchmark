# Points de Elevator Controller

## Synthèse
- **Total points mesure** : 10
- **Total points commande** : 7
- **Total points état** : 12

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| CPU Usage | sensor-point | % | 0-100% | 30s | Utilisation processeur contrôleur |
| Memory Usage | sensor-point | % | 0-100% | 30s | Utilisation mémoire |
| Position Encoder | sensor-point | mm | 0-999999 | 10ms | Position absolue cabine |
| Speed Reference | sensor-point | m/s | 0-10 | 100ms | Consigne vitesse |
| Speed Actual | sensor-point | m/s | 0-10 | 100ms | Vitesse réelle |
| Position Error | sensor-point | mm | -50 à +50 | 100ms | Erreur de position |
| Brake Current | sensor-elec-current-point | A | 0-50 A | 1s | Courant frein |
| Battery Voltage | sensor-elec-volt-point | V | 20-30 V | 1min | Tension batterie secours |
| Call Queue Size | sensor-point | count | 0-100 | 1s | Appels en attente |
| Uptime | sensor-point | h | 0-999999 | 1h | Temps fonctionnement |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Run Enable | cmd-point | - | ENABLE/DISABLE | Binaire | Activation marche |
| Direction | cmd-point | - | UP/DOWN/STOP | Enum | Direction mouvement |
| Target Floor | cmd-point | floor | -5 à 100 | Analog | Étage destination |
| Door Command | cmd-point | - | OPEN/CLOSE/NUDGE | Enum | Commande portes |
| Speed Limit | cmd-sp-point | m/s | 0-10 | Analog | Limitation vitesse |
| Reset Fault | cmd-point | - | RESET | Binaire | Acquittement défaut |
| Software Reboot | cmd-point | - | REBOOT | Binaire | Redémarrage contrôleur |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Controller Status | status-point | Enum | OK/WARNING/FAULT/OFFLINE | État général |
| Run Status | status-point | Enum | RUNNING/STOPPED/STARTING | État marche |
| Fault Code | status-point | String | Alphanumeric | Code défaut actif |
| Safety Input Status | status-point | Enum | ALL_OK/FAULT | État entrées sécurité |
| Brake Status | status-point | Enum | RELEASED/APPLIED/FAULT | État frein |
| Encoder Status | status-point | Enum | OK/FAULT | État encodeur |
| Communication Status | status-point | Enum | OK/FAULT | État bus terrain |
| Battery Status | status-point | Enum | OK/LOW/CHARGING | État batterie |
| Learn Mode | status-point | Boolean | FALSE/TRUE | Mode apprentissage |
| Fire Recall Active | status-point | Boolean | FALSE/TRUE | Rappel pompiers actif |
| Earthquake Mode | status-point | Boolean | FALSE/TRUE | Mode séisme actif |
| Last Fault Time | status-point | Timestamp | ISO8601 | Horodatage dernier défaut |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | CAN |
|-------|---------------|-----------------|-----|
| Controller Status | MSV0 | 40001 | 0x100 |
| Position Encoder | AI0 | 40002-40003 | 0x200 |
| Speed Actual | AI1 | 40004 | 0x201 |
| Fault Code | CSV0 | 40010 | 0x300 |
| Run Enable | BO0 | 00001 | 0x400 |
| Target Floor | AO0 | 40101 | 0x401 |
| Safety Input Status | MSV1 | 40020 | 0x500 |
| Brake Status | MSV2 | 40021 | 0x501 |

## Sources
- [EN 81-20/50 Safety Norms](https://www.en-standard.eu/)
- [CAN in Automation (CiA) 417](https://www.can-cia.org/)
- [BACnet Elevator Objects](https://www.bacnet.org/)
