# Points de Fire Pump (Pompe incendie)

## Synthèse
- **Total points mesure** : 10
- **Total points commande** : 5
- **Total points état** : 8

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Discharge Pressure | sensor-pressure-point | bar | 0-16 | 1s | Pression refoulement |
| Suction Pressure | sensor-pressure-point | bar | 0-6 | 1s | Pression aspiration |
| Flow Rate | sensor-flow-point | L/min | 0-5000 | 1s | Débit pompe |
| Motor Current | sensor-point | A | 0-500 | 1s | Courant moteur |
| Motor Speed | sensor-point | RPM | 0-3600 | 1s | Vitesse moteur |
| Motor Temperature | sensor-temp-point | °C | 0-150°C | 30s | Température moteur |
| Bearing Temperature | sensor-temp-point | °C | 0-100°C | 30s | Température roulements |
| Tank Level | sensor-level-point | % | 0-100% | 1min | Niveau réservoir |
| Running Hours | sensor-point | h | 0-99999 | 1h | Heures fonctionnement |
| Start Count | sensor-point | count | 0-99999 | Sur événement | Compteur démarrages |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Start Command | cmd-point | - | ON/OFF | Binaire | Démarrage pompe |
| Stop Command | cmd-point | - | TRIGGER | Binaire | Arrêt pompe |
| Mode Select | cmd-sp-point | - | AUTO/MANUAL/OFF | Enum | Sélection mode |
| Test Run | cmd-point | - | TRIGGER | Binaire | Test hebdomadaire |
| Reset Alarms | cmd-point | - | TRIGGER | Binaire | Reset alarmes |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Pump Status | status-point | Enum | STOPPED/RUNNING/FAULT | État général |
| Running Status | status-point | Boolean | FALSE/TRUE | Pompe en marche |
| Mode Status | status-point | Enum | AUTO/MANUAL/OFF | Mode actuel |
| Motor Overload | status-point | Boolean | FALSE/TRUE | Surcharge moteur |
| Low Suction Alarm | status-point | Boolean | FALSE/TRUE | Alarme basse pression aspiration |
| Power Available | status-point | Boolean | FALSE/TRUE | Alimentation disponible |
| Controller Status | status-point | Enum | OK/FAULT | État contrôleur |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register | NFPA 20 |
|-------|---------------|-----------------|---------|
| Discharge Pressure | AI0 | 30001 | Required |
| Suction Pressure | AI1 | 30002 | Required |
| Flow Rate | AI2 | 30003 | - |
| Motor Current | AI3 | 30004 | - |
| Pump Status | MSV0 | 40001 | Required |
| Running Status | BI0 | 10001 | Required |
| Start Command | BO0 | 00001 | - |
| Mode Select | MSV1 | 40002 | - |

## Sources
- [EN 12845 Sprinkler Systems](https://www.en-standard.eu/)
- [NFPA 20 Stationary Pumps](https://www.nfpa.org/)
- [FM Global Data Sheet 3-7](https://www.fmglobal.com/)
