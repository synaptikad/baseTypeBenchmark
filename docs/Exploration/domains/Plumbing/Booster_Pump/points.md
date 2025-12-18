# Points de Booster Pump (Surpresseur)

## Synthèse
- **Total points mesure** : 10
- **Total points commande** : 5
- **Total points état** : 9

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Inlet Pressure | sensor-pressure-point | bar | 0-10 | 5s | Pression aspiration |
| Outlet Pressure | sensor-pressure-point | bar | 0-16 | 5s | Pression refoulement |
| Flow Rate | sensor-flow-point | L/min | 0-1000 | 10s | Débit total |
| Motor Current | sensor-elec-current-point | A | 0-100 A | 1s | Courant moteur |
| Motor Speed | sensor-point | RPM | 0-3600 | 1s | Vitesse moteur (VFD) |
| Motor Temperature | sensor-temp-point | °C | 30-80°C | 1min | Température moteur |
| Power Consumption | sensor-elec-power-point | kW | 0-50 | 1min | Puissance consommée |
| Running Hours | sensor-point | h | 0-999999 | 1h | Heures fonctionnement |
| Start Count | sensor-point | count | 0-999999 | Sur événement | Démarrages cumulés |
| Energy Consumption | sensor-elec-energy-point | kWh | 0-999999 | 1h | Énergie consommée |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Pump Command | cmd-point | - | START/STOP/AUTO | Enum | Commande pompe |
| Pressure Setpoint | cmd-sp-point | bar | 2-10 | Analog | Consigne pression |
| Speed Override | cmd-sp-point | % | 0-100% | Analog | Forçage vitesse |
| Lead Pump Select | cmd-point | - | PUMP1/PUMP2/AUTO | Enum | Sélection pompe pilote |
| Reset Fault | cmd-point | - | RESET | Binaire | Acquittement défaut |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| Pump Status | status-point | Enum | RUNNING/STOPPED/FAULT | État général |
| Motor Status | status-point | Enum | OK/OVERLOAD/FAULT | État moteur |
| VFD Status | status-point | Enum | OK/WARNING/FAULT | État variateur |
| Pump 1 Status | status-point | Enum | RUNNING/STOPPED/FAULT | État pompe 1 |
| Pump 2 Status | status-point | Enum | RUNNING/STOPPED/FAULT | État pompe 2 |
| Low Suction Pressure | status-point | Boolean | FALSE/TRUE | Alarme basse pression aspiration |
| High Discharge Pressure | status-point | Boolean | FALSE/TRUE | Alarme haute pression |
| Dry Run Protection | status-point | Boolean | FALSE/TRUE | Protection marche à sec |
| Communication Status | status-point | Enum | OK/FAULT | État communication |

## Mappings Protocoles
| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| Outlet Pressure | AI0 | 30001 |
| Flow Rate | AI1 | 30002 |
| Motor Current | AI2 | 30003 |
| Pump Status | MSV0 | 40001 |
| Pump Command | MSV1 | 40101 |
| Pressure Setpoint | AO0 | 40201 |
| Low Suction Pressure | BI0 | 10001 |
| VFD Status | MSV2 | 40010 |

## Sources
- [EN 806 Water Installations](https://www.en-standard.eu/)
- [IEC 60034 Motors](https://webstore.iec.ch/)
- [Europump Guidelines](https://europump.net/)
