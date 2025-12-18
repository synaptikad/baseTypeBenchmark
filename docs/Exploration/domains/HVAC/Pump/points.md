# Points de Pump

## Synthèse
- **Total points mesure** : 18
- **Total points commande** : 10
- **Total points état** : 14

## Points de Mesure (Capteurs)

| Point | Description | Unité | Plage Typique | Haystack Tags | Brick Class | Fréquence |
|-------|-------------|-------|---------------|---------------|-------------|-----------|
| Flow | Débit volumétrique | m³/h | 0-500 | `chilled water flow sensor pump equipRef` | `brick:Water_Flow_Sensor` | 5-10s |
| Differential_Pressure | Pression différentielle | kPa | 0-1000 | `discharge pressure sensor pump equipRef` | `brick:Differential_Pressure_Sensor` | 5-10s |
| Suction_Pressure | Pression aspiration | kPa | -100 à 200 | `suction pressure sensor pump equipRef` | `brick:Suction_Pressure_Sensor` | 10s |
| Discharge_Pressure | Pression refoulement | kPa | 0-1000 | `discharge pressure sensor pump equipRef` | `brick:Discharge_Pressure_Sensor` | 10s |
| Motor_Current | Courant moteur | A | 0-200 | `elec current sensor motor pump equipRef` | `brick:Electric_Current_Sensor` | 5-10s |
| Motor_Power | Puissance électrique | kW | 0-100 | `elec power sensor motor pump equipRef` | `brick:Electric_Power_Sensor` | 10s |
| Energy_Consumption | Énergie cumulée | kWh | 0-999999 | `elec energy sensor motor pump equipRef` | `brick:Energy_Sensor` | 1min |
| Motor_Voltage | Tension moteur | V | 0-480 | `elec volt sensor motor pump equipRef` | `brick:Voltage_Sensor` | 30s |
| Speed_Feedback | Vitesse moteur (VFD) | rpm / Hz | 0-3600 / 0-60 | `speed sensor vfd pump equipRef` | `brick:Speed_Sensor` | 5s |
| VFD_Frequency | Fréquence sortie VFD | Hz | 0-60 | `freq sensor vfd pump equipRef` | `brick:Frequency_Sensor` | 5s |
| VFD_Output_Percent | Pourcentage sortie VFD | % | 0-100 | `output sensor vfd pump equipRef` | `brick:VFD_Output_Sensor` | 5s |
| Supply_Water_Temp | Température eau départ | °C | 4-90 | `chilled water supply temp sensor pump equipRef` | `brick:Supply_Water_Temperature_Sensor` | 30s |
| Return_Water_Temp | Température eau retour | °C | 4-90 | `chilled water return temp sensor pump equipRef` | `brick:Return_Water_Temperature_Sensor` | 30s |
| Motor_Winding_Temp | Température enroulements | °C | 0-150 | `temp sensor motor windings pump equipRef` | `brick:Motor_Temperature_Sensor` | 30s |
| Bearing_Temp | Température paliers | °C | 20-100 | `temp sensor bearing pump equipRef` | `brick:Bearing_Temperature_Sensor` | 1min |
| Vibration_Level | Niveau vibration | mm/s RMS | 0-50 | `vibration sensor pump equipRef` | `brick:Vibration_Sensor` | 1-5min |
| Run_Hours | Heures fonctionnement | h | 0-999999 | `run sensor totalizer pump equipRef` | `brick:Run_Time_Sensor` | 1h |
| Power_Factor | Facteur de puissance | - | 0-1 | `pf sensor motor pump equipRef` | `brick:Power_Factor_Sensor` | 1min |

## Points de Commande (Actionneurs/Consignes)

| Point | Description | Unité | Plage | Haystack Tags | Brick Class |
|-------|-------------|-------|-------|---------------|-------------|
| Start_Stop_Cmd | Marche/arrêt | - | 0/1 | `run cmd pump equipRef` | `brick:Run_Command` |
| Speed_Setpoint | Consigne vitesse VFD | % / Hz | 0-100 / 0-60 | `speed sp vfd pump equipRef` | `brick:Speed_Setpoint` |
| Pressure_Setpoint | Consigne pression diff. | kPa | 50-500 | `pressure sp pump equipRef` | `brick:Differential_Pressure_Setpoint` |
| Flow_Setpoint | Consigne débit | m³/h | 5-500 | `flow sp pump equipRef` | `brick:Water_Flow_Setpoint` |
| Enable_Cmd | Autorisation système | - | 0/1 | `enable cmd pump equipRef` | `brick:Enable_Command` |
| Reset_Alarm_Cmd | Réarmement alarmes | - | pulse | `reset cmd alarm pump equipRef` | `brick:Reset_Command` |
| Lead_Lag_Select | Sélection Lead/Lag | - | 0/1 | `lead cmd pump equipRef` | `brick:Lead_Lag_Command` |
| VFD_Start_Cmd | Démarrage VFD | - | 0/1 | `run cmd vfd pump equipRef` | `brick:Start_Command` |
| VFD_Reset_Cmd | Reset VFD | - | pulse | `reset cmd vfd pump equipRef` | `brick:Reset_Command` |
| Schedule_Override | Forçage manuel | - | 0/1 | `override cmd pump equipRef` | `brick:Override_Command` |

## Points d'État

| Point | Description | Valeurs | Haystack Tags | Brick Class |
|-------|-------------|---------|---------------|-------------|
| Run_Status | État marche | Off/On | `run status pump equipRef` | `brick:Run_Status` |
| Fault_Status | Défaut général | Normal/Fault | `fault status pump equipRef` | `brick:Fault_Status` |
| Alarm_Status | Alarme active | Normal/Alarm | `alarm status pump equipRef` | `brick:Alarm_Status` |
| HOA_Mode | Mode Hand-Off-Auto | Off/Hand/Auto | `mode status pump equipRef` | `brick:Operating_Mode_Status` |
| VFD_Ready | VFD prêt | Not Ready/Ready | `ready status vfd pump equipRef` | `brick:VFD_Ready_Status` |
| VFD_Running | VFD en marche | Stopped/Running | `run status vfd pump equipRef` | `brick:Run_Status` |
| VFD_Fault | Défaut VFD | Normal/Fault | `fault status vfd pump equipRef` | `brick:Fault_Status` |
| Thermal_Overload | Surcharge thermique | Normal/Trip | `overload status motor pump equipRef` | `brick:Overload_Status` |
| Low_Flow_Alarm | Alarme débit bas | Normal/Low Flow | `flow alarm pump equipRef` | `brick:Low_Flow_Alarm_Status` |
| High_Vibration_Alarm | Alarme vibration | Normal/High Vib | `vibration alarm pump equipRef` | `brick:High_Vibration_Alarm` |
| Seal_Leak_Alarm | Fuite joint | Normal/Leak | `leak alarm seal pump equipRef` | `brick:Seal_Leak_Alarm` |
| Lead_Lag_Status | Statut Lead/Lag | Lag/Lead | `lead status pump equipRef` | `brick:Lead_Status` |
| Proof_Of_Flow | Preuve débit | No Flow/Flow OK | `flow switch pump equipRef` | `brick:Flow_Switch_Status` |
| Isolation_Valve_Status | Vanne isolation | Closed/Open | `isolation valve status pump equipRef` | `brick:Valve_Position_Status` |

## Mappings Protocoles

### BACnet

| Point | Object Type | Object ID | Units | R/W |
|-------|-------------|-----------|-------|-----|
| Flow | Analog Input (AI) | AI:0 | m³/h | R |
| Differential_Pressure | Analog Input (AI) | AI:1 | kPa | R |
| Motor_Current | Analog Input (AI) | AI:4 | A | R |
| Motor_Power | Analog Input (AI) | AI:5 | kW | R |
| Speed_Feedback | Analog Input (AI) | AI:8 | Hz | R |
| Start_Stop_Cmd | Binary Output (BO) | BO:0 | - | W |
| Speed_Setpoint | Analog Output (AO) | AO:0 | % | W |
| Pressure_Setpoint | Analog Output (AO) | AO:1 | kPa | W |
| Run_Status | Binary Input (BI) | BI:0 | - | R |
| Fault_Status | Binary Input (BI) | BI:1 | - | R |
| VFD_Fault | Binary Input (BI) | BI:5 | - | R |

### Modbus (VFD)

| Point | Type | Registre | Fonction | Échelle |
|-------|------|----------|----------|---------|
| VFD_Frequency | Input Register | 3202 | 04 Read | 0.01 Hz |
| Motor_Current | Input Register | 3204 | 04 Read | 0.01 A |
| Motor_Power | Input Register | 3211 | 04 Read | 0.1 kW |
| Speed_Setpoint | Holding Register | 2101 | 06/16 Write | 0.01 Hz |
| VFD_Start_Cmd | Coil | 8501 | 05 Write | 1=Start |
| VFD_Reset_Cmd | Coil | 8502 | 05 Write | Pulse |
| VFD_Run_Status | Discrete Input | 3201 | 02 Read | 1=Running |

## Sources

- [Project Haystack - Chilled Water Pump Tagging](https://project-haystack.org/forum/topic/127)
- [Brick Schema - Pump Ontology](https://brickschema.org/)
- [Grundfos - Variable Frequency Drive](https://www.grundfos.com/us/learn/research-and-insights/variable-frequency-drive)
- [Pumps and Systems - VFDs Improve Motor Pump Control](https://www.pumpsandsystems.com/vfds-improve-motor-pump-control)
- [Lead-Lag Pump Control](https://www.predig.com/app/lead-lag-pump-alternation-control)
- [Vibration Monitoring for Predictive Maintenance](https://www.bannerengineering.com/us/en/solutions/iiot-data-driven-factory/vibration-monitoring-for-predictive-maintenance.html)
