# Points de Boiler

## Synthèse
- **Total points mesure** : 28
- **Total points commande** : 9
- **Total points état** : 12

## Points de Mesure (Capteurs)

| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| hw_supply_temp | leaving-hot-water-temp-sensor | °C | 40-95 | 30s | Température eau chaude départ vers réseau |
| hw_return_temp | entering-hot-water-temp-sensor | °C | 35-85 | 30s | Température eau chaude retour du réseau |
| hw_delta_temp | hot-water-delta-temp-sensor | °C | 5-25 | 30s | Delta température départ-retour (ΔT) |
| hw_supply_pressure | leaving-hot-water-pressure-sensor | bar | 1-6 | 1min | Pression eau chaude départ |
| hw_return_pressure | entering-hot-water-pressure-sensor | bar | 0.8-5.5 | 1min | Pression eau chaude retour |
| hw_delta_pressure | hot-water-delta-pressure-sensor | bar | 0.1-1.5 | 1min | Pression différentielle circuit hydraulique |
| hw_flow | leaving-hot-water-flow-sensor | m³/h | 5-200 | 30s | Débit eau chaude départ |
| hw_return_flow | entering-hot-water-flow-sensor | m³/h | 5-200 | 1min | Débit eau chaude retour (vérification) |
| thermal_power | thermal-power-sensor | kW | 50-10000 | 1min | Puissance thermique instantanée fournie |
| thermal_energy | thermal-energy-sensor | kWh | - | 15min | Énergie thermique cumulée produite |
| flue_gas_temp | exhaust-air-temp-sensor | °C | 80-250 | 1min | Température fumées sortie chaudière |
| combustion_o2 | o2-sensor | % | 2-8 | 30s | Teneur oxygène dans fumées (efficacité combustion) |
| combustion_co | co-sensor | ppm | 0-200 | 30s | Teneur monoxyde de carbone dans fumées (sécurité) |
| combustion_efficiency | efficiency-sensor | % | 85-98 | 5min | Rendement combustion calculé |
| fuel_flow | fuel-flow-sensor | m³/h ou kg/h | 5-500 | 1min | Débit combustible (gaz, fioul) instantané |
| fuel_consumption | fuel-consumption-sensor | m³ ou L | - | 15min | Consommation combustible cumulée |
| fuel_pressure | fuel-pressure-sensor | mbar | 15-25 | 1min | Pression alimentation gaz naturel |
| combustion_air_temp | outside-air-temp-sensor | °C | -20-40 | 5min | Température air de combustion |
| water_level | water-level-sensor | % | 30-90 | 30s | Niveau d'eau dans corps de chauffe |
| boiler_body_temp | boiler-temp-sensor | °C | 45-95 | 1min | Température corps de chaudière |
| condensate_return_temp | condensate-temp-sensor | °C | 30-70 | 5min | Température condensats retour (si vapeur) |
| makeup_water_flow | makeup-water-flow-sensor | L/h | 0-100 | 5min | Débit eau appoint circuit |
| burner_runtime | run-sensor | h | - | 1h | Heures fonctionnement brûleur cumulées |
| burner_starts | starts-sensor | - | - | event | Nombre démarrages brûleur (usure) |
| burner_modulation | modulation-sensor | % | 0-100 | 30s | Taux modulation brûleur (charge actuelle) |
| pump_speed | speed-sensor | % ou rpm | 0-100 | 1min | Vitesse pompe primaire (si VFD) |
| pump_power | elec-power-sensor | kW | 0.5-50 | 1min | Puissance électrique pompe circulation |
| total_elec_power | elec-power-sensor | kW | 1-100 | 1min | Puissance électrique totale équipement |

## Points de Commande (Actionneurs/Consignes)

| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| hw_supply_temp_sp | leaving-hot-water-temp-sp | °C | 60-85 | Consigne | Consigne température départ eau chaude |
| enable_cmd | enable-cmd | - | 0/1 | Commande | Activation/arrêt chaudière (ON/OFF) |
| burner_enable_cmd | burner-enable-cmd | - | 0/1 | Commande | Activation brûleur (sécurité) |
| burner_modulation_cmd | modulation-cmd | % | 0-100 | Commande | Consigne modulation brûleur (charge) |
| pump_enable_cmd | pump-enable-cmd | - | 0/1 | Commande | Activation pompe primaire circulation |
| pump_speed_cmd | speed-cmd | % | 30-100 | Commande | Consigne vitesse pompe (si VFD) |
| reset_alarm_cmd | reset-cmd | - | pulse | Commande | Réarmement défauts réinitialisables |
| lead_lag_mode_cmd | mode-cmd | - | 0/1/2 | Consigne | Mode séquencement (Lead/Lag/Standby) |
| operating_mode_cmd | mode-cmd | - | 0/1/2/3 | Consigne | Mode fonctionnement (Off/Manual/Auto/Cascade) |

## Points d'État

| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| boiler_status | run | Boolean | on/off | État marche chaudière globale |
| burner_status | burner-run | Boolean | on/off | État fonctionnement brûleur |
| flame_status | flame | Boolean | detected/lost | Détection flamme brûleur (sécurité) |
| pump_status | pump-run | Boolean | on/off | État pompe primaire circulation |
| fault_status | fault | Boolean | fault/ok | Défaut actif présent |
| alarm_status | alarm | Boolean | alarm/ok | Alarme active présente |
| lockout_status | lockout | Boolean | locked/ok | Verrouillage sécurité (nécessite reset) |
| low_water_alarm | low-water-alarm | Boolean | alarm/ok | Alarme niveau eau bas (LWCO) |
| high_limit_alarm | high-limit-alarm | Boolean | alarm/ok | Alarme haute limite température/pression |
| flame_failure_alarm | flame-failure-alarm | Boolean | alarm/ok | Alarme perte flamme brûleur |
| fuel_pressure_alarm | fuel-pressure-alarm | Boolean | alarm/ok | Alarme pression gaz insuffisante |
| operating_mode | operating-mode | Enum | off/manual/auto/cascade | Mode opératoire actuel |

## Mappings Protocoles

| Point | BACnet Object | Modbus Register | KNX GA |
|-------|---------------|-----------------|--------|
| hw_supply_temp | AI:1 | 40001 | 1/2/1 |
| hw_return_temp | AI:2 | 40002 | 1/2/2 |
| hw_supply_pressure | AI:3 | 40003 | 1/2/3 |
| hw_flow | AI:4 | 40004 | 1/2/4 |
| thermal_power | AI:5 | 40005 | 1/2/5 |
| thermal_energy | AI:6 | 40006-40007 | 1/2/6 |
| flue_gas_temp | AI:7 | 40008 | 1/2/7 |
| combustion_o2 | AI:8 | 40009 | 1/2/8 |
| combustion_co | AI:9 | 40010 | 1/2/9 |
| combustion_efficiency | AI:10 | 40011 | 1/2/10 |
| fuel_flow | AI:11 | 40012 | 1/2/11 |
| fuel_consumption | AI:12 | 40013-40014 | 1/2/12 |
| fuel_pressure | AI:13 | 40015 | 1/2/13 |
| water_level | AI:14 | 40016 | 1/2/14 |
| burner_modulation | AI:15 | 40017 | 1/2/15 |
| pump_speed | AI:16 | 40018 | 1/2/16 |
| pump_power | AI:17 | 40019 | 1/2/17 |
| total_elec_power | AI:18 | 40020 | 1/2/18 |
| hw_supply_temp_sp | AV:1 | 40101 | 1/3/1 |
| enable_cmd | BO:1 | 00001 | 1/4/1 |
| burner_enable_cmd | BO:2 | 00002 | 1/4/2 |
| burner_modulation_cmd | AO:1 | 40201 | 1/4/3 |
| pump_enable_cmd | BO:3 | 00003 | 1/4/4 |
| pump_speed_cmd | AO:2 | 40202 | 1/4/5 |
| reset_alarm_cmd | BO:4 | 00004 | 1/4/6 |
| operating_mode_cmd | AO:3 | 40203 | 1/4/7 |
| boiler_status | BI:1 | 10001 | 1/5/1 |
| burner_status | BI:2 | 10002 | 1/5/2 |
| flame_status | BI:3 | 10003 | 1/5/3 |
| pump_status | BI:4 | 10004 | 1/5/4 |
| fault_status | BI:5 | 10005 | 1/5/5 |
| alarm_status | BI:6 | 10006 | 1/5/6 |
| lockout_status | BI:7 | 10007 | 1/5/7 |
| low_water_alarm | BI:8 | 10008 | 1/5/8 |
| high_limit_alarm | BI:9 | 10009 | 1/5/9 |
| flame_failure_alarm | BI:10 | 10010 | 1/5/10 |
| fuel_pressure_alarm | BI:11 | 10011 | 1/5/11 |
| operating_mode | MI:1 | 30001 | 1/5/12 |

## Sources

- [Project Haystack - Hot Water Boiler Equip](https://project-haystack.org/doc/proto/hot-water-boiler-equip) - Définitions tags Haystack pour chaudières eau chaude
- [Project Haystack - Hot Water Plant](https://project-haystack.org/doc/lib-phIoT/hot-water-plant) - Modélisation centrales thermiques
- [Brick Schema - Equipment](https://brickschema.org/) - Ontologie Brick pour équipements CVC
- [BACnet Integration - Hydronic Systems](https://blog.smartbuildingsacademy.com/hydronic-system-control-part-1) - Contrôle systèmes hydroniques et BACnet
- [AERCO BACnet Objects](https://www.aerco.com/products/hvac-hot-water-solutions/boilers/boiler-accessories/communications-and-controls/protonode-gateway) - Points BACnet chaudières AERCO
- [Real-time Monitoring Energy Efficiency Condensing Boilers](https://www.sciencedirect.com/science/article/pii/S019689041730016X) - Monitoring performance chaudières à condensation
- [Oxygen Analyzers - Boiler Combustion Efficiency](https://www.processsensing.com/en-us/blog/improve_boiler_combustion_efficiency_with_oxygen_analyzers.htm) - Analyseurs O2 pour efficacité combustion
- [Flue Gas Analysis - CleanBoiler.org](http://cleanboiler.org/flue-gas-analysis/) - Analyse gaz de fumées
- [Burner Combustion Control - Eurotherm](https://www.eurotherm.com/us/machine-control-process-automation-articles-us/burner-combustion-control-for-boilers/) - Contrôle combustion brûleurs
- [Modulating Burners - Triangle Tube](https://triangletube.com/about-us/blog/how-modulation-works/) - Fonctionnement modulation brûleurs
- [Boiler Safety Controls and Functions](https://www.rfmacdonald.com/boiler-safety-controls-and-their-functions/) - Dispositifs sécurité chaudières
- [Low Water Cutoff Technology - National Board](https://www.nationalboard.org/index.aspx?pageID=164&ID=237) - Technologies coupure niveau bas
- [Boiler Sequence Control - CleanBoiler.org](http://cleanboiler.org/learn-about/boiler-efficiency-improvement/efficiency-index/boiler-sequence-control/) - Séquencement multi-chaudières
- [Lead-Lag Boiler Controls Guide](https://www.rasmech.com/blog/lead-lag-boiler-controls-the-ultimate-guide/) - Guide contrôle Lead-Lag
- [Differential Pressure VFD Control](https://jmpcoblog.com/hvac-blog/fundamentals-of-differential-pressure-sensored-control-in-variable-speed-pumping) - Contrôle DP pompes vitesse variable
- [Modbus BMS Integration Basics](https://www.projectbms.co.uk/modbus-basics-for-building-management-systems/) - Bases intégration Modbus BMS
