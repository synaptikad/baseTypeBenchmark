# Points de Heat Pump

## Synthèse
- **Total points mesure** : 28
- **Total points commande** : 12
- **Total points état** : 15

## Points de Mesure (Capteurs)

| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| leaving_water_temp | leaving-water-temp-sensor | °C | 5-70 | 30s | Température eau départ (sortie PAC) |
| entering_water_temp | entering-water-temp-sensor | °C | 0-65 | 30s | Température eau retour (entrée PAC) |
| outdoor_air_temp | outside-air-temp-sensor | °C | -25-45 | 60s | Température air extérieur (source air) |
| source_entering_temp | entering-source-temp-sensor | °C | -10-35 | 30s | Température entrée source (air/eau/sol) |
| source_leaving_temp | leaving-source-temp-sensor | °C | -15-30 | 30s | Température sortie source |
| hot_gas_temp | hot-gas-temp-sensor | °C | 40-120 | 30s | Température gaz chaud (refoulement compresseur) |
| suction_temp | suction-temp-sensor | °C | -20-30 | 30s | Température aspiration compresseur |
| liquid_line_temp | liquid-line-temp-sensor | °C | 0-60 | 30s | Température ligne liquide (avant détendeur) |
| evaporating_temp | evaporating-temp-sensor | °C | -30-20 | 30s | Température évaporation (calculée ou mesurée) |
| condensing_temp | condensing-temp-sensor | °C | 20-80 | 30s | Température condensation |
| discharge_pressure | discharge-pressure-sensor | bar | 5-35 | 30s | Pression refoulement (haute pression) |
| suction_pressure | suction-pressure-sensor | bar | 1-12 | 30s | Pression aspiration (basse pression) |
| water_flow_rate | water-flow-sensor | L/min | 10-500 | 30s | Débit eau circuit hydraulique |
| superheat | superheat-sensor | K | 3-15 | 60s | Surchauffe (superheat) évaporateur |
| subcooling | subcooling-sensor | K | 3-10 | 60s | Sous-refroidissement (subcooling) condenseur |
| power_input | elec-power-sensor | kW | 2-300 | 10s | Puissance électrique consommée |
| energy_input | elec-energy-sensor | kWh | 0-∞ | 300s | Énergie électrique cumulée |
| thermal_power_output | thermal-power-sensor | kW | 5-1000 | 30s | Puissance thermique produite (calculée) |
| thermal_energy_output | thermal-energy-sensor | kWh | 0-∞ | 300s | Énergie thermique cumulée |
| cop_realtime | cop-sensor | - | 1.5-6.0 | 60s | COP instantané (thermique/électrique) |
| scop_cumulative | scop-sensor | - | 2.0-5.5 | 3600s | SCOP saisonnier (cumulé) |
| compressor_speed | compressor-speed-sensor | % | 0-100 | 30s | Vitesse compresseur (inverter) |
| compressor_speed_rpm | compressor-speed-sensor | rpm | 0-8000 | 30s | Vitesse compresseur en tours/min |
| fan_speed | fan-speed-sensor | % | 0-100 | 30s | Vitesse ventilateur condenseur/évaporateur |
| expansion_valve_opening | valve-position-sensor | % | 0-100 | 30s | Ouverture détendeur électronique (EEV) |
| operating_hours_total | run-time-sensor | h | 0-∞ | 3600s | Heures de fonctionnement totales |
| operating_hours_heating | heating-run-time-sensor | h | 0-∞ | 3600s | Heures fonctionnement mode chauffage |
| operating_hours_cooling | cooling-run-time-sensor | h | 0-∞ | 3600s | Heures fonctionnement mode refroidissement |

## Points de Commande (Actionneurs/Consignes)

| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| leaving_water_temp_sp | leaving-water-temp-sp | °C | 7-65 | Consigne | Consigne température eau départ |
| enable_cmd | enable-cmd | - | on/off | Commande | Commande marche/arrêt PAC |
| mode_cmd | mode-cmd | - | heating/cooling/auto | Commande | Commande mode opératoire |
| compressor_speed_cmd | compressor-speed-cmd | % | 0-100 | Consigne | Consigne vitesse compresseur (inverter) |
| fan_speed_cmd | fan-speed-cmd | % | 0-100 | Consigne | Consigne vitesse ventilateur |
| defrost_cmd | defrost-cmd | - | enable/disable | Commande | Déclenchement dégivrage manuel |
| reset_alarm_cmd | reset-cmd | - | trigger | Commande | Réinitialisation alarmes |
| heating_curve_slope | heating-curve-slope-sp | - | 0.2-3.0 | Paramètre | Pente loi d'eau chauffage |
| heating_curve_offset | heating-curve-offset-sp | °C | -10-10 | Paramètre | Décalage loi d'eau |
| dhw_priority_cmd | dhw-priority-cmd | - | enable/disable | Commande | Priorité eau chaude sanitaire |
| sg_ready_input_1 | sg-ready-input-1-cmd | - | on/off | Commande | Interface SG Ready - Input 1 (blocage EVU) |
| sg_ready_input_2 | sg-ready-input-2-cmd | - | on/off | Commande | Interface SG Ready - Input 2 (mode forcé) |

## Points d'État

| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| heatpump_status | run-status | Boolean | on/off | État marche générale PAC |
| operating_mode | mode-status | Enum | heating/cooling/auto/standby | Mode opératoire actif |
| compressor_status | compressor-run-status | Boolean | on/off | État marche compresseur |
| reversing_valve_status | reversing-valve-status | Boolean | heating/cooling | Position vanne 4 voies (réversible) |
| defrost_status | defrost-status | Boolean | active/inactive | État dégivrage en cours |
| water_pump_status | water-pump-run-status | Boolean | on/off | État pompe circuit hydraulique |
| fan_status | fan-run-status | Boolean | on/off | État ventilateur condenseur/évaporateur |
| alarm_general | alarm-status | Boolean | alarm/normal | Alarme générale présente |
| high_pressure_alarm | high-pressure-alarm | Boolean | alarm/normal | Alarme haute pression |
| low_pressure_alarm | low-pressure-alarm | Boolean | alarm/normal | Alarme basse pression |
| flow_alarm | flow-alarm | Boolean | alarm/normal | Alarme débit insuffisant |
| antifreeze_alarm | antifreeze-alarm | Boolean | alarm/normal | Alarme protection antigel |
| sensor_fault_alarm | sensor-fault-alarm | Boolean | alarm/normal | Alarme défaut capteur |
| maintenance_required | maintenance-required-status | Boolean | required/ok | Maintenance nécessaire (heures/filtre) |
| performance_degraded | performance-alarm | Boolean | alarm/normal | Alerte performance dégradée |

## Mappings Protocoles

| Point | BACnet Object | Modbus Register | KNX GA |
|-------|---------------|-----------------|--------|
| leaving_water_temp | AI:1 | 40001 (float) | 1/1/1 (DPT 9.001) |
| entering_water_temp | AI:2 | 40003 (float) | 1/1/2 (DPT 9.001) |
| outdoor_air_temp | AI:3 | 40005 (float) | 1/1/3 (DPT 9.001) |
| discharge_pressure | AI:10 | 40019 (float) | 1/2/1 (DPT 9.006) |
| suction_pressure | AI:11 | 40021 (float) | 1/2/2 (DPT 9.006) |
| water_flow_rate | AI:12 | 40023 (float) | 1/3/1 (DPT 9.025) |
| power_input | AI:15 | 40029 (float) | 1/4/1 (DPT 9.024) |
| thermal_power_output | AI:16 | 40031 (float) | 1/4/2 (DPT 9.024) |
| cop_realtime | AI:20 | 40039 (float) | 1/5/1 (DPT 9.xxx) |
| compressor_speed | AI:22 | 40043 (uint16) | 1/6/1 (DPT 5.001) |
| expansion_valve_opening | AI:25 | 40049 (uint16) | 1/6/2 (DPT 5.001) |
| leaving_water_temp_sp | AV:1 | 40101 (float) | 2/1/1 (DPT 9.001) |
| enable_cmd | BO:1 | 00001 (coil) | 3/1/1 (DPT 1.001) |
| mode_cmd | MV:1 | 40201 (uint16) | 3/2/1 (DPT 20.105) |
| compressor_speed_cmd | AO:1 | 40301 (uint16) | 3/3/1 (DPT 5.001) |
| defrost_cmd | BO:5 | 00005 (coil) | 3/4/1 (DPT 1.001) |
| heatpump_status | BI:1 | 10001 (discrete) | 4/1/1 (DPT 1.001) |
| operating_mode | MV:10 | 30001 (uint16) | 4/2/1 (DPT 20.105) |
| compressor_status | BI:2 | 10002 (discrete) | 4/3/1 (DPT 1.001) |
| defrost_status | BI:5 | 10005 (discrete) | 4/4/1 (DPT 1.001) |
| alarm_general | BI:20 | 10020 (discrete) | 5/1/1 (DPT 1.005) |
| high_pressure_alarm | BI:21 | 10021 (discrete) | 5/1/2 (DPT 1.005) |
| low_pressure_alarm | BI:22 | 10022 (discrete) | 5/1/3 (DPT 1.005) |
| flow_alarm | BI:23 | 10023 (discrete) | 5/1/4 (DPT 1.005) |
| maintenance_required | BI:30 | 10030 (discrete) | 5/2/1 (DPT 1.005) |

## Sources

- [Daikin EWYT-B BAS Integration Guide BACnet](https://www.daikin.eu/content/dam/document-library/installation-manuals/EWYT-B-(SL.SR.SS.XL.XR.XS.)_BAS%20Integration%20Guide%20BACNet_D-EIGOC00107-23_01_English.pdf)
- [Heat Pump Monitoring - OpenEnergyMonitor Documentation](https://docs.openenergymonitor.org/applications/heatpump.html)
- [Project Haystack - Unitary Equipment Working Group](https://project-haystack.org/forum/topic/506)
- [Brick Schema - Modeling an Air Source Heat Pump](https://groups.google.com/g/brickschema/c/XXwlCe2lVlQ)
- [Gree Versati Modbus Protocol V1.5](https://man.kievclimate.com/man/Gree/Versati/Versati%20III/R32_Versati%20Modbus%20V1.5.pdf)
- [TE Connectivity - Sensors for Heat Pumps](https://www.te.com/en/industries/intelligent-buildings-smart-cities/applications/sensors-for-hvac/heat-pumps.html)
- [Sensata - Temperature Sensors in Heat Pump Applications](https://www.sensata.com/sites/default/files/a/sensata-temperature-sensors-heat-pump-appnote.pdf)
- [KNX Association - Heating, Cooling, Ventilation with KNX](https://www.knx.org/knx-en/Microsites/docs/brochure_en.pdf)
- [Schneider Electric Blog - COP Calculation and Monitoring in HVAC Applications](https://blog.se.com/industry/machine-and-process-management/2016/04/13/cop-calculation-monitoring-hvac-application/)
- [NIST - Fault Detection and Diagnostics for Air-Conditioners and Heat Pumps](https://www.nist.gov/programs-projects/fault-detection-and-diagnostics-air-conditioners-and-heat-pumps)
