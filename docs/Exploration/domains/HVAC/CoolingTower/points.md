# Points de Cooling Tower

## Synthèse
- **Total points mesure** : 28
- **Total points commande** : 12
- **Total points état** : 8

## Points de Mesure (Capteurs)

| Point | Description | Unité | Plage Typique | Haystack Tags | Brick Class | Fréquence |
|-------|-------------|-------|---------------|---------------|-------------|-----------|
| Entering Water Temp | Température eau entrée tour | °C | 30-40 | `condenser-water-entering-temp-sensor` | `brick:Entering_Water_Temperature_Sensor` | 30s |
| Leaving Water Temp | Température eau sortie tour | °C | 18-32 | `condenser-water-leaving-temp-sensor` | `brick:Leaving_Water_Temperature_Sensor` | 30s |
| Ambient Wet Bulb Temp | Température humide air extérieur | °C | -5-30 | `outside-air-wetBulb-temp-sensor` | `brick:Outside_Air_Wet_Bulb_Temperature_Sensor` | 1min |
| Ambient Dry Bulb Temp | Température sèche air extérieur | °C | -10-40 | `outside-air-temp-sensor` | `brick:Outside_Air_Temperature_Sensor` | 1min |
| Basin Water Temp | Température eau dans bassin | °C | 2-40 | `basin-water-temp-sensor` | `brick:Water_Temperature_Sensor` | 1min |
| Approach Temperature | Écart eau sortie / wet bulb | °C | 3-10 | `approach-temp-sensor` | `brick:Differential_Temperature_Sensor` | 1min |
| Range Temperature | Écart eau entrée / sortie | °C | 5-15 | `range-temp-sensor` | `brick:Differential_Temperature_Sensor` | 1min |
| Condenser Water Flow | Débit eau condenseur | m³/h | 50-1000 | `condenser-water-flow-sensor` | `brick:Water_Flow_Sensor` | 30s |
| Makeup Water Flow | Débit eau d'appoint | L/min | 0-200 | `makeup-water-flow-sensor` | `brick:Makeup_Water_Flow_Sensor` | 1min |
| Blowdown Water Flow | Débit eau de purge | L/min | 0-100 | `blowdown-water-flow-sensor` | `brick:Blowdown_Water_Flow_Sensor` | 1min |
| Basin Water Level | Niveau d'eau bassin | % | 0-100 | `basin-water-level-sensor` | `brick:Water_Level_Sensor` | 30s |
| Water Conductivity | Conductivité eau | µS/cm | 500-5000 | `water-conductivity-sensor` | `brick:Conductivity_Sensor` | 5min |
| Water pH | pH eau | pH | 6.5-9.5 | `water-ph-sensor` | `brick:pH_Sensor` | 15min |
| Condenser Water Pressure | Pression eau condenseur | bar | 1-6 | `condenser-water-pressure-sensor` | `brick:Water_Pressure_Sensor` | 30s |
| Total Power Consumption | Puissance électrique totale | kW | 5-200 | `elec-power-sensor` | `brick:Electric_Power_Sensor` | 1min |
| Fan 1 Power | Puissance ventilateur 1 | kW | 2-50 | `fan-elec-power-sensor` | `brick:Fan_Electric_Power_Sensor` | 1min |
| Fan 2 Power | Puissance ventilateur 2 | kW | 2-50 | `fan-elec-power-sensor` | `brick:Fan_Electric_Power_Sensor` | 1min |
| Fan 3 Power | Puissance ventilateur 3 | kW | 2-50 | `fan-elec-power-sensor` | `brick:Fan_Electric_Power_Sensor` | 1min |
| Energy Meter Total | Énergie cumulée | kWh | 0-999999 | `elec-energy-sensor` | `brick:Electric_Energy_Sensor` | Horaire |
| Thermal Energy Rejected | Énergie thermique rejetée | kWh | 0-999999 | `cooling-thermal-energy-sensor` | `brick:Thermal_Energy_Sensor` | Horaire |
| Fan 1 Vibration | Vibration ventilateur 1 | mm/s | 0-20 | `vibration-sensor` | `brick:Vibration_Sensor` | 1min |
| Fan 2 Vibration | Vibration ventilateur 2 | mm/s | 0-20 | `vibration-sensor` | `brick:Vibration_Sensor` | 1min |
| Fan 3 Vibration | Vibration ventilateur 3 | mm/s | 0-20 | `vibration-sensor` | `brick:Vibration_Sensor` | 1min |
| Makeup Water Total | Volume eau appoint cumulé | m³ | 0-999999 | `makeup-water-volume-sensor` | `brick:Water_Volume_Sensor` | Horaire |
| Cycles of Concentration | Ratio conductivité | ratio | 2-10 | `cycles-concentration-sensor` | N/A | 15min |

## Points de Commande (Actionneurs/Consignes)

| Point | Description | Unité | Plage | Haystack Tags | Brick Class |
|-------|-------------|-------|-------|---------------|-------------|
| Leaving Water Temp Setpoint | Consigne température eau sortie | °C | 18-32 | `condenser-water-leaving-temp-sp` | `brick:Leaving_Water_Temperature_Setpoint` |
| Approach Setpoint | Consigne approche | °C | 3-7 | `approach-temp-sp` | `brick:Differential_Temperature_Setpoint` |
| Fan 1 Speed Command | Vitesse ventilateur 1 | % | 0-100 | `fan-speed-cmd` | `brick:Fan_Speed_Setpoint` |
| Fan 2 Speed Command | Vitesse ventilateur 2 | % | 0-100 | `fan-speed-cmd` | `brick:Fan_Speed_Setpoint` |
| Fan 3 Speed Command | Vitesse ventilateur 3 | % | 0-100 | `fan-speed-cmd` | `brick:Fan_Speed_Setpoint` |
| Fan 1 Enable | Activation ventilateur 1 | ON/OFF | - | `fan-enable-cmd` | `brick:Enable_Command` |
| Fan 2 Enable | Activation ventilateur 2 | ON/OFF | - | `fan-enable-cmd` | `brick:Enable_Command` |
| Fan 3 Enable | Activation ventilateur 3 | ON/OFF | - | `fan-enable-cmd` | `brick:Enable_Command` |
| Blowdown Valve Command | Ouverture valve purge | ON/OFF | - | `blowdown-valve-cmd` | `brick:Valve_Command` |
| Makeup Water Valve Command | Ouverture valve appoint | ON/OFF | - | `makeup-water-valve-cmd` | `brick:Valve_Command` |
| Basin Heater Enable | Activation chauffage bassin | ON/OFF | - | `basin-heater-enable-cmd` | `brick:Enable_Command` |
| Conductivity Setpoint | Consigne conductivité | µS/cm | 1500-4000 | `conductivity-sp` | `brick:Conductivity_Setpoint` |

## Points d'État

| Point | Description | Valeurs | Haystack Tags | Brick Class |
|-------|-------------|---------|---------------|-------------|
| Tower Operating Status | État tour | OFF/ON/FAULT | `run-status` | `brick:Run_Status` |
| Fan 1 Status | État ventilateur 1 | OFF/ON/FAULT | `fan-run-status` | `brick:Fan_Run_Status` |
| Fan 2 Status | État ventilateur 2 | OFF/ON/FAULT | `fan-run-status` | `brick:Fan_Run_Status` |
| Fan 3 Status | État ventilateur 3 | OFF/ON/FAULT | `fan-run-status` | `brick:Fan_Run_Status` |
| High Temperature Alarm | Alarme température haute | NORMAL/ALARM | `temp-sensor alarm` | `brick:High_Temperature_Alarm` |
| Low Basin Water Level Alarm | Alarme niveau bas | NORMAL/ALARM | `level-sensor alarm` | `brick:Low_Water_Level_Alarm` |
| High Conductivity Alarm | Alarme conductivité haute | NORMAL/ALARM | `conductivity-sensor alarm` | `brick:High_Conductivity_Alarm` |
| Fan Vibration Alarm | Alarme vibration | NORMAL/ALARM | `vibration-sensor alarm` | `brick:Vibration_Alarm` |

## Mappings Protocoles

### BACnet

| Point | Object Type | Object Instance | Units | Writable |
|-------|-------------|-----------------|-------|----------|
| Entering Water Temp | Analog Input (AI) | 1 | degreesCelsius | No |
| Leaving Water Temp | Analog Input (AI) | 2 | degreesCelsius | No |
| Wet Bulb Temp | Analog Input (AI) | 3 | degreesCelsius | No |
| Condenser Water Flow | Analog Input (AI) | 20 | cubicMetersPerHour | No |
| Conductivity | Analog Input (AI) | 31 | microsiemensPerCentimeter | No |
| Leaving Water Temp SP | Analog Output (AO) | 100 | degreesCelsius | Yes |
| Fan 1 Speed Command | Analog Output (AO) | 110 | percent | Yes |
| Fan 1 Enable | Binary Output (BO) | 120 | noUnits | Yes |
| Tower Operating Status | Binary Value (BV) | 200 | noUnits | No |
| High Temp Alarm | Binary Value (BV) | 300 | noUnits | No |

### Modbus

| Point | Type | Adresse | Format | Unité |
|-------|------|---------|--------|-------|
| Entering Water Temp | Holding | 40001 | INT16 | °C × 10 |
| Leaving Water Temp | Holding | 40002 | INT16 | °C × 10 |
| Condenser Water Flow | Holding | 40010 | UINT16 | m³/h |
| Conductivity | Holding | 40016 | UINT16 | µS/cm |
| Leaving Water Temp SP | Holding | 40100 | INT16 | °C × 10 (RW) |
| Fan 1 Speed CMD | Holding | 40110 | UINT16 | % × 10 (RW) |
| Fan 1 Enable | Coil | 00001 | BOOL | ON/OFF (RW) |
| Fan 1 Status | Discrete Input | 10001 | BOOL | ON/OFF |

## Sources

- [Project Haystack - Cooling Tower Tags](https://project-haystack.org/forum/topic/839)
- [Brick Schema - Cooling Tower Class](https://brickschema.org/ontology/1.3/classes/Cooling_Tower/)
- [SPX Cooling Technologies - MarleyGard LINK BACnet/IP](https://spxcooling.com/library/marleygard-link-bacnet-ip-communication-panel/)
- [MEP Academy - Cooling Tower Fan Speed Control](https://mepacademy.com/cooling-tower-fan-speed-control/)
- [Cooling Best Practices - Entering Condenser Water Temperature Reset](https://coolingbestpractices.com/technology/cooling-controls/optimize-chillers-automatic-entering-condenser-water-temperature-reset)
