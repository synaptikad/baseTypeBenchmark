# Points de VRF (Variable Refrigerant Flow)

## Synthèse
- **Total points mesure** : 45
- **Total points commande** : 18
- **Total points état** : 15

## Points de Mesure (Capteurs)

### Outdoor Unit (Unité Extérieure)

| Point | Description | Unité | Plage | Haystack Tags | Brick Class | Fréquence |
|-------|-------------|-------|-------|---------------|-------------|-----------|
| Condensing Temperature | Température condensation | °C | -10 à 70 | `condensing`, `refrig`, `temp`, `sensor` | `brick:Condensing_Temperature_Sensor` | 1-5s |
| Evaporating Temperature | Température évaporation | °C | -20 à 15 | `evaporating`, `refrig`, `temp`, `sensor` | `brick:Evaporating_Temperature_Sensor` | 1-5s |
| Discharge Line Temperature | Température refoulement | °C | 40 à 130 | `discharge`, `refrig`, `temp`, `sensor` | `brick:Discharge_Temperature_Sensor` | 1-5s |
| Suction Line Temperature | Température aspiration | °C | -10 à 30 | `suction`, `refrig`, `temp`, `sensor` | `brick:Suction_Temperature_Sensor` | 1-5s |
| Liquid Line Temperature | Température ligne liquide | °C | 5 à 50 | `liquid`, `refrig`, `temp`, `sensor` | `brick:Liquid_Line_Temperature_Sensor` | 1-5s |
| High Pressure (Discharge) | Pression haute | bar | 15-42 | `discharge`, `refrig`, `pressure`, `sensor` | `brick:Discharge_Pressure_Sensor` | 1-5s |
| Low Pressure (Suction) | Pression basse | bar | 4-12 | `suction`, `refrig`, `pressure`, `sensor` | `brick:Suction_Pressure_Sensor` | 1-5s |
| Outdoor Air Temperature | Température air extérieur | °C | -30 à 50 | `outdoor`, `air`, `temp`, `sensor` | `brick:Outside_Air_Temperature_Sensor` | 10-60s |
| Compressor Frequency | Fréquence compresseur | Hz | 10-120 | `compressor`, `freq`, `sensor` | `brick:Frequency_Sensor` | 1-5s |
| Compressor Runtime | Temps fonctionnement | h | 0-100000 | `compressor`, `run`, `duration`, `sensor` | `brick:Run_Time_Sensor` | 1h |
| Outdoor Fan Speed | Vitesse ventilateur | % | 0-100 | `outdoor`, `fan`, `speed`, `sensor` | `brick:Fan_Speed_Sensor` | 5-10s |
| Outdoor Unit Power | Puissance électrique | kW | 2-50 | `outdoor`, `elec`, `power`, `sensor` | `brick:Electric_Power_Sensor` | 1-5s |
| Outdoor Unit Energy | Énergie consommée | kWh | 0-999999 | `outdoor`, `elec`, `energy`, `sensor` | `brick:Energy_Sensor` | 15-60min |
| Oil Level | Niveau huile | % | 0-100 | `compressor`, `oil`, `level`, `sensor` | `brick:Oil_Level_Sensor` | 1h |
| Refrigerant Leak Detection | Détection fuite | ppm | 0-1000 | `refrig`, `leak`, `concentration`, `sensor` | `brick:Refrigerant_Sensor` | 1-5s |
| Compressor Current | Courant compresseur | A | 5-80 | `compressor`, `elec`, `current`, `sensor` | `brick:Electric_Current_Sensor` | 1-5s |

### Indoor Unit (Unité Intérieure) - Par unité

| Point | Description | Unité | Plage | Haystack Tags | Brick Class | Fréquence |
|-------|-------------|-------|-------|---------------|-------------|-----------|
| Room Temperature | Température zone | °C | 10 à 35 | `zone`, `air`, `temp`, `sensor` | `brick:Zone_Air_Temperature_Sensor` | 10-60s |
| Return Air Temperature | Température reprise | °C | 15 à 30 | `return`, `air`, `temp`, `sensor` | `brick:Return_Air_Temperature_Sensor` | 10-60s |
| Liquid Pipe Temperature | Température tuyau liquide | °C | 0 à 20 | `liquid`, `refrig`, `temp`, `sensor` | `brick:Liquid_Line_Temperature_Sensor` | 5-10s |
| Gas Pipe Temperature | Température tuyau gaz | °C | 5 à 25 | `gas`, `refrig`, `temp`, `sensor` | `brick:Suction_Temperature_Sensor` | 5-10s |
| Indoor Unit Power | Puissance électrique | W | 20-500 | `elec`, `power`, `sensor` | `brick:Electric_Power_Sensor` | 5-10s |
| Indoor Unit Energy | Énergie consommée | kWh | 0-99999 | `elec`, `energy`, `sensor` | `brick:Energy_Sensor` | 15-60min |
| Fan Speed Feedback | Vitesse ventilateur | % | 0-100 | `fan`, `speed`, `sensor` | `brick:Fan_Speed_Sensor` | 5-10s |
| Airflow Rate | Débit d'air | m³/h | 100-2000 | `air`, `flow`, `sensor` | `brick:Supply_Air_Flow_Sensor` | 10-60s |
| Filter Pressure Drop | Perte charge filtre | Pa | 0-300 | `filter`, `differential`, `pressure`, `sensor` | `brick:Filter_Differential_Pressure_Sensor` | 1h |
| Humidity Sensor | Humidité zone | %RH | 0-100 | `zone`, `air`, `humidity`, `sensor` | `brick:Zone_Air_Humidity_Sensor` | 1-5min |
| Occupancy Sensor | Présence | bool | 0/1 | `zone`, `occupied`, `sensor` | `brick:Occupancy_Sensor` | 1-10s |
| Condensate Overflow | Débordement | bool | 0/1 | `condensate`, `overflow`, `sensor` | `brick:Condensate_Sensor` | real-time |

## Points de Commande (Actionneurs/Consignes)

### Outdoor Unit

| Point | Description | Unité | Plage | Haystack Tags | Brick Class |
|-------|-------------|-------|-------|---------------|-------------|
| System On/Off Command | Marche/arrêt système | bool | 0/1 | `vrf`, `cmd` | `brick:On_Off_Command` |
| Master Mode Command | Mode maître | enum | Cool/Heat/Auto | `hvacMode`, `cmd` | `brick:Mode_Command` |
| Outdoor Fan Speed Command | Vitesse ventilateur | % | 0-100 | `outdoor`, `fan`, `speed`, `cmd` | `brick:Fan_Speed_Command` |
| Compressor Frequency Setpoint | Fréquence compresseur | Hz | 10-120 | `compressor`, `freq`, `sp` | `brick:Frequency_Setpoint` |
| Defrost Initiate Command | Dégivrage | bool | 0/1 | `defrost`, `cmd` | `brick:Defrost_Command` |

### Indoor Unit - Par unité

| Point | Description | Unité | Plage | Haystack Tags | Brick Class |
|-------|-------------|-------|-------|---------------|-------------|
| Unit On/Off Command | Marche/arrêt | bool | 0/1 | `cmd` | `brick:On_Off_Command` |
| Operation Mode Command | Mode fonctionnement | enum | Cool/Heat/Dry/Fan/Auto | `hvacMode`, `cmd` | `brick:Mode_Command` |
| Temperature Setpoint | Consigne température | °C | 16-32 | `zone`, `air`, `temp`, `sp` | `brick:Zone_Air_Temperature_Setpoint` |
| Cooling Setpoint | Consigne froid | °C | 18-32 | `zone`, `air`, `cooling`, `temp`, `sp` | `brick:Cooling_Temperature_Setpoint` |
| Heating Setpoint | Consigne chaud | °C | 16-28 | `zone`, `air`, `heating`, `temp`, `sp` | `brick:Heating_Temperature_Setpoint` |
| Fan Speed Command | Vitesse ventilateur | enum | Auto/Low/Med/High | `fan`, `speed`, `cmd` | `brick:Fan_Speed_Command` |
| Louver Position Command | Position volets | enum | Auto/Pos1-5/Swing | `louver`, `position`, `cmd` | `brick:Damper_Position_Command` |
| Vertical Airflow Direction | Direction verticale | enum | Up/Center/Down/Auto | `airflow`, `vertical`, `direction`, `cmd` | `brick:Damper_Position_Command` |
| Horizontal Airflow Direction | Direction horizontale | enum | Left/Center/Right/Swing | `airflow`, `horizontal`, `direction`, `cmd` | `brick:Damper_Position_Command` |
| Setpoint Override | Blocage consigne | bool | 0/1 | `sp`, `lock`, `cmd` | `brick:Enable_Command` |
| Quiet Mode Command | Mode silencieux | bool | 0/1 | `quietMode`, `cmd` | `brick:Enable_Command` |
| Filter Sign Reset | Reset filtre | pulse | Pulse | `filter`, `reset`, `cmd` | `brick:Reset_Command` |

## Points d'État

### Outdoor Unit

| Point | Description | Valeurs | Haystack Tags | Brick Class |
|-------|-------------|---------|---------------|-------------|
| System Running Status | État système | Off/On | `vrf`, `run`, `status` | `brick:Run_Status` |
| Compressor Status | État compresseur | Off/Running | `compressor`, `run`, `status` | `brick:Compressor_Status` |
| Outdoor Fan Status | État ventilateur | Off/Running | `outdoor`, `fan`, `run`, `status` | `brick:Fan_Status` |
| Defrost Mode Active | Dégivrage actif | Off/Active | `defrost`, `mode`, `status` | `brick:Defrost_Status` |
| Fault Code ODU | Code défaut | 00-99 | `fault`, `alarm` | `brick:Fault_Status` |
| Master Thermostat Priority | Priorité maître | Cool/Heat | `master`, `priority`, `status` | `brick:Status` |

### Indoor Unit - Par unité

| Point | Description | Valeurs | Haystack Tags | Brick Class |
|-------|-------------|---------|---------------|-------------|
| Unit Running Status | État unité | Off/On/Standby | `run`, `status` | `brick:Run_Status` |
| Current Operation Mode | Mode actuel | Cool/Heat/Dry/Fan/Auto | `hvacMode`, `status` | `brick:Mode_Status` |
| Alarm Status IDU | Alarme | Normal/Alarm | `alarm`, `status` | `brick:Alarm_Status` |
| Malfunction Code IDU | Code défaut | 00-99 | `fault`, `alarm` | `brick:Fault_Status` |
| Filter Status | État filtre | Clean/Dirty | `filter`, `alarm`, `status` | `brick:Filter_Status` |
| Communication Status | Communication | OK/Lost | `comm`, `status` | `brick:Communication_Status` |
| EEV Position | Position vanne | 0-500 steps | `valve`, `position`, `status` | `brick:Valve_Position_Status` |
| Thermo On Status | État thermostat | Off/On | `thermostat`, `status` | `brick:Thermostat_Status` |

## Mappings Protocoles

### BACnet

| Point | Object Type | Object Instance | Units | R/W |
|-------|-------------|-----------------|-------|-----|
| Room Temperature | Analog Input (AI) | AI:1001 | degrees-celsius | R |
| Temperature Setpoint | Analog Value (AV) | AV:1001 | degrees-celsius | R/W |
| Unit On/Off Command | Binary Output (BO) | BO:1001 | - | W |
| Unit Running Status | Binary Input (BI) | BI:1001 | - | R |
| Operation Mode Command | Multi-state Output (MSO) | MSO:1001 | enum (1-5) | W |
| Current Operation Mode | Multi-state Input (MSI) | MSI:1001 | enum (1-5) | R |
| Fan Speed Command | Multi-state Output (MSO) | MSO:1002 | enum (1-4) | W |
| Alarm Status | Binary Input (BI) | BI:1002 | - | R |
| Power Consumption | Analog Input (AI) | AI:1003 | kilowatts | R |

### Modbus

| Point | Type | Registre | Data Type | Unités |
|-------|------|----------|-----------|--------|
| Room Temperature | Holding Register | 40001 | INT16 | 0.1°C |
| Temperature Setpoint | Holding Register | 40101 | INT16 | 0.1°C |
| Unit On/Off Command | Coil | 00001 | BOOL | - |
| Unit Running Status | Discrete Input | 10001 | BOOL | - |
| Operation Mode | Holding Register | 40201 | UINT16 | enum |
| Fan Speed | Holding Register | 40301 | UINT16 | enum |
| Compressor Frequency | Input Register | 30001 | UINT16 | Hz |
| High Pressure | Input Register | 30101 | UINT16 | 0.1 bar |
| Power Consumption | Input Register | 30301 | UINT16 | 0.1 kW |
| Fault Code ODU | Input Register | 30501 | UINT16 | code |

### KNX

| Point | DPT | Description | Unités |
|-------|-----|-------------|--------|
| Unit On/Off | DPT 1.001 | Switch | bool |
| Room Temperature | DPT 9.001 | Temperature (°C) | °C |
| Temperature Setpoint | DPT 9.001 | Temperature (°C) | °C |
| HVAC Mode | DPT 20.102 | HVAC Mode | enum |
| Fan Speed | DPT 5.001 | Scaling (%) | % |
| Alarm Status | DPT 1.005 | Alarm | bool |
| Energy Consumption | DPT 13.010 | Active Energy (Wh) | Wh |
| Power Consumption | DPT 14.056 | Power (kW) | kW |

## Sources

- [Project Haystack - VRF System](https://project-haystack.org/doc/docHaystack/VRF)
- [Brick Schema](https://brickschema.org/)
- [Daikin VRV BACnet Integration](https://www.daikinac.com/content/commercial/accessories-and-controllers/bacnet-interface-dms502b71/)
- [Mitsubishi Electric BACnet](https://www.mitsubishitechinfo.ca/sites/default/files/BACnet%20points%20list%20MEAPP0002_0.pdf)
- [CoolAutomation - VRF Integration](https://coolautomation.com/building-management-systems-professionals/daikin-vrv-hvac-integration-with-bms/)
- [VRF Leak Detection](https://macurco.com/product/rd-vrf/)
- [VRF Monitoring Research](https://www.researchgate.net/publication/341878588_Power_consumption_and_energy_efficiency_of_VRF_system_based_on_large_scale_monitoring_virtual_sensors)
