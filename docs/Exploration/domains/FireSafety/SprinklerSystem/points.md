# Points de Sprinkler System (Système sprinkler)

## Synthèse
- **Total points mesure** : 10
- **Total points commande** : 6
- **Total points état** : 9

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| System Pressure | sensor-pressure-point | bar | 0-16 | 5s | Pression système |
| Air Pressure | sensor-pressure-point | bar | 0-6 | 5s | Pression air (système sec) |
| Water Flow Rate | sensor-flow-point | L/min | 0-5000 | 1s | Débit eau |
| Tank Level | sensor-level-point | % | 0-100% | 1min | Niveau réservoir |
| Sprinklers Activated | sensor-point | count | 0-100 | Sur événement | Têtes activées |
| Zones Activated | sensor-point | count | 0-50 | Sur événement | Zones activées |
| Main Drain Flow | sensor-flow-point | L/min | 0-2000 | 10s | Débit vidange principale |
| Inspector Test Flow | sensor-flow-point | L/min | 0-200 | 1s | Débit test inspecteur |
| Water Temperature | sensor-temp-point | °C | 0-50°C | 5min | Température eau |
| Event Count | sensor-point | count | 0-9999 | Sur événement | Compteur événements |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| System Enable | cmd-point | - | ON/OFF | Binaire | Activation système |
| Zone Valve Control | cmd-sp-point | - | Zone ID | Analog | Contrôle vanne zone |
| Main Valve Control | cmd-point | - | OPEN/CLOSE | Binaire | Contrôle vanne principale |
| Alarm Silence | cmd-point | - | TRIGGER | Binaire | Acquittement alarme |
| Test Mode | cmd-point | - | ON/OFF | Binaire | Mode test |
| Reset System | cmd-point | - | TRIGGER | Binaire | Reset système |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| System Status | status-point | Enum | READY/ACTIVE/ALARM/FAULT | État général |
| Main Valve Status | status-point | Enum | OPEN/CLOSED/FAULT | État vanne principale |
| Flow Alarm | status-point | Boolean | FALSE/TRUE | Alarme écoulement |
| Low Pressure Alarm | status-point | Boolean | FALSE/TRUE | Alarme basse pression |
| High Pressure Alarm | status-point | Boolean | FALSE/TRUE | Alarme haute pression |
| Tamper Alarm | status-point | Boolean | FALSE/TRUE | Alarme sabotage |
| Pump Running | status-point | Boolean | FALSE/TRUE | Pompe en marche |
| Freeze Protection | status-point | Boolean | FALSE/TRUE | Protection gel active |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | SIA/CEI Protocol |
|-------|---------------|-----------------|------------------|
| System Pressure | AI0 | 30001 | - |
| Water Flow Rate | AI1 | 30002 | - |
| Tank Level | AI2 | 30003 | - |
| System Status | MSV0 | 40001 | Status 0x00 |
| Flow Alarm | BI0 | 10001 | Event WF |
| Low Pressure Alarm | BI1 | 10002 | Event LP |
| Tamper Alarm | BI2 | 10003 | Event TA |
| System Enable | BO0 | 00001 | - |

## Sources
- [EN 12845 Automatic Sprinkler Systems](https://www.en-standard.eu/)
- [NFPA 13 Sprinkler Systems](https://www.nfpa.org/)
- [NFPA 25 Inspection Testing](https://www.nfpa.org/)
- [FM Global Data Sheet 2-0](https://www.fmglobal.com/)
