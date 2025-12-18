# Points de Gas Extinguishing System (Système extinction gaz)

## Synthèse
- **Total points mesure** : 7
- **Total points commande** : 7
- **Total points état** : 10

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Agent Weight | sensor-point | kg | 0-500 | 1h | Poids agent extincteur |
| Cylinder Pressure | sensor-pressure-point | bar | 0-300 | 1min | Pression bouteille |
| Room Pressure | sensor-pressure-point | Pa | -100 à +100 | 1s | Pression salle protégée |
| Agent Concentration | sensor-point | % | 0-20% | 1s | Concentration agent |
| Countdown Timer | sensor-point | s | 0-60 | 1s | Temporisation avant décharge |
| Discharge Count | sensor-point | count | 0-99 | Sur événement | Compteur décharges |
| Room Temperature | sensor-temp-point | °C | 0-50°C | 1min | Température salle |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| System Enable | cmd-point | - | ON/OFF | Binaire | Activation système |
| Manual Release | cmd-point | - | TRIGGER | Binaire | Déclenchement manuel |
| Abort | cmd-point | - | TRIGGER | Binaire | Abandon décharge |
| Zone Select | cmd-sp-point | - | 1-10 | Analog | Sélection zone |
| Pre-discharge Time | cmd-sp-point | s | 10-60 | Analog | Temps pré-décharge |
| Reset System | cmd-point | - | TRIGGER | Binaire | Reset système |
| Inhibit | cmd-point | - | ON/OFF | Binaire | Inhibition système |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| System Status | status-point | Enum | READY/PRE-DISCHARGE/DISCHARGING/DISCHARGED/FAULT | État général |
| Armed Status | status-point | Boolean | FALSE/TRUE | Système armé |
| Pre-discharge Active | status-point | Boolean | FALSE/TRUE | Pré-décharge en cours |
| Discharge Active | status-point | Boolean | FALSE/TRUE | Décharge en cours |
| Discharged Status | status-point | Boolean | FALSE/TRUE | Système déchargé |
| Low Agent Alarm | status-point | Boolean | FALSE/TRUE | Alarme niveau bas agent |
| Door Status | status-point | Enum | CLOSED/OPEN | État portes zone |
| Damper Status | status-point | Enum | CLOSED/OPEN | État clapets |
| Inhibited | status-point | Boolean | FALSE/TRUE | Système inhibé |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| Agent Weight | AI0 | 30001 |
| Cylinder Pressure | AI1 | 30002 |
| Agent Concentration | AI2 | 30003 |
| Countdown Timer | AI3 | 30004 |
| System Status | MSV0 | 40001 |
| Armed Status | BI0 | 10001 |
| Discharge Active | BI1 | 10002 |
| System Enable | BO0 | 00001 |
| Manual Release | BO1 | 00002 |
| Abort | BO2 | 00003 |

## Sources
- [EN 15004 Gas Extinguishing Systems](https://www.en-standard.eu/)
- [NFPA 2001 Clean Agent Systems](https://www.nfpa.org/)
- [ISO 14520 Gaseous Fire-Extinguishing](https://www.iso.org/)
