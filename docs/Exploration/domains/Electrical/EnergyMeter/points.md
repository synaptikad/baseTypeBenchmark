# Points de Energy Meter (Compteur d'Énergie Électrique)

## Synthèse
- **Total points mesure** : 58
- **Total points commande** : 4
- **Total points état** : 12
- **Total général** : 74 points

## Points de Mesure (Capteurs)

### Tensions (Voltage)

| Point | Description | Unité | Plage Typique | Haystack Tags | Brick Class | Fréquence |
|-------|-------------|-------|---------------|---------------|-------------|-----------|
| V_L1_N | Tension phase 1 vers neutre | V | 0-300 V | ac, volt, phase, magnitude, sensor, point | Electric_Voltage_Sensor | 1 s |
| V_L2_N | Tension phase 2 vers neutre | V | 0-300 V | ac, volt, phase, magnitude, sensor, point | Electric_Voltage_Sensor | 1 s |
| V_L3_N | Tension phase 3 vers neutre | V | 0-300 V | ac, volt, phase, magnitude, sensor, point | Electric_Voltage_Sensor | 1 s |
| V_L1_L2 | Tension phase à phase L1-L2 | V | 0-480 V | ac, volt, line, magnitude, sensor, point | Electric_Voltage_Sensor | 1 s |
| V_L2_L3 | Tension phase à phase L2-L3 | V | 0-480 V | ac, volt, line, magnitude, sensor, point | Electric_Voltage_Sensor | 1 s |
| V_L3_L1 | Tension phase à phase L3-L1 | V | 0-480 V | ac, volt, line, magnitude, sensor, point | Electric_Voltage_Sensor | 1 s |
| V_Avg | Tension moyenne triphasée | V | 0-480 V | ac, volt, avg, sensor, point | Electric_Voltage_Sensor | 1 s |
| V_Unbalance | Déséquilibre de tension | % | 0-100 % | ac, volt, imbalance, sensor, point | Voltage_Imbalance_Sensor | 5 s |

### Courants (Current)

| Point | Description | Unité | Plage Typique | Haystack Tags | Brick Class | Fréquence |
|-------|-------------|-------|---------------|---------------|-------------|-----------|
| I_L1 | Courant phase 1 | A | 0-6000 A | ac, current, phase, magnitude, sensor, point | Electric_Current_Sensor | 1 s |
| I_L2 | Courant phase 2 | A | 0-6000 A | ac, current, phase, magnitude, sensor, point | Electric_Current_Sensor | 1 s |
| I_L3 | Courant phase 3 | A | 0-6000 A | ac, current, phase, magnitude, sensor, point | Electric_Current_Sensor | 1 s |
| I_N | Courant neutre | A | 0-6000 A | ac, current, neutral, magnitude, sensor, point | Electric_Current_Sensor | 1 s |
| I_Avg | Courant moyen triphasé | A | 0-6000 A | ac, current, avg, sensor, point | Electric_Current_Sensor | 1 s |
| I_Unbalance | Déséquilibre de courant | % | 0-100 % | ac, current, imbalance, sensor, point | Current_Imbalance_Sensor | 5 s |

### Fréquence

| Point | Description | Unité | Plage Typique | Haystack Tags | Brick Class | Fréquence |
|-------|-------------|-------|---------------|---------------|-------------|-----------|
| Freq | Fréquence du réseau | Hz | 45-65 Hz | ac, freq, sensor, point | Frequency_Sensor | 1 s |

### Puissance Active (Active Power)

| Point | Description | Unité | Plage Typique | Haystack Tags | Brick Class | Fréquence |
|-------|-------------|-------|---------------|---------------|-------------|-----------|
| P_L1 | Puissance active phase 1 | kW | -10000 - +10000 kW | ac, active, power, phase, sensor, point | Electric_Power_Sensor | 1 s |
| P_L2 | Puissance active phase 2 | kW | -10000 - +10000 kW | ac, active, power, phase, sensor, point | Electric_Power_Sensor | 1 s |
| P_L3 | Puissance active phase 3 | kW | -10000 - +10000 kW | ac, active, power, phase, sensor, point | Electric_Power_Sensor | 1 s |
| P_Total | Puissance active totale | kW | -10000 - +10000 kW | ac, active, power, total, sensor, point | Electric_Power_Sensor | 1 s |

### Puissance Réactive (Reactive Power)

| Point | Description | Unité | Plage Typique | Haystack Tags | Brick Class | Fréquence |
|-------|-------------|-------|---------------|---------------|-------------|-----------|
| Q_L1 | Puissance réactive phase 1 | kVAR | -10000 - +10000 kVAR | ac, reactive, power, phase, sensor, point | Reactive_Power_Sensor | 1 s |
| Q_L2 | Puissance réactive phase 2 | kVAR | -10000 - +10000 kVAR | ac, reactive, power, phase, sensor, point | Reactive_Power_Sensor | 1 s |
| Q_L3 | Puissance réactive phase 3 | kVAR | -10000 - +10000 kVAR | ac, reactive, power, phase, sensor, point | Reactive_Power_Sensor | 1 s |
| Q_Total | Puissance réactive totale | kVAR | -10000 - +10000 kVAR | ac, reactive, power, total, sensor, point | Reactive_Power_Sensor | 1 s |

### Puissance Apparente (Apparent Power)

| Point | Description | Unité | Plage Typique | Haystack Tags | Brick Class | Fréquence |
|-------|-------------|-------|---------------|---------------|-------------|-----------|
| S_L1 | Puissance apparente phase 1 | kVA | 0-10000 kVA | ac, apparent, power, phase, sensor, point | Apparent_Power_Sensor | 1 s |
| S_L2 | Puissance apparente phase 2 | kVA | 0-10000 kVA | ac, apparent, power, phase, sensor, point | Apparent_Power_Sensor | 1 s |
| S_L3 | Puissance apparente phase 3 | kVA | 0-10000 kVA | ac, apparent, power, phase, sensor, point | Apparent_Power_Sensor | 1 s |
| S_Total | Puissance apparente totale | kVA | 0-10000 kVA | ac, apparent, power, total, sensor, point | Apparent_Power_Sensor | 1 s |

### Facteur de Puissance (Power Factor)

| Point | Description | Unité | Plage Typique | Haystack Tags | Brick Class | Fréquence |
|-------|-------------|-------|---------------|---------------|-------------|-----------|
| PF_L1 | Facteur de puissance phase 1 (True PF) | - | -1.0 - +1.0 | ac, pf, phase, sensor, point | Power_Factor_Sensor | 1 s |
| PF_L2 | Facteur de puissance phase 2 (True PF) | - | -1.0 - +1.0 | ac, pf, phase, sensor, point | Power_Factor_Sensor | 1 s |
| PF_L3 | Facteur de puissance phase 3 (True PF) | - | -1.0 - +1.0 | ac, pf, phase, sensor, point | Power_Factor_Sensor | 1 s |
| PF_Total | Facteur de puissance total (True PF) | - | -1.0 - +1.0 | ac, pf, total, sensor, point | Power_Factor_Sensor | 1 s |
| DPF_L1 | Facteur de puissance de déplacement phase 1 (cos φ) | - | -1.0 - +1.0 | ac, displacement, pf, phase, sensor, point | Power_Factor_Sensor | 1 s |
| DPF_L2 | Facteur de puissance de déplacement phase 2 (cos φ) | - | -1.0 - +1.0 | ac, displacement, pf, phase, sensor, point | Power_Factor_Sensor | 1 s |
| DPF_L3 | Facteur de puissance de déplacement phase 3 (cos φ) | - | -1.0 - +1.0 | ac, displacement, pf, phase, sensor, point | Power_Factor_Sensor | 1 s |
| DPF_Total | Facteur de puissance de déplacement total (cos φ) | - | -1.0 - +1.0 | ac, displacement, pf, total, sensor, point | Power_Factor_Sensor | 1 s |

### Énergie Active (Active Energy)

| Point | Description | Unité | Plage Typique | Haystack Tags | Brick Class | Fréquence |
|-------|-------------|-------|---------------|---------------|-------------|-----------|
| Energy_Active_Import | Énergie active importée (totale) | kWh | 0-999999999 kWh | ac, active, import, energy, sensor, point, elec, meter | Energy_Sensor | 15 min |
| Energy_Active_Export | Énergie active exportée (totale) | kWh | 0-999999999 kWh | ac, active, export, energy, sensor, point, elec, meter | Energy_Sensor | 15 min |
| Energy_Active_Net | Énergie active nette (import - export) | kWh | -999999999 - +999999999 kWh | ac, active, net, energy, sensor, point, elec, meter | Energy_Sensor | 15 min |
| Energy_Active_T1 | Énergie active tarif 1 (heures pleines) | kWh | 0-999999999 kWh | ac, active, import, energy, sensor, point, elec, meter | Energy_Sensor | 15 min |
| Energy_Active_T2 | Énergie active tarif 2 (heures creuses) | kWh | 0-999999999 kWh | ac, active, import, energy, sensor, point, elec, meter | Energy_Sensor | 15 min |
| Energy_Active_T3 | Énergie active tarif 3 (épaule) | kWh | 0-999999999 kWh | ac, active, import, energy, sensor, point, elec, meter | Energy_Sensor | 15 min |
| Energy_Active_T4 | Énergie active tarif 4 (pointe) | kWh | 0-999999999 kWh | ac, active, import, energy, sensor, point, elec, meter | Energy_Sensor | 15 min |

### Énergie Réactive (Reactive Energy)

| Point | Description | Unité | Plage Typique | Haystack Tags | Brick Class | Fréquence |
|-------|-------------|-------|---------------|---------------|-------------|-----------|
| Energy_Reactive_Import | Énergie réactive importée (inductive) | kVARh | 0-999999999 kVARh | ac, reactive, import, energy, sensor, point, elec, meter | Energy_Sensor | 15 min |
| Energy_Reactive_Export | Énergie réactive exportée (capacitive) | kVARh | 0-999999999 kVARh | ac, reactive, export, energy, sensor, point, elec, meter | Energy_Sensor | 15 min |

### Énergie Apparente (Apparent Energy)

| Point | Description | Unité | Plage Typique | Haystack Tags | Brick Class | Fréquence |
|-------|-------------|-------|---------------|---------------|-------------|-----------|
| Energy_Apparent | Énergie apparente totale | kVAh | 0-999999999 kVAh | ac, apparent, energy, sensor, point, elec, meter | Energy_Sensor | 15 min |

### Demande Maximale (Maximum Demand)

| Point | Description | Unité | Plage Typique | Haystack Tags | Brick Class | Fréquence |
|-------|-------------|-------|---------------|---------------|-------------|-----------|
| Demand_P_Max | Demande maximale puissance active | kW | 0-10000 kW | ac, active, power, demand, max, sensor, point | Peak_Power_Demand_Sensor | 15 min |
| Demand_Q_Max | Demande maximale puissance réactive | kVAR | 0-10000 kVAR | ac, reactive, power, demand, max, sensor, point | Peak_Power_Demand_Sensor | 15 min |
| Demand_S_Max | Demande maximale puissance apparente | kVA | 0-10000 kVA | ac, apparent, power, demand, max, sensor, point | Peak_Power_Demand_Sensor | 15 min |
| Demand_P_Current | Demande courante puissance active (fenêtre glissante) | kW | 0-10000 kW | ac, active, power, demand, sensor, point | Peak_Power_Demand_Sensor | 1 min |

### Qualité de l'Énergie - Harmoniques (Power Quality - Harmonics)

| Point | Description | Unité | Plage Typique | Haystack Tags | Brick Class | Fréquence |
|-------|-------------|-------|---------------|---------------|-------------|-----------|
| THD_V_L1 | Distorsion harmonique totale tension phase 1 | % | 0-100 % | ac, volt, thd, phase, sensor, point | THD_Sensor | 5 s |
| THD_V_L2 | Distorsion harmonique totale tension phase 2 | % | 0-100 % | ac, volt, thd, phase, sensor, point | THD_Sensor | 5 s |
| THD_V_L3 | Distorsion harmonique totale tension phase 3 | % | 0-100 % | ac, volt, thd, phase, sensor, point | THD_Sensor | 5 s |
| THD_I_L1 | Distorsion harmonique totale courant phase 1 | % | 0-100 % | ac, current, thd, phase, sensor, point | THD_Sensor | 5 s |
| THD_I_L2 | Distorsion harmonique totale courant phase 2 | % | 0-100 % | ac, current, thd, phase, sensor, point | THD_Sensor | 5 s |
| THD_I_L3 | Distorsion harmonique totale courant phase 3 | % | 0-100 % | ac, current, thd, phase, sensor, point | THD_Sensor | 5 s |

### Qualité de l'Énergie - Événements (Power Quality - Events)

| Point | Description | Unité | Plage Typique | Haystack Tags | Brick Class | Fréquence |
|-------|-------------|-------|---------------|---------------|-------------|-----------|
| Sag_Count | Nombre de creux de tension (sags) | count | 0-65535 | ac, volt, sag, event, sensor, point | Sensor | event |
| Swell_Count | Nombre de surtensions (swells) | count | 0-65535 | ac, volt, swell, event, sensor, point | Sensor | event |
| Crest_Factor_V | Facteur de crête tension | - | 1.0-5.0 | ac, volt, crest, sensor, point | Sensor | 5 s |
| Crest_Factor_I | Facteur de crête courant | - | 1.0-10.0 | ac, current, crest, sensor, point | Sensor | 5 s |

## Points de Commande (Actionneurs/Consignes)

| Point | Description | Unité | Plage | Haystack Tags | Brick Class |
|-------|-------------|-------|-------|---------------|-------------|
| Reset_Energy | Réinitialisation compteur d'énergie | bool | 0/1 | cmd, reset, energy, point | Command |
| Reset_Demand | Réinitialisation demande maximale | bool | 0/1 | cmd, reset, demand, point | Command |
| Reset_Alarms | Réinitialisation alarmes | bool | 0/1 | cmd, reset, alarm, point | Command |
| CT_Ratio | Rapport transformateur de courant (TC) | - | 1-10000 | cmd, config, ratio, point | Setpoint |

## Points d'État

| Point | Description | Valeurs | Haystack Tags | Brick Class |
|-------|-------------|---------|---------------|-------------|
| Comm_Status | État communication | 0=OK, 1=Erreur | status, comm, point | Communication_Status |
| Phase_Rotation | Sens de rotation des phases | 0=ABC, 1=CBA, 2=Erreur | status, rotation, phase, point | Status |
| Phase_Loss_L1 | Perte phase 1 | 0=OK, 1=Perte | alarm, phase, loss, point | Alarm |
| Phase_Loss_L2 | Perte phase 2 | 0=OK, 1=Perte | alarm, phase, loss, point | Alarm |
| Phase_Loss_L3 | Perte phase 3 | 0=OK, 1=Perte | alarm, phase, loss, point | Alarm |
| Reverse_Power | Détection puissance inverse | 0=Normal, 1=Inverse | alarm, reverse, power, point | Alarm |
| Over_Voltage | Alarme surtension | 0=OK, 1=Alarme | alarm, over, volt, point | Alarm |
| Under_Voltage | Alarme sous-tension | 0=OK, 1=Alarme | alarm, under, volt, point | Alarm |
| Over_Current | Alarme surintensité | 0=OK, 1=Alarme | alarm, over, current, point | Alarm |
| THD_Alarm | Alarme distorsion harmonique excessive | 0=OK, 1=Alarme | alarm, thd, point | Alarm |
| Tariff_Active | Tarif actif actuel | 1-4 | status, tariff, point | Status |
| Meter_Time | Horodatage compteur (synchronisation) | timestamp | status, time, point | Status |

## Mappings Protocoles

### BACnet

| Point | Object Type | Object Instance | Property | Units | Access |
|-------|-------------|-----------------|----------|-------|--------|
| V_L1_N | Analog Input | 1 | Present_Value | Volts | R |
| V_L2_N | Analog Input | 2 | Present_Value | Volts | R |
| V_L3_N | Analog Input | 3 | Present_Value | Volts | R |
| I_L1 | Analog Input | 10 | Present_Value | Amperes | R |
| I_L2 | Analog Input | 11 | Present_Value | Amperes | R |
| I_L3 | Analog Input | 12 | Present_Value | Amperes | R |
| Freq | Analog Input | 20 | Present_Value | Hertz | R |
| P_Total | Analog Input | 30 | Present_Value | Kilowatts | R |
| Q_Total | Analog Input | 31 | Present_Value | Kilovolt-Amperes-Reactive | R |
| S_Total | Analog Input | 32 | Present_Value | Kilovolt-Amperes | R |
| PF_Total | Analog Input | 40 | Present_Value | No-Units | R |
| Energy_Active_Import | Accumulator | 100 | Present_Value | Kilowatt-Hours | R |
| Energy_Active_Export | Accumulator | 101 | Present_Value | Kilowatt-Hours | R |
| Energy_Reactive_Import | Accumulator | 110 | Present_Value | Kilovolt-Amperes-Reactive-Hours | R |
| Demand_P_Max | Analog Value | 120 | Present_Value | Kilowatts | R |
| THD_V_L1 | Analog Input | 200 | Present_Value | Percent | R |
| THD_I_L1 | Analog Input | 210 | Present_Value | Percent | R |
| Comm_Status | Binary Value | 300 | Present_Value | No-Units | R |
| Phase_Loss_L1 | Binary Value | 310 | Present_Value | No-Units | R |
| Reset_Energy | Binary Value | 400 | Present_Value | No-Units | R/W |

### Modbus RTU/TCP

| Point | Type | Registre | Data Type | Facteur | Unités |
|-------|------|----------|-----------|---------|--------|
| V_L1_N | Input Reg | 30001 | UINT16 | 0.1 | V |
| V_L2_N | Input Reg | 30003 | UINT16 | 0.1 | V |
| V_L3_N | Input Reg | 30005 | UINT16 | 0.1 | V |
| I_L1 | Input Reg | 30013 | UINT32 | 0.001 | A |
| I_L2 | Input Reg | 30015 | UINT32 | 0.001 | A |
| I_L3 | Input Reg | 30017 | UINT32 | 0.001 | A |
| Freq | Input Reg | 30057 | UINT16 | 0.01 | Hz |
| P_Total | Input Reg | 30053 | INT32 | 0.001 | kW |
| Q_Total | Input Reg | 30063 | INT32 | 0.001 | kVAR |
| S_Total | Input Reg | 30061 | UINT32 | 0.001 | kVA |
| PF_Total | Input Reg | 30059 | INT16 | 0.001 | - |
| Energy_Active_Import | Input Reg | 30001 (bloc 2) | UINT64 | 0.01 | kWh |
| Energy_Active_Export | Input Reg | 30009 (bloc 2) | UINT64 | 0.01 | kWh |
| Energy_Reactive_Import | Input Reg | 30017 (bloc 2) | UINT64 | 0.01 | kVARh |
| Demand_P_Max | Input Reg | 30201 | UINT32 | 0.001 | kW |
| THD_V_L1 | Input Reg | 30301 | UINT16 | 0.1 | % |
| THD_I_L1 | Input Reg | 30321 | UINT16 | 0.1 | % |
| Reset_Energy | Holding Reg | 40001 | UINT16 | 1 | - |
| CT_Ratio | Holding Reg | 40100 | UINT16 | 1 | - |

### KNX (si applicable via passerelle)

| Point | DPT | Description | Unités |
|-------|-----|-------------|--------|
| V_L1_N | DPT 14.027 | Tension électrique | V |
| I_L1 | DPT 14.019 | Courant électrique | A |
| P_Total | DPT 14.056 | Puissance active | kW |
| Energy_Active_Import | DPT 12.001 | Compteur énergie (unsigned 32 bits) | kWh |
| Freq | DPT 14.033 | Fréquence | Hz |
| PF_Total | DPT 14.000 | Valeur flottante (facteur de puissance) | - |
| Comm_Status | DPT 1.001 | Booléen (on/off) | - |

## Sources

1. https://project-haystack.org/doc/docHaystack/Meters - Project Haystack Meters Documentation
2. https://docs.brickschema.org/modeling/meters.html - Brick Schema Meters Modeling
3. https://www.productinfo.schneider-electric.com/pm5300/ - Schneider Electric PowerLogic PM5300 Series
4. https://library.e.abb.com/public/3d43ee0be2a241eca99274d3814d060d/M4M%202X_catalogue_9AKK107491A7132.pdf - ABB M4M Network Analyzers
5. https://cache.industry.siemens.com/dl/files/595/34261595/att_951630/v1/manual_pac4200_en-US_en-US.pdf - Siemens SENTRON PAC4200 System Manual
6. https://www.gavazziautomation.com/fileadmin/images/PIM/OTHERSTUFF/COMPRO/EM330_EM340_ET330_ET340_CP.pdf - Carlo Gavazzi EM340 Communication Protocol
7. https://blog.se.com/energy-management-energy-efficiency/energy-regulations/2016/10/18/understanding-iec-standard-makes-meter-comparisons-easier/ - Understanding IEC 61557-12 Standard
8. https://www.accuenergy.com/products/acuvim-3-power-quality-meters/ - Acuvim 3 Series Power Quality Meters (IEC 61000-4-30 Class A)
9. https://clouglobal.com/accurate-energy-measurements-in-unbalanced-three-phase-systems/ - Accurate Energy Measurements
10. https://www.accuenergy.com/application-solutions/time-of-use-metering/ - Time of Use (TOU) Energy Metering