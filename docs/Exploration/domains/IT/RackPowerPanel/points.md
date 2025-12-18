# Points de Rack Power Panel (PDU)

## Synthèse
- **Total points mesure** : 12
- **Total points commande** : 5
- **Total points état** : 8

## Points de Mesure (Capteurs)
| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| Total Power | sensor-elec-power-point | kW | 0-50 kW | 10s | Puissance totale consommée |
| Total Current | sensor-elec-current-point | A | 0-200 A | 10s | Courant total |
| Voltage L1 | sensor-elec-volt-point | V | 200-250 V | 30s | Tension phase 1 |
| Voltage L2 | sensor-elec-volt-point | V | 200-250 V | 30s | Tension phase 2 |
| Voltage L3 | sensor-elec-volt-point | V | 200-250 V | 30s | Tension phase 3 |
| Power Factor | sensor-elec-pf-point | - | 0.8-1.0 | 1min | Facteur de puissance |
| Energy Total | sensor-elec-energy-point | kWh | 0-999999 | 5min | Énergie totale consommée |
| Temperature | sensor-temp-point | °C | 15-45°C | 1min | Température rack |
| Humidity | sensor-humidity-point | %RH | 20-80% | 1min | Humidité rack |
| Outlet Power | sensor-elec-power-point | W | 0-5000 W | 30s | Puissance par prise |
| Outlet Current | sensor-elec-current-point | A | 0-20 A | 30s | Courant par prise |
| Load Balance | sensor-point | % | 0-100% | 1min | Équilibrage charge phases |

## Points de Commande (Actionneurs/Consignes)
| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| Outlet Control | cmd-point | - | ON/OFF/CYCLE | Enum | Contrôle prise (par prise) |
| Outlet Sequence | cmd-point | - | TRIGGER | Binaire | Séquence démarrage |
| Power Limit | cmd-sp-point | kW | 0-50 | Analog | Limite puissance totale |
| Outlet Priority | cmd-sp-point | - | 1-10 | Analog | Priorité prise (délestage) |
| Reset Peak | cmd-point | - | RESET | Binaire | Reset valeurs crêtes |

## Points d'État
| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| PDU Status | status-point | Enum | OK/WARNING/CRITICAL/OFFLINE | État général |
| Outlet Status | status-point | Enum | ON/OFF/CYCLING | État prise (par prise) |
| Input Status | status-point | Enum | OK/UNDERVOLTAGE/OVERVOLTAGE | État entrée |
| Breaker Status | status-point | Enum | CLOSED/OPEN/TRIPPED | État disjoncteur |
| Overload Status | status-point | Boolean | TRUE/FALSE | Surcharge détectée |
| High Temp Alarm | status-point | Boolean | TRUE/FALSE | Alarme haute température |
| Environmental Alarm | status-point | Boolean | TRUE/FALSE | Alarme environnementale |
| Communication Status | status-point | Enum | CONNECTED/DISCONNECTED | État communication |

## Mappings Protocoles
| Point | SNMP OID | Modbus Register |
|-------|----------|-----------------|
| Total Power | rPDU2DeviceConfigInletPower | 40001-40002 (Float) |
| Total Current | rPDU2DeviceConfigInletCurrent | 40003 |
| Voltage L1 | rPDU2PhaseStatusVoltage.1 | 40004 |
| Temperature | rPDU2TempSensorValue | 40010 |
| Outlet Control | rPDU2OutletSwitchedControlCommand | 00001 |
| Outlet Status | rPDU2OutletSwitchedStatusState | 10001 |
| PDU Status | rPDU2DeviceStatus | 40020 |
| Energy Total | rPDU2DeviceConfigInletEnergy | 40030-40031 |

## Sources
- [APC PowerNet MIB Reference](https://www.apc.com/)
- [Raritan MIB Reference](https://www.raritan.com/)
- [Eaton ePDU MIB](https://www.eaton.com/)
