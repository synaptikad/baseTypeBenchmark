# Points de Generator (Groupe Électrogène)

## Synthèse
- **Total points mesure** : 43
- **Total points commande** : 8
- **Total points état** : 14
- **Total général** : 65 points

## Points de Mesure (Capteurs)

### Mesures Électriques Générateur

| Point | Description | Unité | Plage Typique | Haystack Tags | Brick Class | Fréquence |
|-------|-------------|-------|---------------|---------------|-------------|-----------|
| Generator_Voltage_L1_N | Tension phase L1 vers neutre | V | 0-277 V | generator, voltage, phase, sensor, elec-volt, ac-elec | AC_Voltage_Sensor | 1 s |
| Generator_Voltage_L2_N | Tension phase L2 vers neutre | V | 0-277 V | generator, voltage, phase, sensor, elec-volt, ac-elec | AC_Voltage_Sensor | 1 s |
| Generator_Voltage_L3_N | Tension phase L3 vers neutre | V | 0-277 V | generator, voltage, phase, sensor, elec-volt, ac-elec | AC_Voltage_Sensor | 1 s |
| Generator_Voltage_L1_L2 | Tension ligne L1-L2 | V | 0-480 V | generator, voltage, phase, sensor, elec-volt, ac-elec | AC_Voltage_Sensor | 1 s |
| Generator_Voltage_L2_L3 | Tension ligne L2-L3 | V | 0-480 V | generator, voltage, phase, sensor, elec-volt, ac-elec | AC_Voltage_Sensor | 1 s |
| Generator_Voltage_L3_L1 | Tension ligne L3-L1 | V | 0-480 V | generator, voltage, phase, sensor, elec-volt, ac-elec | AC_Voltage_Sensor | 1 s |
| Generator_Voltage_Avg | Tension moyenne triphasée | V | 0-480 V | generator, voltage, avg, sensor, elec-volt, ac-elec | AC_Voltage_Sensor | 1 s |
| Generator_Current_L1 | Courant phase L1 | A | 0-5000 A | generator, current, phase, sensor, elec-current, ac-elec | AC_Current_Sensor | 1 s |
| Generator_Current_L2 | Courant phase L2 | A | 0-5000 A | generator, current, phase, sensor, elec-current, ac-elec | AC_Current_Sensor | 1 s |
| Generator_Current_L3 | Courant phase L3 | A | 0-5000 A | generator, current, phase, sensor, elec-current, ac-elec | AC_Current_Sensor | 1 s |
| Generator_Current_Avg | Courant moyen triphasé | A | 0-5000 A | generator, current, avg, sensor, elec-current, ac-elec | AC_Current_Sensor | 1 s |
| Generator_Frequency | Fréquence électrique | Hz | 47-63 Hz | generator, freq, sensor, ac-elec | AC_Frequency_Sensor | 1 s |
| Generator_Power_kW_L1 | Puissance active phase L1 | kW | 0-2000 kW | generator, power, active, phase, sensor, elec-power, ac-elec | Active_Power_Sensor | 1 s |
| Generator_Power_kW_L2 | Puissance active phase L2 | kW | 0-2000 kW | generator, power, active, phase, sensor, elec-power, ac-elec | Active_Power_Sensor | 1 s |
| Generator_Power_kW_L3 | Puissance active phase L3 | kW | 0-2000 kW | generator, power, active, phase, sensor, elec-power, ac-elec | Active_Power_Sensor | 1 s |
| Generator_Power_kW_Total | Puissance active totale | kW | 0-2000 kW | generator, power, active, total, sensor, elec-power, ac-elec | Active_Power_Sensor | 1 s |
| Generator_Power_kVA_Total | Puissance apparente totale | kVA | 0-2500 kVA | generator, power, apparent, total, sensor, ac-elec | Apparent_Power_Sensor | 1 s |
| Generator_Power_kVAr_Total | Puissance réactive totale | kVAr | -1000 à +1000 kVAr | generator, power, reactive, total, sensor, ac-elec | Reactive_Power_Sensor | 1 s |
| Generator_Power_Factor_Avg | Facteur de puissance moyen | - | 0.0-1.0 | generator, pf, avg, sensor, ac-elec | Power_Factor_Sensor | 1 s |
| Generator_Load_Percent | Charge générateur | % | 0-100% | generator, load, sensor, ac-elec | Load_Sensor | 1 s |
| Generator_Energy_Total | Énergie totale produite | kWh | 0-999999 kWh | generator, energy, total, sensor, elec-energy, ac-elec | Energy_Sensor | 5 min |
| Generator_THD_Voltage | Distorsion harmonique tension | % | 0-25% | generator, voltage, thd, sensor, ac-elec | THD_Sensor | 5 s |
| Generator_THD_Current | Distorsion harmonique courant | % | 0-25% | generator, current, thd, sensor, ac-elec | THD_Sensor | 5 s |

### Mesures Moteur Diesel/Gaz

| Point | Description | Unité | Plage Typique | Haystack Tags | Brick Class | Fréquence |
|-------|-------------|-------|---------------|---------------|-------------|-----------|
| Engine_Speed_RPM | Vitesse moteur | RPM | 0-2000 RPM | generator, engine, speed, sensor | Speed_Sensor | 1 s |
| Engine_Oil_Pressure | Pression huile moteur | kPa / PSI | 0-700 kPa | generator, engine, oil, pressure, sensor | Pressure_Sensor | 1 s |
| Engine_Oil_Temperature | Température huile moteur | °C | -40 à 150°C | generator, engine, oil, temp, sensor | Temperature_Sensor | 5 s |
| Engine_Oil_Level | Niveau huile moteur | % | 0-100% | generator, engine, oil, level, sensor | Level_Sensor | 1 min |
| Engine_Coolant_Temperature | Température liquide refroidissement | °C | -40 à 120°C | generator, engine, coolant, temp, sensor | Temperature_Sensor | 5 s |
| Engine_Coolant_Level | Niveau liquide refroidissement | % | 0-100% | generator, engine, coolant, level, sensor | Level_Sensor | 1 min |
| Engine_Exhaust_Temperature | Température échappement (EGT) | °C | 0-800°C | generator, engine, exhaust, temp, sensor | Temperature_Sensor | 5 s |
| Engine_Intake_Air_Temperature | Température air admission | °C | -40 à 80°C | generator, engine, intake, air, temp, sensor | Temperature_Sensor | 5 s |
| Engine_Turbo_Boost_Pressure | Pression turbocompresseur | kPa | 0-300 kPa | generator, engine, turbo, pressure, sensor | Pressure_Sensor | 1 s |
| Engine_Fuel_Level | Niveau carburant réservoir | % / L | 0-100% | generator, engine, fuel, level, sensor | Fuel_Level_Sensor | 1 min |
| Engine_Fuel_Pressure | Pression carburant | kPa | 0-600 kPa | generator, engine, fuel, pressure, sensor | Pressure_Sensor | 5 s |
| Engine_Fuel_Rate | Débit carburant instantané | L/h | 0-500 L/h | generator, engine, fuel, flow, sensor | Flow_Sensor | 5 s |
| Engine_Runtime_Hours | Heures de fonctionnement moteur | h | 0-999999 h | generator, engine, run, sensor | Run_Time_Sensor | 1 min |
| Engine_Start_Count | Nombre de démarrages | - | 0-999999 | generator, engine, starts, sensor | Counter_Sensor | event |
| Engine_Alternator_Temperature | Température alternateur | °C | -40 à 150°C | generator, alternator, temp, sensor | Temperature_Sensor | 5 s |

### Mesures Batterie et Système Électrique

| Point | Description | Unité | Plage Typique | Haystack Tags | Brick Class | Fréquence |
|-------|-------------|-------|---------------|---------------|-------------|-----------|
| Battery_Voltage | Tension batterie démarrage | Vdc | 0-30 Vdc | generator, battery, voltage, sensor, dc-elec, elec-volt | DC_Voltage_Sensor | 10 s |
| Battery_Charge_Current | Courant charge batterie | A | 0-50 A | generator, battery, charging, current, sensor, dc-elec, elec-current | DC_Current_Sensor | 10 s |
| Block_Heater_Temperature | Température préchauffeur moteur | °C | 0-120°C | generator, heater, temp, sensor | Temperature_Sensor | 1 min |
| Block_Heater_Status | État préchauffeur moteur | - | ON/OFF | generator, heater, sensor | Enable_Status | 1 min |

### Mesures Réseau Principal (Mains)

| Point | Description | Unité | Plage Typique | Haystack Tags | Brick Class | Fréquence |
|-------|-------------|-------|---------------|---------------|-------------|-----------|
| Mains_Voltage_Avg | Tension réseau principal moyenne | V | 0-480 V | mains, voltage, avg, sensor, elec-volt, ac-elec | AC_Voltage_Sensor | 1 s |
| Mains_Frequency | Fréquence réseau principal | Hz | 47-63 Hz | mains, freq, sensor, ac-elec | AC_Frequency_Sensor | 1 s |
| Mains_Available | Réseau principal disponible | - | Available/Unavailable | mains, available, sensor | Status_Sensor | 1 s |

## Points de Commande (Actionneurs/Consignes)

| Point | Description | Unité | Plage | Haystack Tags | Brick Class |
|-------|-------------|-------|-------|---------------|-------------|
| Generator_Start_Command | Commande démarrage générateur | - | START/STOP | generator, start, cmd | Start_Stop_Command |
| Generator_Stop_Command | Commande arrêt générateur | - | STOP | generator, stop, cmd | Start_Stop_Command |
| Generator_Mode_Command | Sélection mode fonctionnement | - | OFF/MANUAL/AUTO/TEST | generator, mode, cmd | Mode_Command |
| Generator_Test_Command | Commande test périodique | - | START_TEST | generator, test, cmd | Enable_Command |
| Generator_Reset_Command | Réinitialisation alarmes | - | RESET | generator, reset, cmd | Reset_Command |
| Generator_Load_Setpoint | Consigne charge générateur | kW | 0-rated kW | generator, load, sp | Power_Setpoint |
| ATS_Transfer_Command | Commande transfert ATS | - | MAINS/GENERATOR | ats, transfer, cmd | Mode_Command |
| Block_Heater_Enable | Activation préchauffeur | - | ENABLE/DISABLE | generator, heater, cmd | Enable_Command |

## Points d'État

### États Généraux

| Point | Description | Valeurs | Haystack Tags | Brick Class |
|-------|-------------|---------|---------------|-------------|
| Generator_Run_Status | État fonctionnement générateur | STOPPED/STARTING/RUNNING/STOPPING/COOLDOWN | generator, run, sensor | Run_Status |
| Generator_Ready_Status | Générateur prêt à démarrer | READY/NOT_READY | generator, ready, sensor | Status_Sensor |
| Generator_Operating_Mode | Mode opératoire actif | OFF/MANUAL/AUTO/TEST | generator, mode, sensor | Mode_Status |
| Generator_On_Load | Générateur sous charge | ON_LOAD/OFF_LOAD | generator, load, sensor | Status_Sensor |
| ATS_Position | Position contacteur ATS | MAINS/GENERATOR/NEUTRAL | ats, position, sensor | Position_Sensor |
| ATS_Ready_Transfer | ATS prêt à transférer | READY/NOT_READY | ats, ready, sensor | Status_Sensor |

### Alarmes et Défauts Critiques

| Point | Description | Valeurs | Haystack Tags | Brick Class |
|-------|-------------|---------|---------------|-------------|
| Alarm_Emergency_Stop | Arrêt d'urgence activé | ACTIVE/INACTIVE | generator, alarm, estop, sensor | Alarm_Status |
| Alarm_Overspeed | Survitesse moteur | ACTIVE/INACTIVE | generator, alarm, overspeed, sensor | Alarm_Status |
| Alarm_Low_Oil_Pressure | Pression huile basse | ACTIVE/INACTIVE | generator, alarm, oil, pressure, low, sensor | Alarm_Status |
| Alarm_High_Coolant_Temp | Température liquide haute | ACTIVE/INACTIVE | generator, alarm, coolant, temp, high, sensor | Alarm_Status |
| Alarm_Overcurrent | Surintensité générateur | ACTIVE/INACTIVE | generator, alarm, overcurrent, sensor | Alarm_Status |
| Alarm_Over_Voltage | Surtension générateur | ACTIVE/INACTIVE | generator, alarm, voltage, high, sensor | Alarm_Status |
| Alarm_Under_Voltage | Sous-tension générateur | ACTIVE/INACTIVE | generator, alarm, voltage, low, sensor | Alarm_Status |
| Alarm_Over_Frequency | Surfréquence | ACTIVE/INACTIVE | generator, alarm, freq, high, sensor | Alarm_Status |
| Alarm_Under_Frequency | Sous-fréquence | ACTIVE/INACTIVE | generator, alarm, freq, low, sensor | Alarm_Status |
| Alarm_Fail_To_Start | Échec démarrage | ACTIVE/INACTIVE | generator, alarm, start, fail, sensor | Alarm_Status |
| Alarm_Low_Fuel_Level | Niveau carburant bas | ACTIVE/INACTIVE | generator, alarm, fuel, level, low, sensor | Alarm_Status |
| Alarm_Low_Battery_Voltage | Tension batterie basse | ACTIVE/INACTIVE | generator, alarm, battery, voltage, low, sensor | Alarm_Status |
| Alarm_High_Exhaust_Temp | Température échappement haute | ACTIVE/INACTIVE | generator, alarm, exhaust, temp, high, sensor | Alarm_Status |
| Alarm_Mains_Failure | Défaillance réseau principal | ACTIVE/INACTIVE | generator, alarm, mains, fail, sensor | Alarm_Status |

## Mappings Protocoles

### BACnet

| Point | Object Type | Object Instance | Units | R/W | Priority Array |
|-------|-------------|-----------------|-------|-----|----------------|
| Generator_Voltage_Avg | Analog Input | 0 | volts-AC | R | - |
| Generator_Current_Avg | Analog Input | 1 | amperes-AC | R | - |
| Generator_Frequency | Analog Input | 2 | hertz | R | - |
| Generator_Power_kW_Total | Analog Input | 3 | kilowatts | R | - |
| Generator_Power_kVA_Total | Analog Input | 4 | kilovolt-amperes | R | - |
| Generator_Power_Factor_Avg | Analog Input | 5 | no-units | R | - |
| Generator_Load_Percent | Analog Input | 6 | percent | R | - |
| Generator_Energy_Total | Analog Input | 7 | kilowatt-hours | R | - |
| Engine_Speed_RPM | Analog Input | 10 | revolutions-per-minute | R | - |
| Engine_Oil_Pressure | Analog Input | 11 | kilopascals | R | - |
| Engine_Oil_Temperature | Analog Input | 12 | degrees-celsius | R | - |
| Engine_Coolant_Temperature | Analog Input | 13 | degrees-celsius | R | - |
| Engine_Fuel_Level | Analog Input | 14 | percent | R | - |
| Engine_Runtime_Hours | Analog Input | 15 | hours | R | - |
| Battery_Voltage | Analog Input | 16 | volts-DC | R | - |
| Mains_Voltage_Avg | Analog Input | 17 | volts-AC | R | - |
| Mains_Frequency | Analog Input | 18 | hertz | R | - |
| Generator_Run_Status | Multi-state Input | 100 | - | R | - |
| Generator_Operating_Mode | Multi-state Input | 101 | - | R | - |
| ATS_Position | Multi-state Input | 102 | - | R | - |
| Alarm_Emergency_Stop | Binary Input | 200 | - | R | - |
| Alarm_Overspeed | Binary Input | 201 | - | R | - |
| Alarm_Low_Oil_Pressure | Binary Input | 202 | - | R | - |
| Alarm_High_Coolant_Temp | Binary Input | 203 | - | R | - |
| Alarm_Mains_Failure | Binary Input | 204 | - | R | - |
| Generator_Start_Command | Binary Output | 300 | - | R/W | Yes (1-16) |
| Generator_Stop_Command | Binary Output | 301 | - | R/W | Yes (1-16) |
| Generator_Mode_Command | Multi-state Output | 400 | - | R/W | Yes (1-16) |
| Generator_Load_Setpoint | Analog Output | 500 | kilowatts | R/W | Yes (1-16) |

### Modbus

| Point | Type | Registre | Data Type | Unités | R/W |
|-------|------|----------|-----------|--------|-----|
| Generator_Voltage_L1_N | Input Register | 40001 | UINT16 (x0.1) | V | R |
| Generator_Voltage_L2_N | Input Register | 40002 | UINT16 (x0.1) | V | R |
| Generator_Voltage_L3_N | Input Register | 40003 | UINT16 (x0.1) | V | R |
| Generator_Current_L1 | Input Register | 40011 | UINT16 (x0.1) | A | R |
| Generator_Current_L2 | Input Register | 40012 | UINT16 (x0.1) | A | R |
| Generator_Current_L3 | Input Register | 40013 | UINT16 (x0.1) | A | R |
| Generator_Frequency | Input Register | 40021 | UINT16 (x0.01) | Hz | R |
| Generator_Power_kW_Total | Input Register | 40031 | UINT32 | kW | R |
| Generator_Power_kVA_Total | Input Register | 40033 | UINT32 | kVA | R |
| Generator_Power_Factor_Avg | Input Register | 40041 | INT16 (x0.01) | - | R |
| Generator_Load_Percent | Input Register | 40051 | UINT16 | % | R |
| Generator_Energy_Total | Input Register | 40061 | UINT32 | kWh | R |
| Engine_Speed_RPM | Input Register | 40101 | UINT16 | RPM | R |
| Engine_Oil_Pressure | Input Register | 40111 | UINT16 (x0.1) | kPa | R |
| Engine_Oil_Temperature | Input Register | 40112 | INT16 | °C | R |
| Engine_Coolant_Temperature | Input Register | 40121 | INT16 | °C | R |
| Engine_Fuel_Level | Input Register | 40131 | UINT16 | % | R |
| Engine_Runtime_Hours | Input Register | 40141 | UINT32 | h | R |
| Battery_Voltage | Input Register | 40151 | UINT16 (x0.1) | Vdc | R |
| Mains_Voltage_Avg | Input Register | 40201 | UINT16 (x0.1) | V | R |
| Mains_Frequency | Input Register | 40211 | UINT16 (x0.01) | Hz | R |
| Generator_Run_Status | Input Register | 40301 | UINT16 (enum) | - | R |
| Generator_Operating_Mode | Input Register | 40311 | UINT16 (enum) | - | R |
| Alarm_Status_Word_1 | Input Register | 40401 | UINT16 (bitmap) | - | R |
| Alarm_Status_Word_2 | Input Register | 40402 | UINT16 (bitmap) | - | R |
| Generator_Start_Command | Coil | 00001 | BOOL | - | R/W |
| Generator_Stop_Command | Coil | 00002 | BOOL | - | R/W |
| Generator_Mode_Command | Holding Register | 40001 | UINT16 (enum) | - | R/W |
| Generator_Load_Setpoint | Holding Register | 40011 | UINT16 | kW | R/W |

## Sources

1. https://www.ccontrols.com/support/dp/ManualEMCP4.pdf - Caterpillar EMCP 4 Application and Installation Guide
2. https://csdieselgenerators.com/Images/Generators/2852/Cummins-PowerCommand-1.1-1.2-2.2-2.3-3.3-modbus-register-mapping.pdf - Cummins PowerCommand Modbus Register Mapping
3. https://resources.kohler.com/power/kohler/industrial/pdf/Controller_Brochure.pdf - Kohler Generator Controllers Brochure
4. http://cdn.senquip.com/wp-content/uploads/2024/04/18104724/APN0029-Rev-1.0-Modbus-Integration-With-Deep-Sea-Engine-Controller.pdf - Modbus Integration with Deep Sea Controller
5. https://www.genpowerusa.com/content/files/DEEP-SEA-7320-MANUAL.pdf - DSE 7200/7300 Series Operators Manual
6. https://generatorsource.com/safety-maintenance/nfpa-110-generator-requirements/ - NFPA 110 Standard Overview on Generator Requirements
7. https://www.energyly.com/diesel-generator-monitoring.html - Diesel Generator Monitoring System
8. https://www.ny-engineers.com/blog/diesel-genset-specifications-kw-kva-and-power-factor - Diesel Genset Specification: kW, kVA & Power Factor
9. https://www.shentongroup.co.uk/products/generators-and-ups/ats-panels/ - ATS Panels
10. https://generatorhelponline.com/generator-alarms/ - What Generator Alarms Mean