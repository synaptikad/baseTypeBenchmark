# Points de Air Handling Unit (AHU)

## Synthèse
- **Total points mesure** : 28
- **Total points commande** : 14
- **Total points état** : 12

## Points de Mesure (Capteurs)

| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| supply_air_temp | discharge-air-temp-sensor | °C | 10-35 | 1min | Température air soufflé en sortie AHU |
| return_air_temp | return-air-temp-sensor | °C | 15-30 | 1min | Température air de retour |
| mixed_air_temp | mixed-air-temp-sensor | °C | 5-35 | 1min | Température air mélangé (extérieur + reprise) |
| outside_air_temp | outside-air-temp-sensor | °C | -30 à 45 | 1min | Température air extérieur/neuf |
| preheat_coil_leaving_temp | preheat-leaving-air-temp-sensor | °C | 5-20 | 1min | Température air sortie batterie préchauffage |
| cooling_coil_leaving_temp | cooling-leaving-air-temp-sensor | °C | 5-18 | 1min | Température air sortie batterie froid |
| heating_coil_leaving_temp | heating-leaving-air-temp-sensor | °C | 15-45 | 1min | Température air sortie batterie chaud |
| freeze_stat_temp | freezeStat-temp-sensor | °C | -5 à 10 | 30sec | Thermostat antigel protection batterie |
| supply_air_humidity | discharge-air-humidity-sensor | %RH | 20-80 | 1min | Humidité relative air soufflé |
| return_air_humidity | return-air-humidity-sensor | %RH | 20-80 | 1min | Humidité relative air de retour |
| outside_air_humidity | outside-air-humidity-sensor | %RH | 0-100 | 1min | Humidité relative air extérieur |
| supply_air_co2 | discharge-air-co2-sensor | ppm | 400-2000 | 1min | Concentration CO2 air soufflé |
| return_air_co2 | return-air-co2-sensor | ppm | 400-3000 | 1min | Concentration CO2 air de retour |
| supply_air_voc | discharge-air-voc-sensor | mg/m³ | 0-2000 | 1min | Composés organiques volatils air soufflé |
| supply_static_pressure | discharge-air-static-pressure-sensor | Pa | 0-2500 | 1min | Pression statique air soufflé dans gaines |
| return_static_pressure | return-air-static-pressure-sensor | Pa | -500 à 500 | 1min | Pression statique air de retour |
| building_static_pressure | building-static-pressure-sensor | Pa | -10 à 50 | 1min | Surpression bâtiment |
| supply_airflow | discharge-air-flow-sensor | m³/h | 1000-100000 | 1min | Débit volumique air soufflé |
| return_airflow | return-air-flow-sensor | m³/h | 1000-100000 | 1min | Débit volumique air de reprise |
| outside_airflow | outside-air-flow-sensor | m³/h | 500-50000 | 1min | Débit air neuf |
| filter_diff_pressure | filter-discharge-air-differential-pressure-sensor | Pa | 0-500 | 5min | Pression différentielle à travers filtres |
| supply_fan_speed | supply-fan-speed-sensor | Hz / RPM | 0-60 Hz / 0-1800 RPM | 1min | Vitesse réelle ventilateur soufflage |
| return_fan_speed | return-fan-speed-sensor | Hz / RPM | 0-60 Hz / 0-1800 RPM | 1min | Vitesse réelle ventilateur reprise |
| supply_fan_current | supply-fan-elec-current-sensor | A | 0-100 | 1min | Courant électrique ventilateur soufflage |
| return_fan_current | return-fan-elec-current-sensor | A | 0-100 | 1min | Courant électrique ventilateur reprise |
| supply_fan_power | supply-fan-elec-power-sensor | kW | 0-75 | 1min | Puissance électrique ventilateur soufflage |
| energy_recovery_efficiency | heatRecovery-effectiveness-sensor | % | 0-90 | 5min | Efficacité roue récupération d'énergie |
| energy_recovery_wheel_speed | heatRecovery-wheel-speed-sensor | RPM | 0-20 | 5min | Vitesse rotation roue thermique |

## Points de Commande (Actionneurs/Consignes)

| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| supply_air_temp_sp | discharge-air-temp-sp | °C | 12-28 | Consigne | Consigne température air soufflé |
| supply_air_humidity_sp | discharge-air-humidity-sp | %RH | 30-60 | Consigne | Consigne humidité relative air soufflé |
| supply_static_pressure_sp | discharge-air-static-pressure-sp | Pa | 100-1500 | Consigne | Consigne pression statique soufflage |
| min_outside_air_sp | min-outside-air-flow-sp | m³/h | 500-20000 | Consigne | Débit minimum air neuf réglementaire |
| cooling_valve_cmd | cooling-valve-cmd | % | 0-100 | Actionneur | Commande vanne eau glacée batterie froid |
| heating_valve_cmd | heating-valve-cmd | % | 0-100 | Actionneur | Commande vanne eau chaude batterie chaud |
| preheat_valve_cmd | preheat-valve-cmd | % | 0-100 | Actionneur | Commande vanne préchauffage |
| humidifier_valve_cmd | humidifier-valve-cmd | % | 0-100 | Actionneur | Commande vanne/électrovanne humidificateur |
| outside_air_damper_cmd | outside-air-damper-cmd | % | 0-100 | Actionneur | Position commande registre air neuf |
| return_air_damper_cmd | return-air-damper-cmd | % | 0-100 | Actionneur | Position commande registre air recyclé |
| exhaust_air_damper_cmd | exhaust-air-damper-cmd | % | 0-100 | Actionneur | Position commande registre air rejeté |
| supply_fan_speed_cmd | supply-fan-speed-cmd | Hz / % | 20-60 Hz / 0-100% | Actionneur | Commande vitesse VFD ventilateur soufflage |
| return_fan_speed_cmd | return-fan-speed-cmd | Hz / % | 20-60 Hz / 0-100% | Actionneur | Commande vitesse VFD ventilateur reprise |
| energy_recovery_wheel_cmd | heatRecovery-wheel-run-cmd | Boolean | ON/OFF | Actionneur | Commande marche/arrêt roue récupération |

## Points d'État

| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| supply_fan_status | supply-fan-run | Boolean | true/false | État marche/arrêt ventilateur soufflage |
| return_fan_status | return-fan-run | Boolean | true/false | État marche/arrêt ventilateur reprise |
| supply_fan_alarm | supply-fan-alarm | Boolean | true/false | Alarme défaut ventilateur soufflage |
| return_fan_alarm | return-fan-alarm | Boolean | true/false | Alarme défaut ventilateur reprise |
| filter_alarm | filter-alarm | Boolean | true/false | Alarme encrassement filtre (ΔP élevé) |
| freeze_alarm | freezeStat-alarm | Boolean | true/false | Alarme antigel activée |
| high_temp_alarm | high-temp-alarm | Boolean | true/false | Alarme haute température |
| low_temp_alarm | low-temp-alarm | Boolean | true/false | Alarme basse température |
| smoke_alarm | smoke-alarm | Boolean | true/false | Alarme détection fumée |
| ahu_enable_status | ahu-enable | Boolean | true/false | État autorisation fonctionnement AHU |
| occupancy_mode | occupancy-mode | Enum | occupied/unoccupied/bypass/standby | Mode occupation selon planning horaire |
| economizer_status | economizer-enable | Boolean | true/false | État économiseur air gratuit actif |

## Mappings Protocoles

| Point | BACnet Object | Modbus Register | KNX GA |
|-------|---------------|-----------------|--------|
| supply_air_temp | AI:1 | 40001 (HR) | 1/1/1 |
| return_air_temp | AI:2 | 40002 (HR) | 1/1/2 |
| mixed_air_temp | AI:3 | 40003 (HR) | 1/1/3 |
| outside_air_temp | AI:4 | 40004 (HR) | 1/1/4 |
| supply_air_humidity | AI:5 | 40005 (HR) | 1/1/10 |
| return_air_co2 | AI:6 | 40006 (HR) | 1/1/15 |
| supply_static_pressure | AI:7 | 40007 (HR) | 1/1/20 |
| supply_airflow | AI:8 | 40008 (HR) | 1/1/25 |
| filter_diff_pressure | AI:9 | 40009 (HR) | 1/1/30 |
| supply_fan_speed | AI:10 | 40010 (HR) | 1/1/35 |
| supply_fan_power | AI:11 | 40011 (HR) | 1/1/40 |
| supply_air_temp_sp | AV:1 | 40101 (HR) | 1/2/1 |
| supply_static_pressure_sp | AV:2 | 40102 (HR) | 1/2/2 |
| cooling_valve_cmd | AO:1 | 40201 (HR) | 1/3/1 |
| heating_valve_cmd | AO:2 | 40202 (HR) | 1/3/2 |
| outside_air_damper_cmd | AO:3 | 40203 (HR) | 1/3/3 |
| return_air_damper_cmd | AO:4 | 40204 (HR) | 1/3/4 |
| supply_fan_speed_cmd | AO:5 | 40205 (HR) | 1/3/5 |
| supply_fan_status | BI:1 | 10001 (Coil) | 1/4/1 |
| return_fan_status | BI:2 | 10002 (Coil) | 1/4/2 |
| filter_alarm | BI:3 | 10003 (Coil) | 1/4/10 |
| freeze_alarm | BI:4 | 10004 (Coil) | 1/4/11 |
| smoke_alarm | BI:5 | 10005 (Coil) | 1/4/12 |
| ahu_enable_status | BO:1 | 00001 (Coil) | 1/5/1 |
| occupancy_mode | MSV:1 | 40301 (HR) | 1/6/1 |

**Notes sur les mappings :**
- BACnet : AI = Analog Input, AO = Analog Output, AV = Analog Value, BI = Binary Input, BO = Binary Output, MSV = Multi-State Value
- Modbus : HR = Holding Register (40001+), Coil = Digital Output (00001+ et 10001+)
- KNX : GA = Group Address (format Area/Line/Device)
- Les numéros d'objets BACnet et registres Modbus sont des exemples typiques, varient selon constructeur

## Sources

- [AHUs – Project Haystack](https://project-haystack.org/doc/AHUs) - Documentation officielle Project Haystack sur le tagging des AHU
- [The Language of BACnet-Objects, Properties and Services](https://bacnet.org/wp-content/uploads/sites/4/2022/06/The-Language-of-BACnet-1.pdf) - Spécifications des objets BACnet
- [AHU Sensors | Automation Components, Inc.](https://www.workaci.com/applications/air-handling-unit) - Guide d'application des capteurs AHU
- [AHU Discharge-Air Temperature Control (PNNL)](https://buildingretuning.pnnl.gov/documents/pnnl_sa_84186.pdf) - Guide contrôle température air soufflé
- [AHU Static Pressure Control (PNNL)](https://buildingretuning.pnnl.gov/documents/pnnl_sa_84187.pdf) - Guide contrôle pression statique
- [Air-Side Economizer (PNNL)](https://buildingretuning.pnnl.gov/documents/pnnl_sa_86706.pdf) - Guide économiseur air gratuit
- [Brick: Towards a Unified Metadata Schema For Buildings](https://cseweb.ucsd.edu/~dehong/pdf/buildsys16-paper.pdf) - Schéma ontologie Brick pour bâtiments
- [Differential pressure measurement in air handling unit | Domat](https://www.domat-int.com/en/differential-pressure-measurement-in-air-handling-unit) - Mesure pression différentielle AHU
- [How to Do Filter Differential Pressure Alarming the Right Way | ACHR News](https://www.achrnews.com/articles/163608-how-to-do-filter-differential-pressure-alarming-the-right-way) - Alarmes pression différentielle filtres
- [IAQ Sensor (Indoor Air Quality Sensor): A Complete Guide](https://www.winsen-sensor.com/knowledge/iaq-sensor.html) - Guide capteurs qualité d'air intérieur
- [How Variable Frequency Drives Work in HVAC Systems - MEP Academy](https://mepacademy.com/how-variable-frequency-drives-work-in-hvac-systems/) - Fonctionnement VFD en HVAC
- [Calculate Heat Recovery Efficiency: ASHRAE 84 Tool for AHUs](https://www.conservesolution.com/blog/heat-recovery-effectiveness/) - Calcul efficacité récupération d'énergie
- [User Guide AHU Systems (Distech Controls)](https://docs-be.distech-controls.com/bundle/AHU-Systems_UG/raw/resource/enus/AHU%20Systems_UG.pdf) - Guide utilisateur systèmes AHU
