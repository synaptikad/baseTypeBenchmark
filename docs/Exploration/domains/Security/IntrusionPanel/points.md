# Points de Intrusion Panel (Centrale intrusion)

## Synthèse
- **Total points mesure** : 7
- **Total points commande** : 7
- **Total points état** : 10

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Total Zones | sensor-point | count | 0-256 | 1min | Nombre zones |
| Active Zones | sensor-point | count | 0-256 | 1s | Zones actives |
| Zones in Alarm | sensor-point | count | 0-50 | 1s | Zones en alarme |
| Zones in Fault | sensor-point | count | 0-50 | 1s | Zones en défaut |
| Battery Voltage | sensor-point | V | 10-14 | 1min | Tension batterie |
| Mains Voltage | sensor-point | V | 200-250 | 1min | Tension secteur |
| Event Count | sensor-point | count | 0-999999 | Sur événement | Compteur événements |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Arm Away | cmd-point | - | TRIGGER | Binaire | Armement total |
| Arm Stay | cmd-point | - | TRIGGER | Binaire | Armement partiel |
| Disarm | cmd-point | - | TRIGGER | Binaire | Désarmement |
| Silence Alarm | cmd-point | - | TRIGGER | Binaire | Acquittement alarme |
| Reset Panel | cmd-point | - | TRIGGER | Binaire | Reset centrale |
| Bypass Zone | cmd-sp-point | - | Zone ID | Analog | Bypass zone |
| Unbypass Zone | cmd-sp-point | - | Zone ID | Analog | Annulation bypass |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Panel Status | status-point | Enum | DISARMED/ARMED_AWAY/ARMED_STAY/ALARM/FAULT | État général |
| Armed Status | status-point | Enum | DISARMED/ARMED_AWAY/ARMED_STAY | État armement |
| Alarm Active | status-point | Boolean | FALSE/TRUE | Alarme active |
| Entry Delay | status-point | Boolean | FALSE/TRUE | Temporisation entrée |
| Exit Delay | status-point | Boolean | FALSE/TRUE | Temporisation sortie |
| Mains Status | status-point | Enum | OK/FAULT | État alimentation secteur |
| Battery Status | status-point | Enum | OK/LOW/FAULT | État batterie |
| Tamper Status | status-point | Boolean | FALSE/TRUE | Sabotage détecté |
| Transmission Status | status-point | Enum | OK/FAULT | État transmission |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | SIA Protocol |
|-------|---------------|-----------------|--------------|
| Panel Status | MSV0 | 40001 | Account Status |
| Armed Status | MSV1 | 40002 | CL/OP Event |
| Alarm Active | BI0 | 10001 | BA Event |
| Zones in Alarm | AI0 | 30001 | Zone Data |
| Battery Voltage | AI1 | 30002 | Diagnostic |
| Arm Away | BO0 | 00001 | CA Command |
| Disarm | BO1 | 00002 | OA Command |

## Sources
- [EN 50131-1 Intrusion Systems](https://www.en-standard.eu/)
- [EN 50131-3 Control Panels](https://www.en-standard.eu/)
- [SIA DC-07 Contact ID](https://www.securityindustry.org/)
