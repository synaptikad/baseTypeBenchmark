# Points de UPS (Uninterruptible Power Supply)

## Synthèse
- **Total points mesure** : 56
- **Total points commande** : 8
- **Total points état** : 18
- **Total général** : 82 points

## Points de Mesure (Capteurs)

### Input (Entrée Électrique)

| Point | Description | Unité | Plage Typique | Haystack Tags | Brick Class | Fréquence |
|-------|-------------|-------|---------------|---------------|-------------|-----------|
| Input_Voltage_L1 | Tension entrée phase 1 | V AC | 0-480 | ac elec volt phase:"A" sensor input | Voltage_Sensor | 1s |
| Input_Voltage_L2 | Tension entrée phase 2 | V AC | 0-480 | ac elec volt phase:"B" sensor input | Voltage_Sensor | 1s |
| Input_Voltage_L3 | Tension entrée phase 3 | V AC | 0-480 | ac elec volt phase:"C" sensor input | Voltage_Sensor | 1s |
| Input_Current_L1 | Courant entrée phase 1 | A | 0-1000 | ac elec current phase:"A" sensor input | Current_Sensor | 1s |
| Input_Current_L2 | Courant entrée phase 2 | A | 0-1000 | ac elec current phase:"B" sensor input | Current_Sensor | 1s |
| Input_Current_L3 | Courant entrée phase 3 | A | 0-1000 | ac elec current phase:"C" sensor input | Current_Sensor | 1s |
| Input_Frequency | Fréquence d'entrée | Hz | 45-65 | ac elec freq sensor input | Frequency_Sensor | 1s |
| Input_Active_Power_Total | Puissance active totale entrée | kW | 0-1000 | ac elec power active sensor input | Power_Sensor | 1s |
| Input_Apparent_Power_Total | Puissance apparente totale entrée | kVA | 0-1000 | ac elec power apparent sensor input | Apparent_Power_Sensor | 1s |
| Input_Reactive_Power_Total | Puissance réactive totale entrée | kVAR | 0-1000 | ac elec power reactive sensor input | Reactive_Power_Sensor | 1s |
| Input_Power_Factor | Facteur de puissance entrée | pf | 0-1 | ac elec pf sensor input | Power_Factor_Sensor | 1s |
| Input_THD_Voltage | Distorsion harmonique tension entrée | % | 0-20 | ac elec volt thd sensor input | Sensor | 5s |
| Input_THD_Current | Distorsion harmonique courant entrée | % | 0-50 | ac elec current thd sensor input | Sensor | 5s |
| Input_Line_Bads | Compteur transitions hors tolérance | count | 0-999999 | ac elec sensor input fault counter | Sensor | 10s |

### Output (Sortie Électrique)

| Point | Description | Unité | Plage Typique | Haystack Tags | Brick Class | Fréquence |
|-------|-------------|-------|---------------|---------------|-------------|-----------|
| Output_Voltage_L1 | Tension sortie phase 1 | V AC | 0-480 | ac elec volt phase:"A" sensor output | Voltage_Sensor | 1s |
| Output_Voltage_L2 | Tension sortie phase 2 | V AC | 0-480 | ac elec volt phase:"B" sensor output | Voltage_Sensor | 1s |
| Output_Voltage_L3 | Tension sortie phase 3 | V AC | 0-480 | ac elec volt phase:"C" sensor output | Voltage_Sensor | 1s |
| Output_Current_L1 | Courant sortie phase 1 | A | 0-1000 | ac elec current phase:"A" sensor output | Current_Sensor | 1s |
| Output_Current_L2 | Courant sortie phase 2 | A | 0-1000 | ac elec current phase:"B" sensor output | Current_Sensor | 1s |
| Output_Current_L3 | Courant sortie phase 3 | A | 0-1000 | ac elec current phase:"C" sensor output | Current_Sensor | 1s |
| Output_Frequency | Fréquence de sortie | Hz | 45-65 | ac elec freq sensor output | Frequency_Sensor | 1s |
| Output_Active_Power_Total | Puissance active totale sortie | kW | 0-1000 | ac elec power active sensor output | Power_Sensor | 1s |
| Output_Apparent_Power_Total | Puissance apparente totale sortie | kVA | 0-1000 | ac elec power apparent sensor output | Apparent_Power_Sensor | 1s |
| Output_Reactive_Power_Total | Puissance réactive totale sortie | kVAR | 0-1000 | ac elec power reactive sensor output | Reactive_Power_Sensor | 1s |
| Output_Power_Factor | Facteur de puissance sortie | pf | 0-1 | ac elec pf sensor output | Power_Factor_Sensor | 1s |
| Output_Load_Percent_L1 | Charge sortie phase 1 | % | 0-200 | load sensor output phase:"A" | Load_Sensor | 1s |
| Output_Load_Percent_L2 | Charge sortie phase 2 | % | 0-200 | load sensor output phase:"B" | Load_Sensor | 1s |
| Output_Load_Percent_L3 | Charge sortie phase 3 | % | 0-200 | load sensor output phase:"C" | Load_Sensor | 1s |
| Output_Load_Percent_Total | Charge totale sortie | % | 0-200 | load sensor output | Load_Sensor | 1s |
| Output_THD_Voltage | Distorsion harmonique tension sortie | % | 0-10 | ac elec volt thd sensor output | Sensor | 5s |
| Output_Neutral_Current | Courant neutre sortie | A | 0-500 | ac elec current neutral sensor output | Current_Sensor | 1s |

### Bypass

| Point | Description | Unité | Plage Typique | Haystack Tags | Brick Class | Fréquence |
|-------|-------------|-------|---------------|---------------|-------------|-----------|
| Bypass_Voltage_L1 | Tension bypass phase 1 | V AC | 0-480 | ac elec volt phase:"A" sensor bypass | Voltage_Sensor | 1s |
| Bypass_Voltage_L2 | Tension bypass phase 2 | V AC | 0-480 | ac elec volt phase:"B" sensor bypass | Voltage_Sensor | 1s |
| Bypass_Voltage_L3 | Tension bypass phase 3 | V AC | 0-480 | ac elec volt phase:"C" sensor bypass | Voltage_Sensor | 1s |
| Bypass_Current_L1 | Courant bypass phase 1 | A | 0-1000 | ac elec current phase:"A" sensor bypass | Current_Sensor | 1s |
| Bypass_Current_L2 | Courant bypass phase 2 | A | 0-1000 | ac elec current phase:"B" sensor bypass | Current_Sensor | 1s |
| Bypass_Current_L3 | Courant bypass phase 3 | A | 0-1000 | ac elec current phase:"C" sensor bypass | Current_Sensor | 1s |
| Bypass_Frequency | Fréquence bypass | Hz | 45-65 | ac elec freq sensor bypass | Frequency_Sensor | 1s |
| Bypass_Power_Total | Puissance totale bypass | kW | 0-1000 | ac elec power sensor bypass | Power_Sensor | 1s |

### Battery (Batterie)

| Point | Description | Unité | Plage Typique | Haystack Tags | Brick Class | Fréquence |
|-------|-------------|-------|---------------|---------------|-------------|-----------|
| Battery_Voltage | Tension batterie | V DC | 0-600 | dc elec volt battery sensor | Voltage_Sensor | 1s |
| Battery_Current | Courant batterie (+ charge, - décharge) | A DC | -500 to 500 | dc elec current battery sensor | Current_Sensor | 1s |
| Battery_Charge_Percent | Charge batterie restante | % | 0-100 | battery stateOfCharge sensor | State_Of_Charge_Sensor | 10s |
| Battery_Runtime_Remaining | Autonomie restante estimée | min | 0-999 | battery sensor runtime | Sensor | 10s |
| Battery_Time_On_Battery | Temps écoulé sur batterie | s | 0-999999 | battery sensor discharge time | Sensor | 1s |
| Battery_Temperature | Température batterie | °C | -10 to 80 | battery temp sensor | Temperature_Sensor | 30s |
| Battery_Replacement_Date | Date remplacement batterie | date | - | battery sensor maintenance date | Sensor | 1h |
| Battery_Cycles_Count | Nombre cycles décharge | count | 0-5000 | battery sensor cycle counter | Sensor | 1h |
| Battery_Discharge_Energy | Énergie totale déchargée | kWh | 0-999999 | battery energy discharge sensor | Energy_Sensor | 5s |
| Battery_Charge_Energy | Énergie totale chargée | kWh | 0-999999 | battery energy charge sensor | Energy_Sensor | 5s |

### Température et Environnement

| Point | Description | Unité | Plage Typique | Haystack Tags | Brick Class | Fréquence |
|-------|-------------|-------|---------------|---------------|-------------|-----------|
| Inverter_Temperature | Température onduleur | °C | 0-100 | temp sensor inverter | Temperature_Sensor | 30s |
| Rectifier_Temperature | Température redresseur | °C | 0-100 | temp sensor rectifier | Temperature_Sensor | 30s |
| Ambient_Temperature | Température ambiante | °C | -10 to 60 | temp sensor ambient air | Air_Temperature_Sensor | 60s |
| Cabinet_Humidity | Humidité armoire | %RH | 0-100 | humidity sensor | Humidity_Sensor | 60s |

### Énergie et Compteurs

| Point | Description | Unité | Plage Typique | Haystack Tags | Brick Class | Fréquence |
|-------|-------------|-------|---------------|---------------|-------------|-----------|
| Energy_Output_Total | Énergie totale délivrée | kWh | 0-999999 | ac elec energy output sensor | Energy_Sensor | 5s |
| Energy_Input_Total | Énergie totale consommée | kWh | 0-999999 | ac elec energy input sensor | Energy_Sensor | 5s |
| Runtime_Hours_Total | Heures fonctionnement total | h | 0-999999 | sensor runtime total hours | Sensor | 1h |
| Efficiency_Percent | Rendement instantané | % | 80-99 | sensor efficiency | Efficiency_Sensor | 5s |

## Points de Commande (Actionneurs/Consignes)

| Point | Description | Unité | Plage | Haystack Tags | Brick Class |
|-------|-------------|-------|-------|---------------|-------------|
| Start_Command | Démarrage UPS | bool | 0/1 | cmd start | Start_Stop_Command |
| Shutdown_Command | Arrêt UPS | bool | 0/1 | cmd stop | Start_Stop_Command |
| Shutdown_Delay | Délai avant arrêt | s | -1 to 3600 | cmd sp shutdown delay | Setpoint |
| Startup_Delay | Délai avant démarrage | s | -1 to 3600 | cmd sp startup delay | Setpoint |
| Battery_Test_Start | Démarrage test batterie | bool | 0/1 | cmd battery test | Command |
| Battery_Test_Type | Type de test batterie | enum | 0-2 | cmd sp battery test | Setpoint |
| Eco_Mode_Enable | Activation mode ECO | bool | 0/1 | cmd enable eco mode | Enable_Command |
| Audible_Alarm_Mute | Silence alarme sonore | bool | 0/1 | cmd alarm mute | Command |

## Points d'État

### États de Fonctionnement

| Point | Description | Valeurs | Haystack Tags | Brick Class |
|-------|-------------|---------|---------------|-------------|
| Operating_Mode | Mode de fonctionnement | 0=Unknown, 1=Normal, 2=Battery, 3=Bypass, 4=ECO, 5=Maintenance, 6=Standby, 7=Fault | sensor enum mode | Operating_Mode_Status |
| Output_Source | Source alimentation sortie | 1=Other, 2=None, 3=Normal, 4=Bypass, 5=Battery, 6=Booster, 7=Reducer | sensor enum output source | Status |
| Battery_Status | État batterie | 1=Unknown, 2=Normal, 3=Low, 4=Depleted, 5=Charging | battery sensor enum | Battery_Status |
| UPS_On | UPS en service | 0=Off, 1=On | sensor ups enable | On_Off_Status |
| System_Ready | Système prêt | 0=Not Ready, 1=Ready | sensor ready | Status |
| Inverter_On | Onduleur en service | 0=Off, 1=On | sensor inverter enable | On_Off_Status |
| Rectifier_On | Redresseur en service | 0=Off, 1=On | sensor rectifier enable | On_Off_Status |
| Bypass_Active | Bypass actif | 0=Inactive, 1=Active | sensor bypass active | Status |
| Battery_Breaker_Open | Disjoncteur batterie ouvert | 0=Closed, 1=Open | battery sensor breaker | Status |
| Maintenance_Bypass_Active | Bypass maintenance actif | 0=Inactive, 1=Active | sensor bypass maintenance | Status |
| Auto_Restart_Enabled | Redémarrage auto activé | 0=Disabled, 1=Enabled | sensor enable auto restart | Status |

### Alarmes et Défauts

| Point | Description | Valeurs | Haystack Tags | Brick Class |
|-------|-------------|---------|---------------|-------------|
| Alarm_Present_Count | Nombre alarmes actives | 0-99 | sensor alarm counter | Alarm_Sensor |
| Battery_Low_Alarm | Alarme batterie faible | 0=Normal, 1=Alarm | battery sensor alarm low | Low_Battery_Alarm |
| Battery_Fault_Alarm | Alarme défaut batterie | 0=Normal, 1=Alarm | battery sensor alarm fault | Battery_Fault_Alarm |
| Overload_Alarm | Alarme surcharge | 0=Normal, 1=Alarm | sensor alarm overload | Overload_Alarm |
| Overheat_Alarm | Alarme surchauffe | 0=Normal, 1=Alarm | temp sensor alarm overheat | Temperature_Alarm |
| Communication_Lost_Alarm | Alarme perte communication | 0=Normal, 1=Alarm | sensor alarm communication | Communication_Alarm |
| Input_Bad_Alarm | Alarme entrée dégradée | 0=Normal, 1=Alarm | input sensor alarm fault | Alarm |

## Mappings Protocoles

### BACnet

| Point | Object Type | Object Instance | Units | R/W | Priority |
|-------|-------------|-----------------|-------|-----|----------|
| Output_Voltage_L1 | Analog Input | 0 | volts-AC | R | - |
| Output_Current_L1 | Analog Input | 1 | amperes-AC | R | - |
| Output_Frequency | Analog Input | 2 | hertz | R | - |
| Output_Active_Power_Total | Analog Input | 3 | kilowatts | R | - |
| Output_Load_Percent_Total | Analog Input | 4 | percent | R | - |
| Battery_Voltage | Analog Input | 10 | volts-DC | R | - |
| Battery_Current | Analog Input | 11 | amperes-DC | R | - |
| Battery_Charge_Percent | Analog Input | 12 | percent | R | - |
| Battery_Runtime_Remaining | Analog Input | 13 | minutes | R | - |
| Battery_Temperature | Analog Input | 14 | degrees-celsius | R | - |
| Input_Voltage_L1 | Analog Input | 20 | volts-AC | R | - |
| Input_Current_L1 | Analog Input | 21 | amperes-AC | R | - |
| Input_Frequency | Analog Input | 22 | hertz | R | - |
| Bypass_Voltage_L1 | Analog Input | 30 | volts-AC | R | - |
| Energy_Output_Total | Analog Input | 40 | kilowatt-hours | R | - |
| Efficiency_Percent | Analog Input | 41 | percent | R | - |
| Operating_Mode | Multi-State Input | 100 | no-units | R | - |
| Output_Source | Multi-State Input | 101 | no-units | R | - |
| Battery_Status | Multi-State Input | 102 | no-units | R | - |
| UPS_On | Binary Input | 200 | no-units | R | - |
| Inverter_On | Binary Input | 201 | no-units | R | - |
| Bypass_Active | Binary Input | 202 | no-units | R | - |
| Battery_Low_Alarm | Binary Input | 210 | no-units | R | - |
| Overload_Alarm | Binary Input | 211 | no-units | R | - |
| Overheat_Alarm | Binary Input | 212 | no-units | R | - |
| Start_Command | Binary Output | 300 | no-units | W | 8 |
| Shutdown_Command | Binary Output | 301 | no-units | W | 8 |
| Battery_Test_Start | Binary Output | 302 | no-units | W | 8 |
| Eco_Mode_Enable | Binary Output | 303 | no-units | W | 10 |
| Shutdown_Delay | Analog Output | 310 | seconds | W | 8 |

### Modbus

| Point | Type | Registre | Data Type | Unités | R/W |
|-------|------|----------|-----------|--------|-----|
| Output_Voltage_L1 | Input Register | 40001 | UINT16 | 0.1V AC | R |
| Output_Voltage_L2 | Input Register | 40002 | UINT16 | 0.1V AC | R |
| Output_Voltage_L3 | Input Register | 40003 | UINT16 | 0.1V AC | R |
| Output_Current_L1 | Input Register | 40004 | UINT16 | 0.1A AC | R |
| Output_Current_L2 | Input Register | 40005 | UINT16 | 0.1A AC | R |
| Output_Current_L3 | Input Register | 40006 | UINT16 | 0.1A AC | R |
| Output_Frequency | Input Register | 40007 | UINT16 | 0.1Hz | R |
| Output_Active_Power_Total | Input Register | 40008 | UINT16 | 0.1kW | R |
| Output_Apparent_Power_Total | Input Register | 40009 | UINT16 | 0.1kVA | R |
| Output_Load_Percent_Total | Input Register | 40010 | UINT16 | % | R |
| Battery_Voltage | Input Register | 40020 | UINT16 | 0.1V DC | R |
| Battery_Current | Input Register | 40021 | INT16 | 0.1A DC | R |
| Battery_Charge_Percent | Input Register | 40022 | UINT16 | % | R |
| Battery_Runtime_Remaining | Input Register | 40023 | UINT16 | min | R |
| Battery_Temperature | Input Register | 40024 | INT16 | °C | R |
| Battery_Time_On_Battery | Input Register | 40025 | UINT32 | s | R |
| Input_Voltage_L1 | Input Register | 40030 | UINT16 | 0.1V AC | R |
| Input_Voltage_L2 | Input Register | 40031 | UINT16 | 0.1V AC | R |
| Input_Voltage_L3 | Input Register | 40032 | UINT16 | 0.1V AC | R |
| Input_Current_L1 | Input Register | 40033 | UINT16 | 0.1A AC | R |
| Input_Frequency | Input Register | 40034 | UINT16 | 0.1Hz | R |
| Bypass_Voltage_L1 | Input Register | 40040 | UINT16 | 0.1V AC | R |
| Bypass_Frequency | Input Register | 40041 | UINT16 | 0.1Hz | R |
| Energy_Output_Total | Input Register | 40050 | UINT32 | 0.1kWh | R |
| Operating_Mode | Input Register | 40100 | UINT16 | enum | R |
| Output_Source | Input Register | 40101 | UINT16 | enum | R |
| Battery_Status | Input Register | 40102 | UINT16 | enum | R |
| Alarm_Present_Count | Input Register | 40110 | UINT16 | count | R |
| UPS_On | Coil | 00001 | BOOL | - | R |
| Inverter_On | Coil | 00002 | BOOL | - | R |
| Bypass_Active | Coil | 00003 | BOOL | - | R |
| Battery_Low_Alarm | Coil | 00010 | BOOL | - | R |
| Overload_Alarm | Coil | 00011 | BOOL | - | R |
| Start_Command | Holding Register | 40200 | UINT16 | 0/1 | R/W |
| Shutdown_Command | Holding Register | 40201 | UINT16 | 0/1 | R/W |
| Shutdown_Delay | Holding Register | 40202 | INT16 | s | R/W |
| Battery_Test_Start | Holding Register | 40203 | UINT16 | 0/1 | R/W |

## Sources

1. https://datatracker.ietf.org/doc/html/rfc1628 - RFC 1628 UPS Management Information Base (SNMP MIB)
2. https://project-haystack.org/doc/appendix/tags - Haystack Tags Reference
3. https://brickschema.org/ - Brick Schema Official Site
4. https://www.se.com/us/en/download/document/Modbus_MGE_Galax_Smart_UPS/ - Modbus Register Map MGE Galaxy, Smart-UPS
5. https://www.apc.com/us/en/download/document/SPD_CCON-SRVMAP_EN/ - Modbus Register Map Easy UPS SRV
6. https://www.eaton.com/content/dam/eaton/products/backup-power-ups-surge-it-power-distribution/power-management-software-connectivity/eaton-INDGW-modbus-map-UID0.pdf - Eaton INDGW Modbus/BACnet Map
7. https://www.vertiv.com/49b3b3/globalassets/products/monitoring-control-and-management/monitoring/vertiv-liebert-intellislot-rdu101-communications-card/vertiv-liebert-intellislot-modbus-and-bacnet-protocols-reference-guide-sl-28170.pdf - Liebert IntelliSlot Modbus/BACnet Protocols
8. https://www.dpstele.com/blog/ups-snmp-monitoring.php - UPS SNMP Monitoring Guide
9. https://networkupstools.org/ - Network UPS Tools (NUT)
10. https://www.csimn.com/CSI_pages/Modbus-UPS-Monitor.html - Modbus Interface for UPS Systems