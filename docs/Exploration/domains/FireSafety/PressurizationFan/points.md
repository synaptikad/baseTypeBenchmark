# Points de Pressurization Fan (Ventilateur de surpression)

## Synthèse
- **Total points mesure** : 8
- **Total points commande** : 5
- **Total points état** : 7

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Differential Pressure | sensor-pressure-point | Pa | 0-100 | 1s | Pression différentielle |
| Air Flow | sensor-flow-point | m³/h | 0-50000 | 5s | Débit air |
| Motor Current | sensor-point | A | 0-100 | 1s | Courant moteur |
| Motor Speed | sensor-point | RPM | 0-3600 | 1s | Vitesse moteur |
| Motor Temperature | sensor-temp-point | °C | 0-150°C | 30s | Température moteur |
| Bearing Temperature | sensor-temp-point | °C | 0-100°C | 30s | Température roulements |
| Running Hours | sensor-point | h | 0-99999 | 1h | Heures fonctionnement |
| Start Count | sensor-point | count | 0-99999 | Sur événement | Compteur démarrages |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Start Command | cmd-point | - | ON/OFF | Binaire | Démarrage ventilateur |
| Speed Setpoint | cmd-sp-point | % | 0-100% | Analog | Consigne vitesse |
| Pressure Setpoint | cmd-sp-point | Pa | 20-80 | Analog | Consigne pression |
| Mode Select | cmd-sp-point | - | AUTO/MANUAL/OFF | Enum | Sélection mode |
| Reset Alarms | cmd-point | - | TRIGGER | Binaire | Reset alarmes |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Fan Status | status-point | Enum | STOPPED/RUNNING/FAULT | État général |
| Running Status | status-point | Boolean | FALSE/TRUE | Ventilateur en marche |
| Mode Status | status-point | Enum | AUTO/MANUAL/OFF | Mode actuel |
| Motor Overload | status-point | Boolean | FALSE/TRUE | Surcharge moteur |
| Low Pressure Alarm | status-point | Boolean | FALSE/TRUE | Alarme basse pression |
| VFD Status | status-point | Enum | OK/FAULT | État variateur |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| Differential Pressure | AI0 | 30001 |
| Air Flow | AI1 | 30002 |
| Motor Current | AI2 | 30003 |
| Motor Speed | AI3 | 30004 |
| Fan Status | MSV0 | 40001 |
| Running Status | BI0 | 10001 |
| Start Command | BO0 | 00001 |
| Speed Setpoint | AO0 | 40101 |
| Pressure Setpoint | AO1 | 40102 |

## Sources
- [EN 12101-6 Pressure Differential Systems](https://www.en-standard.eu/)
- [NFPA 92 Smoke Control Systems](https://www.nfpa.org/)
- [BS 5588-4 Smoke Control](https://www.bsigroup.com/)
