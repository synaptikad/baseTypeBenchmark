# Points de Smoke Extraction Fan (Ventilateur désenfumage)

## Synthèse
- **Total points mesure** : 9
- **Total points commande** : 5
- **Total points état** : 7

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Air Flow | sensor-flow-point | m³/h | 0-100000 | 5s | Débit air extrait |
| Static Pressure | sensor-pressure-point | Pa | 0-1000 | 1s | Pression statique |
| Motor Current | sensor-point | A | 0-200 | 1s | Courant moteur |
| Motor Speed | sensor-point | RPM | 0-1800 | 1s | Vitesse moteur |
| Motor Temperature | sensor-temp-point | °C | 0-400°C | 30s | Température moteur |
| Bearing Temperature | sensor-temp-point | °C | 0-150°C | 30s | Température roulements |
| Exhaust Temperature | sensor-temp-point | °C | 0-400°C | 5s | Température gaz extraits |
| Running Hours | sensor-point | h | 0-99999 | 1h | Heures fonctionnement |
| Start Count | sensor-point | count | 0-99999 | Sur événement | Compteur démarrages |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Start Command | cmd-point | - | ON/OFF | Binaire | Démarrage ventilateur |
| Speed Setpoint | cmd-sp-point | % | 0-100% | Analog | Consigne vitesse |
| Zone Select | cmd-sp-point | - | 1-10 | Analog | Sélection zone |
| Mode Select | cmd-sp-point | - | AUTO/MANUAL/FIRE | Enum | Sélection mode |
| Reset Alarms | cmd-point | - | TRIGGER | Binaire | Reset alarmes |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Fan Status | status-point | Enum | STOPPED/RUNNING/FAULT | État général |
| Running Status | status-point | Boolean | FALSE/TRUE | Ventilateur en marche |
| Fire Mode Active | status-point | Boolean | FALSE/TRUE | Mode incendie actif |
| Motor Overload | status-point | Boolean | FALSE/TRUE | Surcharge moteur |
| High Temperature Alarm | status-point | Boolean | FALSE/TRUE | Alarme haute température |
| VFD Status | status-point | Enum | OK/FAULT | État variateur |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| Air Flow | AI0 | 30001 |
| Static Pressure | AI1 | 30002 |
| Motor Current | AI2 | 30003 |
| Exhaust Temperature | AI3 | 30004 |
| Fan Status | MSV0 | 40001 |
| Running Status | BI0 | 10001 |
| Fire Mode Active | BI1 | 10002 |
| Start Command | BO0 | 00001 |
| Speed Setpoint | AO0 | 40101 |

## Sources
- [EN 12101-3 Smoke Exhaust Fans](https://www.en-standard.eu/)
- [NFPA 92 Smoke Control Systems](https://www.nfpa.org/)
- [BS 7346-2 Smoke Ventilation](https://www.bsigroup.com/)
