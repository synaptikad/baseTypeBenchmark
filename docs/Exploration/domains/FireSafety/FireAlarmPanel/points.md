# Points de Fire Alarm Panel (Centrale incendie)

## Synthèse
- **Total points mesure** : 8
- **Total points commande** : 8
- **Total points état** : 12

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Total Detectors | sensor-point | count | 0-1000 | 1min | Nombre détecteurs |
| Active Detectors | sensor-point | count | 0-1000 | 1s | Détecteurs actifs |
| Detectors in Alarm | sensor-point | count | 0-100 | 1s | Détecteurs en alarme |
| Detectors in Fault | sensor-point | count | 0-100 | 1s | Détecteurs en défaut |
| Loop Current | sensor-point | mA | 0-50 | 10s | Courant boucle |
| Battery Voltage | sensor-point | V | 20-28 | 1min | Tension batterie |
| Mains Voltage | sensor-point | V | 200-250 | 1min | Tension secteur |
| Event Count | sensor-point | count | 0-999999 | Sur événement | Compteur événements |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Silence Alarms | cmd-point | - | TRIGGER | Binaire | Acquittement alarmes |
| Reset Panel | cmd-point | - | TRIGGER | Binaire | Reset centrale |
| Evacuate | cmd-point | - | TRIGGER | Binaire | Ordre évacuation |
| Disable Zone | cmd-sp-point | - | Zone ID | Analog | Désactivation zone |
| Enable Zone | cmd-sp-point | - | Zone ID | Analog | Activation zone |
| Test Mode | cmd-point | - | ON/OFF | Binaire | Mode test |
| Day Mode | cmd-point | - | ON/OFF | Binaire | Mode jour |
| Night Mode | cmd-point | - | ON/OFF | Binaire | Mode nuit |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Panel Status | status-point | Enum | NORMAL/ALARM/FAULT/DISABLED | État général |
| Fire Alarm | status-point | Boolean | FALSE/TRUE | Alarme incendie active |
| Pre-Alarm | status-point | Boolean | FALSE/TRUE | Pré-alarme active |
| Fault Status | status-point | Boolean | FALSE/TRUE | Défaut système |
| Mains Status | status-point | Enum | OK/FAULT | État alimentation secteur |
| Battery Status | status-point | Enum | OK/LOW/FAULT | État batterie |
| Loop Status | status-point | Enum | OK/OPEN/SHORT | État boucle |
| Sounder Status | status-point | Enum | OK/ACTIVE/FAULT | État sirènes |
| Transmission Status | status-point | Enum | OK/FAULT | État transmission externe |
| Day Night Mode | status-point | Enum | DAY/NIGHT | Mode jour/nuit |
| Silenced | status-point | Boolean | FALSE/TRUE | Alarmes acquittées |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | SIA/CEI Protocol |
|-------|---------------|-----------------|------------------|
| Panel Status | MSV0 | 40001 | Status 0x00 |
| Fire Alarm | BI0 | 10001 | Event FA |
| Pre-Alarm | BI1 | 10002 | Event PA |
| Fault Status | BI2 | 10003 | Event FT |
| Battery Voltage | AI0 | 30001 | Diagnostic |
| Mains Voltage | AI1 | 30002 | Diagnostic |
| Silence Alarms | BO0 | 00001 | Command SI |
| Reset Panel | BO1 | 00002 | Command RR |

## Sources
- [EN 54-2 Fire Detection Control Panel](https://www.en-standard.eu/)
- [NFPA 72 National Fire Alarm Code](https://www.nfpa.org/)
- [UL 864 Fire Alarm Control Units](https://www.ul.com/)
