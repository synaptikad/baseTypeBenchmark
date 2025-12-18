# Points de Transformer (Transformateur MT/BT)

## Synthèse
- **Total points mesure** : 48
- **Total points commande** : 6
- **Total points état** : 18

## Points de Mesure (Capteurs)

| Point | Description | Unité | Plage Typique | Haystack Tags | Brick Class | Fréquence |
|-------|-------------|-------|---------------|---------------|-------------|-----------|
| **Températures** |
| Oil_Top_Temp | Température huile en haut de cuve | °C | 0-120°C | oil, temp, sensor, point | Oil_Temperature_Sensor | 1 min |
| Oil_Bottom_Temp | Température huile en bas de cuve | °C | 0-110°C | oil, temp, sensor, point | Oil_Temperature_Sensor | 1 min |
| Winding_Temp_HV | Température enroulement primaire (HV) | °C | 20-140°C | discharge, temp, sensor, point | Discharge_Air_Temperature_Sensor | 1 min |
| Winding_Temp_LV | Température enroulement secondaire (LV) | °C | 20-140°C | discharge, temp, sensor, point | Discharge_Air_Temperature_Sensor | 1 min |
| Hotspot_Temp | Température point chaud (hot spot) | °C | 30-160°C | hottest, temp, sensor, point | Temperature_Sensor | 30 sec |
| Ambient_Temp | Température ambiante local transformateur | °C | -20 à +50°C | zone, air, temp, sensor, point | Air_Temperature_Sensor | 5 min |
| Core_Temp | Température du noyau magnétique | °C | 20-130°C | temp, sensor, point | Temperature_Sensor | 1 min |
| **Mesures Électriques Primaire (MT)** |
| HV_Voltage_L1 | Tension primaire phase L1 | kV | 0-25 kV | phase:"A", ac, volt, sensor, point, elec | Voltage_Sensor | 1 sec |
| HV_Voltage_L2 | Tension primaire phase L2 | kV | 0-25 kV | phase:"B", ac, volt, sensor, point, elec | Voltage_Sensor | 1 sec |
| HV_Voltage_L3 | Tension primaire phase L3 | kV | 0-25 kV | phase:"C", ac, volt, sensor, point, elec | Voltage_Sensor | 1 sec |
| HV_Current_L1 | Courant primaire phase L1 | A | 0-100 A | phase:"A", ac, current, sensor, point, elec | Current_Sensor | 1 sec |
| HV_Current_L2 | Courant primaire phase L2 | A | 0-100 A | phase:"B", ac, current, sensor, point, elec | Current_Sensor | 1 sec |
| HV_Current_L3 | Courant primaire phase L3 | A | 0-100 A | phase:"C", ac, current, sensor, point, elec | Current_Sensor | 1 sec |
| HV_Active_Power | Puissance active primaire totale | kW | 0-2500 kW | total, active, ac, power, sensor, point, elec | Active_Power_Sensor | 1 sec |
| HV_Reactive_Power | Puissance réactive primaire | kVAr | -1000 à +1000 kVAr | total, reactive, ac, power, sensor, point, elec | Reactive_Power_Sensor | 1 sec |
| HV_Apparent_Power | Puissance apparente primaire | kVA | 0-2500 kVA | total, apparent, ac, power, sensor, point, elec | Apparent_Power_Sensor | 1 sec |
| HV_Power_Factor | Facteur de puissance primaire | - | 0-1 | total, pf, sensor, point, elec | Power_Factor_Sensor | 1 sec |
| HV_Frequency | Fréquence réseau primaire | Hz | 49-51 Hz | ac, freq, sensor, point, elec | Frequency_Sensor | 1 sec |
| **Mesures Électriques Secondaire (BT)** |
| LV_Voltage_L1 | Tension secondaire phase L1 | V | 0-450 V | phase:"A", ac, volt, sensor, point, elec | Voltage_Sensor | 1 sec |
| LV_Voltage_L2 | Tension secondaire phase L2 | V | 0-450 V | phase:"B", ac, volt, sensor, point, elec | Voltage_Sensor | 1 sec |
| LV_Voltage_L3 | Tension secondaire phase L3 | V | 0-450 V | phase:"C", ac, volt, sensor, point, elec | Voltage_Sensor | 1 sec |
| LV_Current_L1 | Courant secondaire phase L1 | A | 0-3000 A | phase:"A", ac, current, sensor, point, elec | Current_Sensor | 1 sec |
| LV_Current_L2 | Courant secondaire phase L2 | A | 0-3000 A | phase:"B", ac, current, sensor, point, elec | Current_Sensor | 1 sec |
| LV_Current_L3 | Courant secondaire phase L3 | A | 0-3000 A | phase:"C", ac, current, sensor, point, elec | Current_Sensor | 1 sec |
| LV_Neutral_Current | Courant neutre secondaire | A | 0-1000 A | neutral, ac, current, sensor, point, elec | Current_Sensor | 1 sec |
| LV_Active_Power | Puissance active secondaire totale | kW | 0-2500 kW | total, active, ac, power, sensor, point, elec | Active_Power_Sensor | 1 sec |
| LV_Reactive_Power | Puissance réactive secondaire | kVAr | -1000 à +1000 kVAr | total, reactive, ac, power, sensor, point, elec | Reactive_Power_Sensor | 1 sec |
| LV_Apparent_Power | Puissance apparente secondaire | kVA | 0-2500 kVA | total, apparent, ac, power, sensor, point, elec | Apparent_Power_Sensor | 1 sec |
| LV_Power_Factor | Facteur de puissance secondaire | - | 0-1 | total, pf, sensor, point, elec | Power_Factor_Sensor | 1 sec |
| LV_THD_Voltage | Distorsion harmonique tension | % | 0-20% | total, thd, ac, volt, sensor, point, elec | Voltage_Sensor | 5 sec |
| LV_THD_Current | Distorsion harmonique courant | % | 0-50% | total, thd, ac, current, sensor, point, elec | Current_Sensor | 5 sec |
| **Énergie** |
| Active_Energy_Import | Énergie active importée cumulée | kWh | 0-999999999 | import, active, energy, sensor, point, elec | Energy_Sensor | 15 min |
| Active_Energy_Export | Énergie active exportée cumulée | kWh | 0-999999999 | export, active, energy, sensor, point, elec | Energy_Sensor | 15 min |
| Reactive_Energy_Import | Énergie réactive importée | kVArh | 0-999999999 | import, reactive, energy, sensor, point, elec | Energy_Sensor | 15 min |
| **Huile et Isolation** |
| Oil_Level | Niveau d'huile dans conservateur | % | 0-100% | oil, level, sensor, point | Level_Sensor | 5 min |
| Oil_Moisture | Humidité relative dans l'huile | %RH | 0-100% | oil, humidity, sensor, point | Humidity_Sensor | 1 h |
| Oil_Moisture_PPM | Humidité absolue dans l'huile | ppm | 0-100 ppm | oil, moisture, sensor, point | Sensor | 1 h |
| Oil_Pressure | Pression de l'huile | bar | 0-2 bar | oil, pressure, sensor, point | Pressure_Sensor | 5 min |
| **DGA - Gaz dissous (Dissolved Gas Analysis)** |
| DGA_H2 | Concentration hydrogène | ppm | 0-1000 ppm | gas, sensor, point | Sensor | 1 h |
| DGA_CH4 | Concentration méthane | ppm | 0-500 ppm | gas, sensor, point | Sensor | 1 h |
| DGA_C2H6 | Concentration éthane | ppm | 0-200 ppm | gas, sensor, point | Sensor | 1 h |
| DGA_C2H4 | Concentration éthylène | ppm | 0-500 ppm | gas, sensor, point | Sensor | 1 h |
| DGA_C2H2 | Concentration acétylène | ppm | 0-100 ppm | gas, sensor, point | Sensor | 1 h |
| DGA_CO | Concentration monoxyde de carbone | ppm | 0-1000 ppm | gas, co, sensor, point | CO_Sensor | 1 h |
| DGA_CO2 | Concentration dioxyde de carbone | ppm | 0-5000 ppm | gas, co2, sensor, point | CO2_Sensor | 1 h |
| **Bushing (Traversées)** |
| Bushing_Capacitance_HV | Capacité traversée HV | pF | 100-1000 pF | sensor, point | Sensor | 1 jour |
| Bushing_Tan_Delta_HV | Facteur de dissipation traversée HV | % | 0-2% | sensor, point | Sensor | 1 jour |

## Points de Commande (Actionneurs/Consignes)

| Point | Description | Unité | Plage | Haystack Tags | Brick Class |
|-------|-------------|-------|-------|---------------|-------------|
| Cooling_Stage_1_Cmd | Commande ventilateurs étage 1 | - | ON/OFF | cooling, fan, cmd, point | Fan_Start_Stop_Command |
| Cooling_Stage_2_Cmd | Commande ventilateurs étage 2 | - | ON/OFF | cooling, fan, cmd, point | Fan_Start_Stop_Command |
| Oil_Pump_Cmd | Commande pompe circulation huile | - | ON/OFF | oil, pump, cmd, point | Pump_Start_Stop_Command |
| Tap_Position_Setpoint | Consigne position prise OLTC | - | 1-33 | sp, point | Setpoint |
| Transformer_Enable_Cmd | Autorisation mise en service | - | ON/OFF | enable, cmd, point | Enable_Command |
| Remote_Control_Enable | Activation contrôle à distance | - | ON/OFF | remote, enable, cmd, point | Enable_Command |

## Points d'État

| Point | Description | Valeurs | Haystack Tags | Brick Class |
|-------|-------------|---------|---------------|-------------|
| **États Généraux** |
| Transformer_Status | État général transformateur | 0=Arrêt, 1=Fonctionnement, 2=Défaut | run, sensor, point | Run_Status |
| HV_Breaker_Status | État disjoncteur primaire | 0=Ouvert, 1=Fermé | breaker, sensor, point | Breaker_Status |
| LV_Breaker_Status | État disjoncteur secondaire | 0=Ouvert, 1=Fermé | breaker, sensor, point | Breaker_Status |
| Tap_Position | Position prise en cours OLTC | 1-33 (ou ±16) | sensor, point | Sensor |
| **Refroidissement** |
| Cooling_Stage_1_Status | État ventilateurs étage 1 | 0=Arrêt, 1=Marche | cooling, fan, sensor, point | Fan_Status |
| Cooling_Stage_2_Status | État ventilateurs étage 2 | 0=Arrêt, 1=Marche | cooling, fan, sensor, point | Fan_Status |
| Oil_Pump_Status | État pompe circulation huile | 0=Arrêt, 1=Marche | oil, pump, sensor, point | Pump_Status |
| **Alarmes Critiques** |
| Buchholz_Alarm | Alarme Buchholz (accumulation gaz) | 0=Normal, 1=Alarme | gas, alarm, point | Alarm |
| Buchholz_Trip | Déclenchement Buchholz (fort gaz) | 0=Normal, 1=Déclenché | gas, trip, alarm, point | Alarm |
| Sudden_Pressure_Alarm | Alarme pression soudaine | 0=Normal, 1=Alarme | pressure, alarm, point | Alarm |
| Oil_Temp_Alarm | Alarme température huile | 0=Normal, 1=Alarme | oil, temp, alarm, point | Alarm |
| Winding_Temp_Alarm | Alarme température enroulements | 0=Normal, 1=Alarme | discharge, temp, alarm, point | Alarm |
| Overload_Alarm | Alarme surcharge | 0=Normal, 1=Alarme | overload, alarm, point | Alarm |
| Oil_Level_Low_Alarm | Alarme niveau huile bas | 0=Normal, 1=Alarme | oil, level, alarm, point | Alarm |
| **Protections Électriques** |
| Differential_Protection | Protection différentielle activée | 0=Normal, 1=Déclenché | protection, alarm, point | Alarm |
| Earth_Fault_Protection | Protection défaut terre | 0=Normal, 1=Déclenché | ground, fault, alarm, point | Alarm |
| Overcurrent_Protection_HV | Protection surintensité primaire | 0=Normal, 1=Déclenché | current, protection, alarm, point | Alarm |
| Undervoltage_Protection | Protection sous-tension | 0=Normal, 1=Déclenché | volt, protection, alarm, point | Alarm |

## Mappings Protocoles

### BACnet

| Point | Object Type | Object Instance | Units | R/W | Description |
|-------|------------|-----------------|-------|-----|-------------|
| Oil_Top_Temp | Analog Input | 1 | degrees-celsius | R | Température huile haute |
| Hotspot_Temp | Analog Input | 2 | degrees-celsius | R | Température point chaud |
| Winding_Temp_HV | Analog Input | 3 | degrees-celsius | R | Température enroulement HV |
| Winding_Temp_LV | Analog Input | 4 | degrees-celsius | R | Température enroulement LV |
| Oil_Level | Analog Input | 5 | percent | R | Niveau d'huile |
| HV_Voltage_L1 | Analog Input | 10 | kilovolts | R | Tension primaire L1 |
| HV_Voltage_L2 | Analog Input | 11 | kilovolts | R | Tension primaire L2 |
| HV_Voltage_L3 | Analog Input | 12 | kilovolts | R | Tension primaire L3 |
| HV_Current_L1 | Analog Input | 13 | amperes | R | Courant primaire L1 |
| HV_Current_L2 | Analog Input | 14 | amperes | R | Courant primaire L2 |
| HV_Current_L3 | Analog Input | 15 | amperes | R | Courant primaire L3 |
| LV_Voltage_L1 | Analog Input | 20 | volts | R | Tension secondaire L1 |
| LV_Voltage_L2 | Analog Input | 21 | volts | R | Tension secondaire L2 |
| LV_Voltage_L3 | Analog Input | 22 | volts | R | Tension secondaire L3 |
| LV_Current_L1 | Analog Input | 23 | amperes | R | Courant secondaire L1 |
| LV_Current_L2 | Analog Input | 24 | amperes | R | Courant secondaire L2 |
| LV_Current_L3 | Analog Input | 25 | amperes | R | Courant secondaire L3 |
| LV_Neutral_Current | Analog Input | 26 | amperes | R | Courant neutre |
| HV_Active_Power | Analog Input | 30 | kilowatts | R | Puissance active HV |
| HV_Reactive_Power | Analog Input | 31 | kilovars-reactive | R | Puissance réactive HV |
| HV_Power_Factor | Analog Input | 32 | no-units | R | Facteur de puissance HV |
| LV_Active_Power | Analog Input | 40 | kilowatts | R | Puissance active LV |
| LV_Reactive_Power | Analog Input | 41 | kilovars-reactive | R | Puissance réactive LV |
| LV_Power_Factor | Analog Input | 42 | no-units | R | Facteur de puissance LV |
| Active_Energy_Import | Accumulator | 50 | kilowatt-hours | R | Énergie active importée |
| DGA_H2 | Analog Input | 60 | parts-per-million | R | Hydrogène dissous |
| DGA_CH4 | Analog Input | 61 | parts-per-million | R | Méthane dissous |
| DGA_C2H2 | Analog Input | 62 | parts-per-million | R | Acétylène dissous |
| DGA_CO | Analog Input | 63 | parts-per-million | R | Monoxyde de carbone |
| Transformer_Status | Multi-state Input | 100 | no-units | R | État général (0=Arrêt, 1=Marche, 2=Défaut) |
| Tap_Position | Multi-state Input | 101 | no-units | R | Position changeur de prises |
| Buchholz_Alarm | Binary Input | 200 | no-units | R | Alarme Buchholz |
| Sudden_Pressure_Alarm | Binary Input | 201 | no-units | R | Alarme pression soudaine |
| Oil_Temp_Alarm | Binary Input | 202 | no-units | R | Alarme température huile |
| Winding_Temp_Alarm | Binary Input | 203 | no-units | R | Alarme température enroulements |
| Differential_Protection | Binary Input | 204 | no-units | R | Protection différentielle |
| Earth_Fault_Protection | Binary Input | 205 | no-units | R | Défaut terre |
| Cooling_Stage_1_Cmd | Binary Output | 300 | no-units | R/W | Commande ventilateurs 1 |
| Cooling_Stage_2_Cmd | Binary Output | 301 | no-units | R/W | Commande ventilateurs 2 |
| Oil_Pump_Cmd | Binary Output | 302 | no-units | R/W | Commande pompe huile |
| Tap_Position_Setpoint | Analog Output | 310 | no-units | R/W | Consigne position prise |

### Modbus

| Point | Type | Registre | Data Type | Unités | R/W | Description |
|-------|------|----------|-----------|--------|-----|-------------|
| Oil_Top_Temp | Input Reg | 30001 | INT16 (x10) | °C | R | Température huile haute (÷10) |
| Hotspot_Temp | Input Reg | 30002 | INT16 (x10) | °C | R | Température point chaud (÷10) |
| Winding_Temp_HV | Input Reg | 30003 | INT16 (x10) | °C | R | Température enroulement HV (÷10) |
| Winding_Temp_LV | Input Reg | 30004 | INT16 (x10) | °C | R | Température enroulement LV (÷10) |
| Oil_Level | Input Reg | 30005 | UINT16 | % | R | Niveau d'huile |
| Oil_Moisture | Input Reg | 30006 | UINT16 | %RH | R | Humidité huile |
| HV_Voltage_L1 | Input Reg | 30010 | UINT16 (x10) | V | R | Tension HV L1 (÷10) |
| HV_Voltage_L2 | Input Reg | 30011 | UINT16 (x10) | V | R | Tension HV L2 (÷10) |
| HV_Voltage_L3 | Input Reg | 30012 | UINT16 (x10) | V | R | Tension HV L3 (÷10) |
| HV_Current_L1 | Input Reg | 30013 | UINT16 (x10) | A | R | Courant HV L1 (÷10) |
| HV_Current_L2 | Input Reg | 30014 | UINT16 (x10) | A | R | Courant HV L2 (÷10) |
| HV_Current_L3 | Input Reg | 30015 | UINT16 (x10) | A | R | Courant HV L3 (÷10) |
| LV_Voltage_L1 | Input Reg | 30020 | UINT16 (x10) | V | R | Tension LV L1 (÷10) |
| LV_Voltage_L2 | Input Reg | 30021 | UINT16 (x10) | V | R | Tension LV L2 (÷10) |
| LV_Voltage_L3 | Input Reg | 30022 | UINT16 (x10) | V | R | Tension LV L3 (÷10) |
| LV_Current_L1 | Input Reg | 30023 | UINT16 (x100) | A | R | Courant LV L1 (÷100) |
| LV_Current_L2 | Input Reg | 30024 | UINT16 (x100) | A | R | Courant LV L2 (÷100) |
| LV_Current_L3 | Input Reg | 30025 | UINT16 (x100) | A | R | Courant LV L3 (÷100) |
| LV_Neutral_Current | Input Reg | 30026 | UINT16 (x100) | A | R | Courant neutre (÷100) |
| HV_Active_Power | Input Reg | 30030-30031 | INT32 | W | R | Puissance active HV (32 bits) |
| HV_Reactive_Power | Input Reg | 30032-30033 | INT32 | VAr | R | Puissance réactive HV (32 bits) |
| HV_Power_Factor | Input Reg | 30034 | INT16 (x1000) | - | R | Facteur puissance HV (÷1000) |
| LV_Active_Power | Input Reg | 30040-30041 | INT32 | W | R | Puissance active LV (32 bits) |
| LV_Reactive_Power | Input Reg | 30042-30043 | INT32 | VAr | R | Puissance réactive LV (32 bits) |
| LV_Power_Factor | Input Reg | 30044 | INT16 (x1000) | - | R | Facteur puissance LV (÷1000) |
| LV_THD_Voltage | Input Reg | 30045 | UINT16 (x10) | % | R | THD tension (÷10) |
| LV_THD_Current | Input Reg | 30046 | UINT16 (x10) | % | R | THD courant (÷10) |
| Active_Energy_Import | Input Reg | 30050-30051 | UINT32 | kWh | R | Énergie active importée (32 bits) |
| Reactive_Energy_Import | Input Reg | 30052-30053 | UINT32 | kVArh | R | Énergie réactive importée (32 bits) |
| DGA_H2 | Input Reg | 30060 | UINT16 | ppm | R | Hydrogène dissous |
| DGA_CH4 | Input Reg | 30061 | UINT16 | ppm | R | Méthane dissous |
| DGA_C2H2 | Input Reg | 30062 | UINT16 | ppm | R | Acétylène dissous |
| DGA_CO | Input Reg | 30063 | UINT16 | ppm | R | Monoxyde de carbone |
| DGA_CO2 | Input Reg | 30064 | UINT16 | ppm | R | Dioxyde de carbone |
| Tap_Position | Input Reg | 30100 | UINT16 | - | R | Position changeur de prises |
| Transformer_Status | Input Reg | 30101 | UINT16 | - | R | État général (0/1/2) |
| Buchholz_Alarm | Coil | 00001 | BOOL | - | R | Alarme Buchholz |
| Sudden_Pressure_Alarm | Coil | 00002 | BOOL | - | R | Alarme pression soudaine |
| Oil_Temp_Alarm | Coil | 00003 | BOOL | - | R | Alarme température huile |
| Winding_Temp_Alarm | Coil | 00004 | BOOL | - | R | Alarme température enroulements |
| Overload_Alarm | Coil | 00005 | BOOL | - | R | Alarme surcharge |
| Differential_Protection | Coil | 00006 | BOOL | - | R | Protection différentielle |
| Earth_Fault_Protection | Coil | 00007 | BOOL | - | R | Défaut terre |
| Cooling_Stage_1_Status | Coil | 00008 | BOOL | - | R | État ventilateurs 1 |
| Cooling_Stage_2_Status | Coil | 00009 | BOOL | - | R | État ventilateurs 2 |
| Oil_Pump_Status | Coil | 00010 | BOOL | - | R | État pompe huile |
| Cooling_Stage_1_Cmd | Coil | 00101 | BOOL | - | R/W | Commande ventilateurs 1 |
| Cooling_Stage_2_Cmd | Coil | 00102 | BOOL | - | R/W | Commande ventilateurs 2 |
| Oil_Pump_Cmd | Coil | 00103 | BOOL | - | R/W | Commande pompe huile |
| Tap_Position_Setpoint | Holding Reg | 40001 | UINT16 | - | R/W | Consigne position prise OLTC |

### IEC 61850 (Logical Nodes)

| Point | Logical Node | Data Object | CDC | Description |
|-------|--------------|-------------|-----|-------------|
| HV_Voltage_L1 | MMXU1 | PhV.phsA | MV | Tension phase A primaire |
| HV_Current_L1 | MMXU1 | A.phsA | MV | Courant phase A primaire |
| HV_Active_Power | MMXU1 | TotW | MV | Puissance active totale primaire |
| LV_Voltage_L1 | MMXU2 | PhV.phsA | MV | Tension phase A secondaire |
| LV_Current_L1 | MMXU2 | A.phsA | MV | Courant phase A secondaire |
| Oil_Top_Temp | STMP1 | Tmp | MV | Température huile haute |
| Winding_Temp_HV | STMP2 | Tmp | MV | Température enroulement HV |
| Differential_Protection | PDIF1 | Op | ACT | Protection différentielle |
| Buchholz_Alarm | RBRF1 | Op | ACT | Relais Buchholz |
| Tap_Position | YLTC1 | TapPos | ING | Position changeur de prises |
| Cooling_Stage_1_Cmd | YFAN1 | OpCnt | INC | Contrôle ventilateurs étage 1 |

## Notes sur les Points

### Températures
- Les transformateurs immergés dans l'huile nécessitent une surveillance continue des températures d'huile et d'enroulements
- Le point chaud (hotspot) est critique : limite de déclenchement typique à 140-160°C
- Plage normale d'exploitation : 55-110°C pour les enroulements en charge normale

### DGA (Dissolved Gas Analysis)
- Surveillance en ligne des gaz dissous pour détection précoce de défauts internes
- H2 (hydrogène) : indicateur de décharges partielles
- C2H2 (acétylène) : indicateur d'arcs électriques
- CO/CO2 : indicateur de dégradation thermique de la cellulose
- Standards : IEC 60599, IEEE C57.104

### Protections
- Protection différentielle (87) : compare courants primaire/secondaire
- Protection Buchholz : détection accumulation gaz et flux huile anormal
- Protection pression soudaine (SPR) : détection arcs internes
- Protection terre restreinte (REF) : défauts terre enroulements

### Changeur de Prises (OLTC)
- Permet ajustement tension secondaire sous charge
- Positions typiques : ±8 à ±16 pas autour position neutre (soit 17-33 positions)
- Surveillance position essentielle pour optimisation tension et diagnostic

### Refroidissement
- Contrôle multi-étages : ventilateurs puis pompes selon température
- Seuils typiques : Stage 1 à 65°C, Stage 2 à 80°C, alarme à 95°C
- Modes : ONAN (naturel), ONAF (forcé air), OFAF (forcé air et huile)

### Qualité de Puissance
- THD tension/courant : surveillance harmoniques
- Facteur de puissance : optimisation facturation et performance
- Fréquence : indicateur stabilité réseau

## Sources

1. **Standards et Normes**
   - IEC 60076 - Power transformers specifications
   - IEC 60599:2015 - Mineral oil-filled electrical equipment - Dissolved gas analysis
   - IEC 60255 - Measuring relays and protection equipment
   - IEC 61850 - Communication networks and systems for power utility automation
   - IEEE C57.104-2019 - Guide for the Interpretation of Gases Generated in Mineral Oil-Immersed Transformers
   - ANSI C12.20 - Electricity meters standard

2. **Project Haystack**
   - https://project-haystack.org/doc/docHaystack/Meters
   - https://project-haystack.org/doc/docHaystack/ElecPanels
   - https://project-haystack.org/forum/topic/446 - Comprehensive Tags for Electrical Meters

3. **Brick Schema**
   - https://brickschema.org/ontology/1.1/classes/Electrical_Equipment/
   - https://brickschema.org/ontology/1.1/classes/Transformer/
   - https://docs.brickschema.org/brick/concepts.html

4. **Manufacturers & Technical Documentation**
   - https://www.dynamicratings.com/solutions/transformer-monitoring/ - Dynamic Ratings transformer monitoring solutions
   - https://www.vaisala.com/en/measurement/dissolved-gas-oil-dga-measurement - Vaisala DGA monitoring
   - https://www.vaisala.com/en/measurement/moisture-oil-measurement - Vaisala oil moisture sensors
   - https://www.reinhausen.com/moisture-sensors-for-power-transformers - Reinhausen moisture sensors
   - https://www.hitachienergy.com/products/sudden-pressure-relay-spr - Hitachi SPR devices
   - https://www.omicronenergy.com/en/solution/partial-discharge-monitoring/ - OMICRON PD monitoring
   - https://www.megger.com/en-us/type/partial-discharge-testing - Megger PD testing
   - https://www.qualitrolcorp.com/when-and-why-to-monitor-partial-discharge/ - Qualitrol PD monitoring

5. **Protection Relays**
   - https://selinc.com/api/download/2818/ - SEL-787 Transformer Protection Relay
   - https://www.eaton.com/etr-5000-technical-data - Eaton ETR-5000 Transformer Relay
   - https://site.ieee.org/fw-pes/files/2013/01/transfguide.pdf - IEEE Transformer Protection Guide

6. **BACnet & Protocols**
   - https://bacnet.org/wp-content/uploads/sites/4/2022/06/The-Language-of-BACnet-1.pdf - BACnet language guide
   - https://www.rtautomation.com/rtas-blog/bacnet-data-representation/ - BACnet data representation
   - https://www.emqx.com/en/blog/iec-61850-protocol - IEC 61850 protocol guide
   - https://www.sgrwin.com/goose-mms-and-sv-protocols/ - GOOSE, MMS, SV protocols

7. **Temperature & Cooling Monitoring**
   - https://www.fjinno.net/transformer-temperature-monitoring-and-cooling-control-essential-practices/ - Temperature monitoring practices
   - https://www.fjinno.net/what-is-transformer-temperature-monitoring/ - Temperature monitoring overview
   - https://advpowertech.com/transformer-monitoring-products/ttc-1000-transformer-monitor/ - TTC-1000 monitor
   - https://www.krenzvent.com/transformer-cooling-fan-control-systems - Cooling fan control

8. **OLTC & Tap Changer**
   - https://www.dynamicratings.com/solutions/transformer-monitoring/oltc-monitoring/ - OLTC monitoring
   - https://advpowertech.com/solutions/oltc-monitoring/ - OLTC monitoring systems

9. **Oil & Insulation Monitoring**
   - https://www.ruggedmonitoring.com/dissolved-gas-analysis-dga-in-transformers-online-vs-offline-methods/ - DGA methods comparison
   - https://kongter.com/products/kt-200-moisture-in-oil-transmitter/ - Moisture transmitter
   - https://globecore.com/products/instruments/toet-transformer-oil-express-tester/ - Oil moisture meter

10. **Bushing & Partial Discharge**
    - https://www.dynamicratings.com/solutions/transformer-monitoring/partial-discharge-monitoring/ - PD monitoring
    - https://transformers-magazine.com/condition-assessment-of-transformer-insulation-during-routine-partial-discharge-pd-tests/ - PD assessment

11. **Protection & Safety**
    - https://electrical-engineering-portal.com/substation-transformer-alarms - Transformer alarms guide
    - https://electrical-engineering-portal.com/troubleshooting-buchholz-relay - Buchholz relay troubleshooting
    - https://electrical-engineering-portal.com/sudden-pressure-relay-in-oil-filled-power-transformer - SPR guide
    - https://www.pes-psrc.org/kb/report/009.pdf - PSRC sudden pressure protection report
    - https://electrical-engineering-portal.com/ground-fault-protective-schemes - Ground fault schemes

12. **Differential Protection**
    - https://voltage-disturbance.com/power-engineering/transformer-differential-protection/ - Differential protection guide
    - https://www.electrical4u.com/differential-protection-of-transformer-differential-relays/ - Differential relays
    - https://control.com/textbook/electric-power-measurement-and-control/differential-87-current-protection/ - 87 protection

13. **Power Quality & Energy Metering**
    - https://www.accuenergy.com/products/acurev-2000-multi-channel-submeter/ - Multi-channel submeter
    - https://hoytmeter.com/acuviml-multifunction-meter.html - Multifunction power meter
    - https://www.eaton.com/power-quality-meters - Advanced power quality meters
    - https://dewesoft.com/applications/power-quality-analysis - Power quality analysis

14. **Technical Papers & Research**
    - https://www.mdpi.com/1424-8220/21/6/2223 - Comprehensive transformer monitoring techniques
    - https://www.sciencedirect.com/science/article/pii/S136403212100633X - Advances in DGA monitoring
    - https://pmc.ncbi.nlm.nih.gov/articles/PMC11699098/ - Fractal-based capacitive moisture sensor
    - https://www.nature.com/articles/s41598-025-92595-4 - Enhanced transformer protection scheme

15. **Market Reports & Industry Analysis**
    - https://www.marketsandmarkets.com/ResearchInsight/transformer-monitoring-system-market.asp - Market analysis
    - https://www.fortunebusinessinsights.com/industry-reports/transformer-monitoring-system-market-101357 - Industry forecast