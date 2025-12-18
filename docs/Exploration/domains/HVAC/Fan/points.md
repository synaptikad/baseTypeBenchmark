# Points de Fan

## Synthèse
- **Total points mesure** : 14
- **Total points commande** : 8
- **Total points état** : 6

## Points de Mesure (Capteurs)

| Point | Description | Unité | Plage Typique | Tags Haystack | Brick Class | Fréquence |
|-------|-------------|-------|---------------|---------------|-------------|-----------|
| Fan_Speed_Feedback | Vitesse réelle | % | 0-100 | `fan`, `speed`, `sensor` | `brick:Fan_Speed_Sensor` | 5-10s |
| Fan_Speed_RPM | Vitesse rotative | rpm | 0-3600 | `fan`, `speed`, `sensor` | `brick:Speed_Sensor` | 5-10s |
| Fan_Airflow | Débit d'air mesuré | m³/h | 500-100,000 | `fan`, `discharge`, `air`, `flow`, `sensor` | `brick:Air_Flow_Sensor` | 10-30s |
| Fan_Static_Pressure | Pression statique sortie | Pa | 50-2,500 | `fan`, `discharge`, `air`, `pressure`, `sensor` | `brick:Static_Pressure_Sensor` | 10-30s |
| Fan_Differential_Pressure | Pression différentielle | Pa | 50-2,500 | `fan`, `air`, `pressure`, `delta`, `sensor` | `brick:Differential_Pressure_Sensor` | 10-30s |
| Fan_Motor_Current | Courant moteur | A | 0.5-200 | `fan`, `motor`, `elec`, `current`, `sensor` | `brick:Current_Sensor` | 10-60s |
| Fan_Power_Consumption | Puissance électrique | kW | 0.2-100 | `fan`, `motor`, `elec`, `power`, `sensor` | `brick:Power_Sensor` | 10-60s |
| Fan_Energy | Énergie cumulée | kWh | 0-999,999 | `fan`, `motor`, `elec`, `energy`, `sensor` | `brick:Energy_Sensor` | 15-60min |
| Fan_Runtime_Hours | Heures fonctionnement | h | 0-100,000 | `fan`, `run`, `duration`, `sensor` | `brick:Run_Time_Sensor` | 60min |
| Fan_Motor_Temperature | Température moteur | °C | 20-150 | `fan`, `motor`, `temp`, `sensor` | `brick:Motor_Temperature_Sensor` | 30-60s |
| Fan_Bearing_Temperature | Température roulements | °C | 20-120 | `fan`, `bearing`, `temp`, `sensor` | `brick:Bearing_Temperature_Sensor` | 30-60s |
| Fan_Vibration | Niveau vibration | mm/s | 0-50 | `fan`, `vibration`, `sensor` | `brick:Vibration_Sensor` | 60s |
| Fan_VFD_Frequency | Fréquence sortie VFD | Hz | 0-60 | `fan`, `vfd`, `freq`, `sensor` | `brick:Frequency_Sensor` | 5-10s |
| Fan_VFD_DC_Bus_Voltage | Tension bus DC VFD | V | 0-800 | `fan`, `vfd`, `dc`, `volt`, `sensor` | `brick:Voltage_Sensor` | 30-60s |

## Points de Commande (Actionneurs/Consignes)

| Point | Description | Unité | Plage | Tags Haystack | Brick Class |
|-------|-------------|-------|-------|---------------|-------------|
| Fan_Command | Marche/arrêt | - | ON/OFF | `fan`, `run`, `cmd` | `brick:Run_Command` |
| Fan_Enable | Autorisation | - | Enable/Disable | `fan`, `enable`, `cmd` | `brick:Enable_Command` |
| Fan_Speed_Setpoint | Consigne vitesse | % | 0-100 | `fan`, `speed`, `sp` | `brick:Speed_Setpoint` |
| Fan_Speed_Override | Override vitesse | % | 0-100 | `fan`, `speed`, `override`, `sp` | `brick:Speed_Setpoint` |
| Fan_Pressure_Setpoint | Consigne pression | Pa | 100-1,500 | `fan`, `discharge`, `air`, `pressure`, `sp` | `brick:Static_Pressure_Setpoint` |
| Fan_Airflow_Setpoint | Consigne débit | m³/h | 500-100,000 | `fan`, `discharge`, `air`, `flow`, `sp` | `brick:Air_Flow_Setpoint` |
| Fan_Start_Stop_Command | Démarrage VFD | - | Start/Stop | `fan`, `vfd`, `run`, `cmd` | `brick:Start_Stop_Command` |
| Fan_Reset_Command | Reset alarme VFD | - | Reset/Normal | `fan`, `vfd`, `reset`, `cmd` | `brick:Reset_Command` |

## Points d'État

| Point | Description | Valeurs | Tags Haystack | Brick Class |
|-------|-------------|---------|---------------|-------------|
| Fan_Status | État fonctionnement | ON/OFF | `fan`, `run`, `status` | `brick:Run_Status` |
| Fan_Proof_of_Flow | Preuve débit | Flow/No Flow | `fan`, `discharge`, `air`, `flow`, `sensor` | `brick:Air_Flow_Sensor` |
| Fan_Alarm | Alarme générale | Alarm/Normal | `fan`, `alarm` | `brick:Alarm` |
| Fan_VFD_Fault | Défaut variateur | Fault/Normal | `fan`, `vfd`, `fault`, `alarm` | `brick:Fault_Status` |
| Fan_VFD_Ready | VFD prêt | Ready/Not Ready | `fan`, `vfd`, `status` | `brick:Status` |
| Fan_VFD_Fault_Code | Code erreur VFD | 0-255 | `fan`, `vfd`, `fault`, `code`, `sensor` | `brick:Fault_Indicator` |

## Mappings Protocoles

### BACnet

| Point | Object Type | Object ID | Units | Writable |
|-------|-------------|-----------|-------|----------|
| Fan_Command | Binary Output (BO) | BO:1 | - | Yes |
| Fan_Status | Binary Input (BI) | BI:1 | - | No |
| Fan_Speed_Setpoint | Analog Output (AO) | AO:10 | percent | Yes |
| Fan_Speed_Feedback | Analog Input (AI) | AI:10 | percent | No |
| Fan_Airflow | Analog Input (AI) | AI:11 | cubic-feet-per-minute | No |
| Fan_Static_Pressure | Analog Input (AI) | AI:12 | inches-of-water | No |
| Fan_Motor_Current | Analog Input (AI) | AI:13 | amperes | No |
| Fan_Power_Consumption | Analog Input (AI) | AI:14 | kilowatts | No |
| Fan_Energy | Analog Input (AI) | AI:15 | kilowatt-hours | No |
| Fan_Alarm | Binary Input (BI) | BI:3 | - | No |

### Modbus (VFD)

| Point | Type | Adresse | Format | Multiplicateur |
|-------|------|---------|--------|----------------|
| Control Word | Holding Register | 0x0000 | UINT16 | 1 |
| Status Word | Holding Register | 0x0001 | UINT16 | 1 |
| Speed Reference | Holding Register | 0x0002 | UINT16 | 0.01 |
| Output Frequency | Input Register | 3202 | UINT16 | 0.01 Hz |
| Output Current | Input Register | 3203 | UINT16 | 0.1 A |
| DC Bus Voltage | Input Register | 5 | UINT16 | 0.1 V |
| Motor Power | Input Register | 3211 | UINT16 | 0.1 kW |
| Fault Code | Input Register | 8 | UINT16 | 1 |
| Motor Temperature | Input Register | 10 | INT16 | 1 °C |
| Run Time Hours | Input Register | 16-17 | UINT32 | 1 h |

### KNX

| Point | DPT | Format | Notes |
|-------|-----|--------|-------|
| Fan_Command | DPT 1.001 | 1-bit | Switch On/Off |
| Fan_Status | DPT 1.001 | 1-bit | Switch On/Off |
| Fan_Speed_Setpoint | DPT 5.001 | 1-byte | 0-100% |
| Fan_Alarm | DPT 1.005 | 1-bit | Alarm |
| Fan_Power | DPT 14.056 | 4-byte float | kW |

## Sources

- [Project Haystack - Fan Tagging](https://project-haystack.org/doc/docHaystack/Motors)
- [Brick Schema - Fan Equipment](https://brickschema.org/)
- [VFD Control in HVAC Systems](https://www.eaton.com/us/en-us/products/controls-drives-automation-sensors/industrial-control-center/automation-control/hvac-control/vfd-control.html)
- [How VFDs Work in HVAC](https://mepacademy.com/how-variable-frequency-drives-work-in-hvac-systems/)
- [HVAC Vibration Monitoring](https://ncd.io/blog/optimizing-hvac-remote-monitoring-systems-with-vibration-sensors/)
- [Static Pressure in HVAC Systems](https://integracontrols.com/what-is-static-pressure-in-hvac-systems/)
