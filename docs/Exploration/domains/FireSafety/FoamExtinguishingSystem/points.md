# Points de Foam Extinguishing System (Système extinction mousse)

## Synthèse
- **Total points mesure** : 8
- **Total points commande** : 6
- **Total points état** : 8

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Foam Concentrate Level | sensor-level-point | % | 0-100% | 1min | Niveau concentré mousse |
| Water Pressure | sensor-pressure-point | bar | 0-16 | 1s | Pression eau |
| Foam Pressure | sensor-pressure-point | bar | 0-16 | 1s | Pression mousse |
| Proportioning Rate | sensor-point | % | 1-6% | 1s | Taux proportionnement |
| Flow Rate | sensor-flow-point | L/min | 0-2000 | 1s | Débit mousse |
| Tank Temperature | sensor-temp-point | °C | -10 à +50°C | 5min | Température réservoir |
| Discharge Count | sensor-point | count | 0-999 | Sur événement | Compteur décharges |
| System Pressure | sensor-pressure-point | bar | 0-20 | 1s | Pression système |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| System Arm | cmd-point | - | ON/OFF | Binaire | Armement système |
| Manual Release | cmd-point | - | TRIGGER | Binaire | Déclenchement manuel |
| Zone Select | cmd-sp-point | - | 1-10 | Analog | Sélection zone |
| Abort | cmd-point | - | TRIGGER | Binaire | Abandon décharge |
| Test Mode | cmd-point | - | ON/OFF | Binaire | Mode test |
| Reset System | cmd-point | - | TRIGGER | Binaire | Reset système |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| System Status | status-point | Enum | READY/ARMED/DISCHARGING/FAULT | État général |
| Armed Status | status-point | Boolean | FALSE/TRUE | Système armé |
| Discharge Status | status-point | Boolean | FALSE/TRUE | Décharge en cours |
| Low Concentrate Alarm | status-point | Boolean | FALSE/TRUE | Alarme niveau bas concentré |
| Proportioner Status | status-point | Enum | OK/FAULT | État proportionneur |
| Valve Status | status-point | Enum | CLOSED/OPEN/FAULT | État vannes |
| Supervision Status | status-point | Enum | OK/FAULT | État supervision |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| Foam Concentrate Level | AI0 | 30001 |
| Water Pressure | AI1 | 30002 |
| Flow Rate | AI2 | 30003 |
| System Status | MSV0 | 40001 |
| Armed Status | BI0 | 10001 |
| Discharge Status | BI1 | 10002 |
| System Arm | BO0 | 00001 |
| Manual Release | BO1 | 00002 |

## Sources
- [EN 13565 Foam Systems](https://www.en-standard.eu/)
- [NFPA 11 Low-Expansion Foam](https://www.nfpa.org/)
- [NFPA 16 Foam-Water Sprinkler](https://www.nfpa.org/)
