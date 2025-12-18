# Points de Variable Air Volume Box (VAV)

## Synthèse
- **Total points mesure** : 15
- **Total points commande** : 12
- **Total points état** : 8

## Points de Mesure (Capteurs)

| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| zone_air_temp | zone-air-temp-sensor | °C | 18-28 | 1min | Température zone desservie |
| discharge_air_temp | discharge-air-temp-sensor | °C | 10-30 | 1min | Température air après reheat/sortie VAV |
| inlet_air_temp | inlet-air-temp-sensor | °C | 12-18 | 1min | Température air entrant (de l'AHU) |
| zone_air_humidity | zone-air-humidity-sensor | %RH | 30-70 | 5min | Humidité relative zone |
| airflow | air-flow-sensor | m³/h | 200-5000 | 30s | Débit d'air mesuré (via DPT) |
| airflow_differential_pressure | air-flow-sensor pressure | Pa | 0-500 | 30s | Pression différentielle flow ring inlet |
| zone_co2 | zone-air-co2-sensor | ppm | 400-2000 | 2min | CO2 zone pour DCV (optionnel) |
| damper_position_feedback | damper-actuator-sensor | % | 0-100 | 1min | Position réelle registre motorisé |
| reheat_valve_position_feedback | heating-valve-sensor | % | 0-100 | 1min | Position vanne réchauffage (VAV reheat) |
| static_pressure_inlet | duct-static-pressure-sensor | Pa | 50-500 | 1min | Pression statique gaine amont |
| fan_speed_feedback | fan-speed-sensor | % | 0-100 | 1min | Vitesse ventilateur (FPV series/parallel) |
| reheat_output_power | heating-power-sensor | kW | 0-10 | 5min | Puissance électrique reheat (si électrique) |
| supply_water_temp | entering-water-temp-sensor | °C | 40-80 | 2min | Température eau chaude entrante (HW reheat) |
| return_water_temp | leaving-water-temp-sensor | °C | 30-70 | 2min | Température eau chaude sortante (HW reheat) |
| occupancy_status | zone-occ-sensor | Boolean | 0/1 | 1min | Présence zone (capteur PIR optionnel) |

## Points de Commande (Actionneurs/Consignes)

| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| zone_temp_sp | zone-air-temp-sp | °C | 18-26 | Consigne | Consigne température zone |
| zone_temp_cooling_sp | zone-air-cooling-temp-sp | °C | 22-26 | Consigne | Consigne refroidissement zone |
| zone_temp_heating_sp | zone-air-heating-temp-sp | °C | 18-22 | Consigne | Consigne chauffage zone |
| airflow_sp | air-flow-sp | m³/h | 200-5000 | Consigne | Consigne débit d'air total |
| airflow_min_sp | air-flow-min-sp | m³/h | 40-1000 | Consigne | Débit minimum (ventilation/occupé) |
| airflow_max_sp | air-flow-max-sp | m³/h | 500-5000 | Consigne | Débit maximum nominal |
| damper_cmd | damper-cmd | % | 0-100 | Actionneur | Commande ouverture registre |
| reheat_valve_cmd | heating-valve-cmd | % | 0-100 | Actionneur | Commande vanne réchauffage modulante |
| reheat_stage_cmd | heating-cmd | stage | 1-3 | Actionneur | Commande étages reheat électrique |
| fan_enable_cmd | fan-enable-cmd | Boolean | 0/1 | Actionneur | Marche/arrêt ventilateur (FPV) |
| fan_speed_cmd | fan-speed-cmd | % | 0-100 | Actionneur | Consigne vitesse ventilateur (FPV) |
| discharge_air_temp_sp | discharge-air-temp-sp | °C | 15-25 | Consigne | Consigne DAT après reheat |

## Points d'État

| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| occupancy_mode | occ-cmd | Enum | occupied/unoccupied/standby | Mode occupation zone |
| operating_mode | hvac-mode-cmd | Enum | off/cooling/heating/deadband | Mode opératoire VAV |
| damper_status | damper-cmd | Enum | open/closed/modulating | État registre |
| fan_status | fan-run-status | Boolean | on/off | État marche ventilateur (FPV) |
| alarm_low_airflow | air-flow-sensor alarm | Boolean | normal/alarm | Alarme débit insuffisant |
| alarm_high_temp | zone-air-temp-sensor alarm | Boolean | normal/alarm | Alarme température zone élevée |
| alarm_sensor_fault | sensor fault | Boolean | normal/fault | Défaut capteur (DPT, température) |
| comm_status | communication-status | Enum | online/offline/fault | État communication BACnet/Modbus |

## Mappings Protocoles

| Point | BACnet Object | Modbus Register | KNX GA |
|-------|---------------|-----------------|--------|
| zone_air_temp | AI:1 | 40001 (IR) | 1/1/1 (DPT 9.001) |
| zone_temp_sp | AV:1 | 40002 (IR) | 1/1/2 (DPT 9.001) |
| airflow | AI:2 | 40003 (IR) | 1/2/1 (DPT 9.009) |
| airflow_sp | AV:2 | 40004 (IR) | 1/2/2 (DPT 9.009) |
| damper_position_feedback | AI:3 | 40005 (IR) | 1/3/1 (DPT 5.001) |
| damper_cmd | AO:1 | 40101 (HR) | 1/3/2 (DPT 5.001) |
| discharge_air_temp | AI:4 | 40006 (IR) | 1/1/3 (DPT 9.001) |
| reheat_valve_position_feedback | AI:5 | 40007 (IR) | 1/4/1 (DPT 5.001) |
| reheat_valve_cmd | AO:2 | 40102 (HR) | 1/4/2 (DPT 5.001) |
| zone_co2 | AI:6 | 40008 (IR) | 1/5/1 (DPT 9.008) |
| occupancy_status | BI:1 | 10001 (DI) | 1/6/1 (DPT 1.001) |
| occupancy_mode | BV:1 | 40201 (HR) | 1/6/2 (DPT 20.102) |
| fan_status | BI:2 | 10002 (DI) | 1/7/1 (DPT 1.001) |
| fan_enable_cmd | BO:1 | 00001 (Coil) | 1/7/2 (DPT 1.001) |
| alarm_low_airflow | BI:3 | 10003 (DI) | 1/8/1 (DPT 1.005) |
| alarm_sensor_fault | BI:4 | 10004 (DI) | 1/8/2 (DPT 1.005) |
| comm_status | BV:2 | 40202 (HR) | 1/9/1 (DPT 20.011) |

**Notes Protocoles :**
- **BACnet** : AI=Analog Input, AO=Analog Output, BI=Binary Input, BO=Binary Output, AV=Analog Value, BV=Binary Value
- **Modbus** : IR=Input Register (4xxxx), HR=Holding Register (4xxxx), DI=Discrete Input (1xxxx), Coil (0xxxx)
- **KNX** : DPT 9.001=Temperature, DPT 9.009=Airflow, DPT 5.001=Percentage, DPT 1.001=Boolean, DPT 9.008=PPM, DPT 20.102=HVAC Mode

## Sources

### Documentation Technique
- [Project Haystack - VAVs Documentation](https://project-haystack.org/doc/docHaystack/VAVs) - Spécifications officielles tags Haystack pour terminaux VAV
- [Brick Schema - VAV Class](https://brick.andrew.cmu.edu/ontology/1.1/classes/VAV/) - Ontologie Brick pour modélisation VAV
- [MEP Academy - How VAV Box DDC Controllers Work](https://mepacademy.com/how-vav-box-ddc-controllers-work/) - Guide fonctionnement contrôleurs DDC VAV

### Standards et Guidelines
- [PNNL - Variable Air Volume Systems O&M](https://www.pnnl.gov/projects/om-best-practices/variable-air-volume-systems) - Best practices opération et maintenance VAV
- [FSU - Sequence of Operation Guideline VAV Box With Reheat](https://www.facilities.fsu.edu/depts/designConstr/2011%20Control%20Standards/Controls/IC-16/IC-16%20VAV%20Box%20With%20Reheat.pdf) - Séquences contrôle standard VAV reheat
- [ASHRAE Journal - Demand Control Ventilation Using CO2](https://www.krueger-hvac.com/files/white%20papers/article_demand_control_ventilation.pdf) - Guide DCV avec CO2

### Protocoles et Intégration
- [BACnet - The Language of BACnet Objects, Properties and Services](https://bacnet.org/wp-content/uploads/sites/4/2022/06/The-Language-of-BACnet-1.pdf) - Spécifications objets BACnet (AI, AO, BI, BO, AV, BV)
- [Belimo - Modbus Register ZoneEase VAV](https://www.belimo.com/mam/general-documents/system_integration/Modbus/belimo_Modbus-Register_ZoneEase-VAV_V1_7_en-gb.pdf) - Registres Modbus détaillés contrôleur VAV
- [KNX Association - Datapoint Types](https://support.knx.org/hc/en-us/articles/115001133744-Datapoint-Type) - Types de données KNX pour HVAC

### Constructeurs et Applications
- [Johnson Controls - VAV Terminal Control Applications](https://docs.johnsoncontrols.com/bas/api/khub/documents/7P5eJSg3kyQBhl9W2JgkPA/content) - Applications terminaux VAV et points de contrôle
- [75F Support - VAV w/ Reheat (No Fan)](https://support.75f.io/hc/en-us/articles/360047633293-VAV-w-Reheat-No-Fan) - Configuration points VAV reheat sans ventilateur
- [Price Industries - The Definitive Guide to VAV Selection](https://www.priceindustries.com/content/documents/the%20definitive%20guide%20to%20vav%20selection.pdf) - Guide sélection et spécifications techniques VAV

### Fault Detection & Diagnostics
- [ScienceDirect - Sensor Fault Detection and Validation of VAV Terminals](https://www.sciencedirect.com/science/article/abs/pii/S0196890404003085) - Détection défauts capteurs VAV
- [Trane Support - Flow Sensor Failure Troubleshooting](https://support.trane.com/hc/en-us/articles/16077694845069-Flow-sensor-failure-Pressure-transducer-troubleshooting) - Diagnostic défaillances capteurs débit
