# Points de Rooftop Unit (RTU)

## Synthèse
- **Total points mesure** : 20
- **Total points commande** : 12
- **Total points état** : 12

## Points de Mesure (Capteurs)

| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| outdoor_temp | outside air temp sensor | °C | -20-45 | 1min | Température air extérieur |
| outdoor_humidity | outside air humidity sensor | %RH | 10-100 | 1min | Humidité air extérieur |
| return_temp | return air temp sensor | °C | 18-28 | 1min | Température air reprise |
| mixed_temp | mixed air temp sensor | °C | 10-30 | 1min | Température air mélangé |
| discharge_temp | discharge air temp sensor | °C | 12-25 | 1min | Température air soufflé |
| zone_temp | zone air temp sensor | °C | 18-28 | 1min | Température zone (thermostat) |
| supply_flow | supply air flow sensor | m³/h | 0-50000 | 1min | Débit air soufflé |
| supply_static_pressure | discharge duct pressure sensor | Pa | 0-1000 | 1min | Pression statique gaine |
| supply_fan_speed | supply fan speed sensor | % | 0-100 | 1min | Vitesse ventilateur soufflage |
| return_fan_speed | return fan speed sensor | % | 0-100 | 1min | Vitesse ventilateur reprise |
| refrigerant_hp | refrig discharge pressure sensor | bar | 10-30 | 30sec | Haute pression réfrigérant |
| refrigerant_lp | refrig suction pressure sensor | bar | 2-8 | 30sec | Basse pression réfrigérant |
| compressor_current | compressor elec current sensor | A | 0-200 | 1min | Courant compresseur |
| heating_stage | heating stage sensor | - | 0-4 | 1min | Étage de chauffage actif |
| cooling_stage | cooling stage sensor | - | 0-4 | 1min | Étage de refroidissement actif |
| oa_damper_position | outside air damper position sensor | % | 0-100 | 1min | Position registre air neuf |
| filter_dp | filter differential pressure sensor | Pa | 50-500 | 5min | Pression différentielle filtres |
| gas_valve_status | gas valve position sensor | % | 0-100 | 1min | Position vanne gaz (si gaz) |
| power_consumption | elec power sensor | kW | 0-100 | 5min | Puissance électrique totale |
| run_hours | run hours sensor | h | 0-99999 | 15min | Heures de fonctionnement |

## Points de Commande (Actionneurs/Consignes)

| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| unit_enable_cmd | enable cmd | - | 0/1 | Actionneur | Commande marche/arrêt unité |
| zone_temp_cooling_sp | zone air temp cooling sp | °C | 22-28 | Consigne | Consigne température refroidissement |
| zone_temp_heating_sp | zone air temp heating sp | °C | 18-22 | Consigne | Consigne température chauffage |
| supply_fan_speed_cmd | supply fan speed cmd | % | 0-100 | Actionneur | Commande vitesse ventilateur soufflage |
| return_fan_speed_cmd | return fan speed cmd | % | 0-100 | Actionneur | Commande vitesse ventilateur reprise |
| oa_damper_cmd | outside air damper cmd | % | 0-100 | Actionneur | Commande registre air neuf |
| oa_damper_min_sp | outside air damper min sp | % | 10-30 | Consigne | Position minimale air neuf |
| cooling_capacity_cmd | cooling capacity cmd | % | 0-100 | Actionneur | Demande capacité refroidissement |
| heating_capacity_cmd | heating capacity cmd | % | 0-100 | Actionneur | Demande capacité chauffage |
| economizer_enable_cmd | economizer enable cmd | - | 0/1 | Actionneur | Activation économiseur |
| supply_pressure_sp | discharge duct pressure sp | Pa | 200-800 | Consigne | Consigne pression gaine |
| unit_mode_cmd | unit mode cmd | - | off/heat/cool/auto | Actionneur | Commande mode fonctionnement |

## Points d'État

| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| supply_fan_run | supply fan run status | Boolean | true/false | Ventilateur soufflage en marche |
| return_fan_run | return fan run status | Boolean | true/false | Ventilateur reprise en marche |
| compressor1_run | compressor1 run status | Boolean | true/false | Compresseur 1 en marche |
| compressor2_run | compressor2 run status | Boolean | true/false | Compresseur 2 en marche |
| heating_active | heating run status | Boolean | true/false | Chauffage actif |
| cooling_active | cooling run status | Boolean | true/false | Refroidissement actif |
| economizer_active | economizer run status | Boolean | true/false | Économiseur actif |
| hp_alarm | high pressure alarm | Boolean | true/false | Alarme haute pression |
| lp_alarm | low pressure alarm | Boolean | true/false | Alarme basse pression |
| filter_dirty_alarm | filter dirty alarm | Boolean | true/false | Alarme filtre encrassé |
| freeze_protect_active | freeze protect alarm | Boolean | true/false | Protection antigel active |
| general_fault | unit fault alarm | Boolean | true/false | Défaut général unité |

## Mappings Protocoles

| Point | BACnet Object | Modbus Register | KNX GA |
|-------|---------------|-----------------|--------|
| outdoor_temp | AI:1 | 40001 (HR) | 1/1/1 |
| outdoor_humidity | AI:2 | 40002 (HR) | 1/1/2 |
| return_temp | AI:3 | 40003 (HR) | 1/1/3 |
| mixed_temp | AI:4 | 40004 (HR) | 1/1/4 |
| discharge_temp | AI:5 | 40005 (HR) | 1/1/5 |
| zone_temp | AI:6 | 40006 (HR) | 1/1/6 |
| supply_flow | AI:7 | 40007 (HR) | 1/1/7 |
| supply_static_pressure | AI:8 | 40008 (HR) | 1/1/8 |
| supply_fan_speed | AI:9 | 40009 (HR) | 1/1/9 |
| return_fan_speed | AI:10 | 40010 (HR) | 1/1/10 |
| refrigerant_hp | AI:11 | 40011 (HR) | 1/1/11 |
| refrigerant_lp | AI:12 | 40012 (HR) | 1/1/12 |
| compressor_current | AI:13 | 40013 (HR) | 1/1/13 |
| heating_stage | AI:14 | 40014 (HR) | 1/1/14 |
| cooling_stage | AI:15 | 40015 (HR) | 1/1/15 |
| oa_damper_position | AI:16 | 40016 (HR) | 1/1/16 |
| filter_dp | AI:17 | 40017 (HR) | 1/1/17 |
| gas_valve_status | AI:18 | 40018 (HR) | 1/1/18 |
| power_consumption | AI:19 | 40019 (HR) | 1/1/19 |
| run_hours | AI:20 | 40020 (HR) | 1/1/20 |
| unit_enable_cmd | BO:1 | 00001 (Coil) | 1/2/1 |
| zone_temp_cooling_sp | AV:1 | 40101 (HR) | 1/2/2 |
| zone_temp_heating_sp | AV:2 | 40102 (HR) | 1/2/3 |
| supply_fan_speed_cmd | AO:1 | 40201 (HR) | 1/2/4 |
| return_fan_speed_cmd | AO:2 | 40202 (HR) | 1/2/5 |
| oa_damper_cmd | AO:3 | 40203 (HR) | 1/2/6 |
| oa_damper_min_sp | AV:3 | 40103 (HR) | 1/2/7 |
| cooling_capacity_cmd | AO:4 | 40204 (HR) | 1/2/8 |
| heating_capacity_cmd | AO:5 | 40205 (HR) | 1/2/9 |
| economizer_enable_cmd | BO:2 | 00002 (Coil) | 1/2/10 |
| supply_pressure_sp | AV:4 | 40104 (HR) | 1/2/11 |
| unit_mode_cmd | MSV:1 | 40301 (HR) | 1/2/12 |
| supply_fan_run | BI:1 | 10001 (DI) | 1/3/1 |
| return_fan_run | BI:2 | 10002 (DI) | 1/3/2 |
| compressor1_run | BI:3 | 10003 (DI) | 1/3/3 |
| compressor2_run | BI:4 | 10004 (DI) | 1/3/4 |
| heating_active | BI:5 | 10005 (DI) | 1/3/5 |
| cooling_active | BI:6 | 10006 (DI) | 1/3/6 |
| economizer_active | BI:7 | 10007 (DI) | 1/3/7 |
| hp_alarm | BI:8 | 10008 (DI) | 1/3/8 |
| lp_alarm | BI:9 | 10009 (DI) | 1/3/9 |
| filter_dirty_alarm | BI:10 | 10010 (DI) | 1/3/10 |
| freeze_protect_active | BI:11 | 10011 (DI) | 1/3/11 |
| general_fault | BI:12 | 10012 (DI) | 1/3/12 |

**Notes sur les mappings :**
- BACnet : AI = Analog Input, AO = Analog Output, AV = Analog Value, BI = Binary Input, BO = Binary Output, MSV = Multi-State Value
- Modbus : HR = Holding Register (40001+), Coil = Digital Output (00001+), DI = Discrete Input (10001+)
- KNX : GA = Group Address (format Area/Line/Device)

## Modes de Fonctionnement

| Mode | Description | Points Actifs |
|------|-------------|---------------|
| Off | Arrêt complet | Aucun |
| Vent Only | Ventilation seule | supply_fan_run |
| Heating | Chauffage | heating_active, supply_fan_run |
| Cooling | Refroidissement | cooling_active, compressor_run, supply_fan_run |
| Economizer | Free-cooling | economizer_active, supply_fan_run |
| Auto | Automatique | Selon demande |

## Sources
- Carrier / Trane / Lennox - RTU BACnet Integration Guides
- ASHRAE Guideline 36 - High Performance Sequences of Operation
- Project Haystack - Rooftop Unit Tags
- Brick Schema - Rooftop_Unit Class
