# Points de Chiller

## Synthèse
- **Total points mesure** : 28
- **Total points commande** : 12
- **Total points état** : 18
- **Total général** : 58

## Points de Mesure (Capteurs)

| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| chw_supply_temp | leaving-chilled-water-temp-sensor | °C | 4-12 | 30s | Température eau glacée départ (sortie évaporateur) |
| chw_return_temp | entering-chilled-water-temp-sensor | °C | 10-18 | 30s | Température eau glacée retour (entrée évaporateur) |
| chw_flow | chilled-water-flow-sensor | m³/h | 50-1000 | 60s | Débit d'eau glacée circuit évaporateur |
| chw_delta_temp | chilled-water-delta-temp-sensor | K | 4-12 | 60s | Delta T eau glacée (retour - départ) |
| chw_diff_pressure | chilled-water-differential-pressure-sensor | kPa | 50-250 | 60s | Pression différentielle évaporateur |
| cw_supply_temp | leaving-condenser-water-temp-sensor | °C | 25-40 | 30s | Température eau condenseur départ (sortie condenseur) |
| cw_return_temp | entering-condenser-water-temp-sensor | °C | 20-35 | 30s | Température eau condenseur retour (entrée condenseur) |
| cw_flow | condenser-water-flow-sensor | m³/h | 60-1200 | 60s | Débit d'eau circuit condenseur |
| cw_delta_temp | condenser-water-delta-temp-sensor | K | 4-8 | 60s | Delta T eau condenseur (départ - retour) |
| cw_diff_pressure | condenser-water-differential-pressure-sensor | kPa | 50-200 | 60s | Pression différentielle condenseur |
| evap_sat_temp | evaporator-refrigerant-temp-sensor | °C | 2-10 | 30s | Température saturation réfrigérant évaporateur |
| evap_sat_pressure | evaporator-refrigerant-pressure-sensor | kPa | 300-600 | 30s | Pression saturation réfrigérant évaporateur |
| evap_approach_temp | evaporator-approach-temp-sensor | K | 0-5 | 60s | Approche évaporateur (Leaving CHW - Evap Sat) |
| cond_sat_temp | condenser-refrigerant-temp-sensor | °C | 30-50 | 30s | Température saturation réfrigérant condenseur |
| cond_sat_pressure | condenser-refrigerant-pressure-sensor | kPa | 1200-2000 | 30s | Pression saturation réfrigérant condenseur |
| cond_approach_temp | condenser-approach-temp-sensor | K | 0.5-3 | 60s | Approche condenseur (Cond Sat - Leaving CW) |
| refrigerant_subcooling | refrigerant-subcooling-sensor | K | 2-8 | 60s | Sous-refroidissement liquide frigorigène |
| refrigerant_superheat | refrigerant-superheat-sensor | K | 3-10 | 60s | Surchauffe vapeur aspiration compresseur |
| refrigerant_level | refrigerant-level-sensor | % | 0-100 | 300s | Niveau réfrigérant réservoir/évaporateur |
| oil_pressure | oil-pressure-sensor | kPa | 200-600 | 30s | Pression huile lubrification compresseur |
| oil_temp | oil-temp-sensor | °C | 40-80 | 60s | Température huile compresseur |
| oil_differential_pressure | oil-filter-differential-pressure-sensor | kPa | 5-35 | 60s | Pression différentielle filtre à huile |
| power_input | elec-power-sensor | kW | 20-1500 | 30s | Puissance électrique totale consommée |
| current | elec-current-sensor | A | 50-2000 | 30s | Courant électrique total |
| cooling_capacity | cooling-capacity-sensor | kW | 100-5000 | 60s | Puissance frigorifique fournie (calculée) |
| cop | efficiency-sensor | - | 2.5-7.0 | 60s | COP instantané (kW frigo / kW élec) |
| kw_per_ton | efficiency-sensor | kW/TR | 0.45-1.2 | 60s | Efficacité kW/ton (0.45-0.64 water-cooled) |
| operating_hours | run-time-sensor | h | 0-100000 | 3600s | Heures de fonctionnement cumulées |

## Points de Commande (Actionneurs/Consignes)

| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| chw_supply_temp_sp | leaving-chilled-water-temp-sp | °C | 5-10 | Consigne | Consigne température eau glacée départ |
| chw_supply_temp_reset_enable | reset-cmd | - | 0/1 | Commande | Activation reset température eau glacée |
| capacity_setpoint | capacity-sp | % | 0-100 | Consigne | Consigne capacité frigorifique % |
| capacity_limit | capacity-limit-sp | % | 0-100 | Consigne | Limite maximale capacité (demand limit) |
| slide_valve_cmd | valve-cmd | % | 20-100 | Commande | Position vanne coulissante (screw chiller) |
| inlet_vane_cmd | damper-cmd | % | 0-100 | Commande | Position clapets admission (centrifugal) |
| compressor_speed_sp | speed-sp | % | 20-100 | Consigne | Consigne vitesse compresseur VFD |
| chiller_start_cmd | start-cmd | - | 0/1 | Commande | Démarrage chiller |
| chiller_stop_cmd | stop-cmd | - | 0/1 | Commande | Arrêt chiller |
| emergency_stop | emergency-stop-cmd | - | 0/1 | Commande | Arrêt d'urgence |
| ice_detection_enable | ice-detection-enable-cmd | - | 0/1 | Commande | Activation détection givrage évaporateur |
| remote_reset | remote-reset-cmd | - | 0/1 | Commande | Réarmement alarmes à distance |

## Points d'État

| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| chiller_status | run | Boolean | on/off | État marche/arrêt chiller |
| chiller_enable | enable | Boolean | enabled/disabled | Chiller autorisé/désactivé |
| chiller_fault | fault | Boolean | fault/normal | Défaut général chiller |
| compressor_status | compressor-run | Boolean | on/off | État compresseur principal |
| compressor_stage_1 | compressor-stage-1-status | Boolean | on/off | État compresseur étage 1 (multi-comp) |
| compressor_stage_2 | compressor-stage-2-status | Boolean | on/off | État compresseur étage 2 (multi-comp) |
| compressor_stage_3 | compressor-stage-3-status | Boolean | on/off | État compresseur étage 3 (multi-comp) |
| compressor_stage_4 | compressor-stage-4-status | Boolean | on/off | État compresseur étage 4 (multi-comp) |
| operating_mode | mode | Enum | cooling/off/standby/test | Mode opératoire actuel |
| capacity_percent | capacity | Analog | 0-100% | Capacité actuelle en % |
| alarm_high_pressure | high-pressure-alarm | Boolean | alarm/normal | Alarme haute pression condenseur |
| alarm_low_pressure | low-pressure-alarm | Boolean | alarm/normal | Alarme basse pression évaporateur |
| alarm_oil_pressure | oil-pressure-alarm | Boolean | alarm/normal | Alarme pression huile insuffisante |
| alarm_oil_filter | oil-filter-alarm | Boolean | alarm/normal | Alarme filtre huile colmaté |
| alarm_freezestat | freezestat-alarm | Boolean | alarm/normal | Alarme antigel/givrage évaporateur |
| alarm_flow_evap | evaporator-flow-alarm | Boolean | alarm/normal | Alarme débit insuffisant évaporateur |
| alarm_flow_cond | condenser-flow-alarm | Boolean | alarm/normal | Alarme débit insuffisant condenseur |
| vfd_fault | vfd-fault | Boolean | fault/normal | Défaut variateur de vitesse |

## Mappings Protocoles

| Point | BACnet Object | Modbus Register | KNX GA |
|-------|---------------|-----------------|--------|
| chw_supply_temp | AI:1 | 40001 (Input Reg) | 1/2/1 |
| chw_return_temp | AI:2 | 40002 | 1/2/2 |
| chw_flow | AI:3 | 40003 | 1/2/3 |
| chw_delta_temp | AV:1 | 40004 | 1/2/4 |
| chw_diff_pressure | AI:4 | 40005 | 1/2/5 |
| cw_supply_temp | AI:5 | 40006 | 1/2/6 |
| cw_return_temp | AI:6 | 40007 | 1/2/7 |
| cw_flow | AI:7 | 40008 | 1/2/8 |
| evap_sat_temp | AI:8 | 40009 | 1/2/9 |
| evap_sat_pressure | AI:9 | 40010 | 1/2/10 |
| cond_sat_temp | AI:10 | 40011 | 1/2/11 |
| cond_sat_pressure | AI:11 | 40012 | 1/2/12 |
| evap_approach_temp | AV:2 | 40013 | 1/2/13 |
| cond_approach_temp | AV:3 | 40014 | 1/2/14 |
| refrigerant_subcooling | AV:4 | 40015 | 1/2/15 |
| refrigerant_superheat | AV:5 | 40016 | 1/2/16 |
| refrigerant_level | AI:12 | 40017 | 1/2/17 |
| oil_pressure | AI:13 | 40018 | 1/2/18 |
| oil_temp | AI:14 | 40019 | 1/2/19 |
| oil_differential_pressure | AI:15 | 40020 | 1/2/20 |
| power_input | AI:16 | 40021 | 1/2/21 |
| current | AI:17 | 40022 | 1/2/22 |
| cooling_capacity | AV:6 | 40023 | 1/2/23 |
| cop | AV:7 | 40024 | 1/2/24 |
| kw_per_ton | AV:8 | 40025 | 1/2/25 |
| operating_hours | AV:9 | 40026 | 1/2/26 |
| chw_supply_temp_sp | AV:10 | 40101 (Holding Reg) | 1/3/1 |
| chw_supply_temp_reset_enable | BV:1 | 00101 (Coil) | 1/3/2 |
| capacity_setpoint | AV:11 | 40102 | 1/3/3 |
| capacity_limit | AV:12 | 40103 | 1/3/4 |
| slide_valve_cmd | AO:1 | 40104 | 1/3/5 |
| inlet_vane_cmd | AO:2 | 40105 | 1/3/6 |
| compressor_speed_sp | AV:13 | 40106 | 1/3/7 |
| chiller_start_cmd | BV:2 | 00102 | 1/3/8 |
| chiller_stop_cmd | BV:3 | 00103 | 1/3/9 |
| emergency_stop | BV:4 | 00104 | 1/3/10 |
| ice_detection_enable | BV:5 | 00105 | 1/3/11 |
| remote_reset | BV:6 | 00106 | 1/3/12 |
| chiller_status | BI:1 | 10001 (Discrete In) | 1/4/1 |
| chiller_enable | BI:2 | 10002 | 1/4/2 |
| chiller_fault | BI:3 | 10003 | 1/4/3 |
| compressor_status | BI:4 | 10004 | 1/4/4 |
| compressor_stage_1 | BI:5 | 10005 | 1/4/5 |
| compressor_stage_2 | BI:6 | 10006 | 1/4/6 |
| compressor_stage_3 | BI:7 | 10007 | 1/4/7 |
| compressor_stage_4 | BI:8 | 10008 | 1/4/8 |
| operating_mode | MSV:1 | 40201 | 1/4/9 |
| capacity_percent | AI:18 | 40027 | 1/4/10 |
| alarm_high_pressure | BI:9 | 10009 | 1/4/11 |
| alarm_low_pressure | BI:10 | 10010 | 1/4/12 |
| alarm_oil_pressure | BI:11 | 10011 | 1/4/13 |
| alarm_oil_filter | BI:12 | 10012 | 1/4/14 |
| alarm_freezestat | BI:13 | 10013 | 1/4/15 |
| alarm_flow_evap | BI:14 | 10014 | 1/4/16 |
| alarm_flow_cond | BI:15 | 10015 | 1/4/17 |
| vfd_fault | BI:16 | 10016 | 1/4/18 |

## Sources

- [Daikin MicroTech III Chiller Unit Controller BACnet Protocol](https://oslo.daikinapplied.com/api/sharepoint/getdocument/Doc100/Daikin_ED_15120-7_LR_MTIII_Unit_Controller_LonWorks-BACnet_Tech_Sheet.pdf/)
- [Daikin MicroTech II BACnet IP Technical Sheet](https://tahoeweb.daikinapplied.com/api/general/DownloadDocumentByName/media/Daikin_ED_15100-5_MTII_Chiller_Unit%20Control_BACnet%20IP_Ethernet_Tech_Sheet.pdf/)
- [Daikin EWYT-B BAS Integration Guide BACnet](https://www.daikin-kosova.com/content/dam/document-library/installation-manuals/EWYT-B-(SL.SR.SS.XL.XR.XS.)_BAS%20Integration%20Guide%20BACNet_D-EIGOC00107-23_01_English.pdf)
- [Project Haystack - Tagging Chilled Water System](https://project-haystack.org/forum/topic/839)
- [Project Haystack - Let's Tackle Chiller Plants](https://project-haystack.org/forum/topic/127)
- [BrickSchema - Chiller Plant Modeling Issue #197](https://github.com/BrickSchema/Brick/issues/197)
- [Chiller Efficiency Calculation kW/ton COP EER - AirCondLounge](https://aircondlounge.com/chiller-efficiency-calculation-kw-ton-cop-eer-iplv-nplv/)
- [The Engineering Mindset - Water Cooled Chiller Design Data](https://theengineeringmindset.com/water-cooled-chiller-design-data/)
- [Chiller Systems Parameters Controls - SkillCat](https://www.skillcatapp.com/post/chillersystems-parameters-controls-andmore)
- [Chiller Capacity Control - Processing Magazine](https://www.processingmagazine.com/process-control-automation/heating-cooling/article/21252595/chiller-capacity-control)
- [The Engineering Mindset - Chiller Fault Finding](https://theengineeringmindset.com/chiller-fault-troubleshooting/)
- [CopperTree Analytics - Calculate kW/ton and COP for Water Cooled Chillers](https://support.coppertreeanalytics.com/knowledge-base/kaizen/legacy-rules/calculate-kw-ton-and-coefficient-of-performance-for-water-cooled-chillers-uses-deg-f-temperature-tls/)
- [Carrier BACnet/Modbus Translator Documentation](https://www.shareddocs.com/hvac/docs/1000/Public/01/808-356.pdf)
- [Optigo Networks - BACnet, LonWorks, Modbus, or KNX](https://www.optigo.net/which-better-bacnet-lonworks-modbus-or-knx/)
- [HVAC School - Saturation and Pressure-Temperature Relationship](http://www.hvacrschool.com/saturation-and-the-pressure-temperature-relationship/)
- [Consulting Specifying Engineer - Understanding Chilled Water Plant Performance](https://www.csemag.com/articles/understanding-chilled-water-plant-performance/)
- [Consulting Specifying Engineer - Control Sequences for Chilled Water Systems](https://www.csemag.com/articles/control-sequences-for-chilled-water-systems/)
