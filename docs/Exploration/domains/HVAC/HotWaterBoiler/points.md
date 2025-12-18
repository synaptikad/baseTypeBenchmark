# Points de Chaudière Eau Chaude (Hot Water Boiler)

## Synthèse
- **Total points mesure** : 14
- **Total points commande** : 6
- **Total points état** : 10

## Points de Mesure (Capteurs)

| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| supply_temp | hot water leaving temp sensor | °C | 40-90 | 1min | Température eau départ |
| return_temp | hot water entering temp sensor | °C | 30-70 | 1min | Température eau retour |
| flue_temp | flue gas temp sensor | °C | 50-200 | 1min | Température fumées |
| outdoor_temp | outside air temp sensor | °C | -20-40 | 5min | Température extérieure (loi d'eau) |
| water_pressure | hot water pressure sensor | bar | 1-4 | 1min | Pression circuit eau |
| gas_pressure | gas pressure sensor | mbar | 15-30 | 1min | Pression gaz entrée |
| combustion_air_temp | combustion air temp sensor | °C | 10-40 | 5min | Température air comburant |
| burner_power | burner power sensor | % | 0-100 | 1min | Puissance brûleur (modulation) |
| thermal_power | thermal power sensor | kW | 0-5000 | 5min | Puissance thermique produite |
| fuel_consumption | fuel flow sensor | m³/h | 0-500 | 5min | Consommation combustible |
| efficiency | efficiency sensor | % | 80-110 | 5min | Rendement instantané |
| o2_flue | flue o2 sensor | % | 3-10 | 1min | Teneur O2 fumées |
| co_flue | flue co sensor | ppm | 0-500 | 1min | Teneur CO fumées |
| run_hours | run hours sensor | h | 0-99999 | 15min | Heures de fonctionnement |

## Points de Commande (Actionneurs/Consignes)

| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| enable_cmd | boiler enable cmd | - | 0/1 | Actionneur | Commande marche/arrêt |
| supply_temp_sp | hot water temp sp | °C | 40-90 | Consigne | Consigne température départ |
| burner_modulation_cmd | burner modulation cmd | % | 0-100 | Actionneur | Commande modulation brûleur |
| heating_curve_slope | heating curve slope sp | - | 0.5-2.0 | Consigne | Pente loi d'eau |
| heating_curve_offset | heating curve offset sp | K | -10-10 | Consigne | Décalage loi d'eau |
| setback_temp_sp | setback temp sp | °C | 30-50 | Consigne | Température réduit (nuit) |

## Points d'État

| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| burner_run | burner run status | Boolean | true/false | Brûleur en marche |
| flame_detected | flame detected status | Boolean | true/false | Flamme détectée |
| pump_run | pump run status | Boolean | true/false | Pompe chaudière en marche |
| modulation_active | modulation run status | Boolean | true/false | Modulation active |
| flame_fault | flame fault alarm | Boolean | true/false | Défaut flamme |
| high_temp_alarm | high temp alarm | Boolean | true/false | Alarme haute température |
| low_pressure_alarm | low pressure alarm | Boolean | true/false | Alarme basse pression |
| high_pressure_alarm | high pressure alarm | Boolean | true/false | Alarme haute pression |
| flue_fault | flue fault alarm | Boolean | true/false | Défaut évacuation fumées |
| general_fault | boiler fault alarm | Boolean | true/false | Défaut général |

## Mappings Protocoles

| Point | BACnet Object | Modbus Register | OpenTherm |
|-------|---------------|-----------------|-----------|
| supply_temp | AI:1 | 40001 (HR) | ID 25 |
| return_temp | AI:2 | 40002 (HR) | ID 28 |
| flue_temp | AI:3 | 40003 (HR) | - |
| outdoor_temp | AI:4 | 40004 (HR) | ID 27 |
| water_pressure | AI:5 | 40005 (HR) | ID 18 |
| gas_pressure | AI:6 | 40006 (HR) | - |
| burner_power | AI:7 | 40007 (HR) | ID 17 |
| thermal_power | AV:1 | 40101 (HR) | - |
| fuel_consumption | AI:8 | 40008 (HR) | - |
| efficiency | AV:2 | 40102 (HR) | - |
| enable_cmd | BO:1 | 00001 (Coil) | ID 0 |
| supply_temp_sp | AV:3 | 40103 (HR) | ID 1 |
| burner_modulation_cmd | AO:1 | 40201 (HR) | ID 14 |
| burner_run | BI:1 | 10001 (DI) | ID 3.0 |
| flame_detected | BI:2 | 10002 (DI) | ID 3.3 |
| flame_fault | BI:3 | 10003 (DI) | ID 5.0 |
| general_fault | BI:4 | 10004 (DI) | ID 0.0 |

## Loi d'Eau Typique

| T_extérieure | T_départ (pente 1.0) | T_départ (pente 1.5) |
|--------------|----------------------|----------------------|
| -10°C | 70°C | 85°C |
| 0°C | 55°C | 62°C |
| 10°C | 40°C | 40°C |
| 20°C | Arrêt | Arrêt |

## Sources
- EN 303 / EN 15502 - Boiler Efficiency Standards
- ASHRAE Handbook - HVAC Systems and Equipment
- OpenTherm Specification - Communication Protocol
- Viessmann / Buderus - BACnet/Modbus Integration Guides
