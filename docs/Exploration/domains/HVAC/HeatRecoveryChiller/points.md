# Points de Chiller à Récupération de Chaleur (Heat Recovery Chiller)

## Synthèse
- **Total points mesure** : 18
- **Total points commande** : 8
- **Total points état** : 10

## Points de Mesure (Capteurs)

| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| chw_supply_temp | chilled water leaving temp sensor | °C | 5-12 | 1min | Température eau glacée départ |
| chw_return_temp | chilled water entering temp sensor | °C | 10-18 | 1min | Température eau glacée retour |
| chw_flow | chilled water flow sensor | m³/h | 0-500 | 1min | Débit eau glacée |
| hw_supply_temp | hot water leaving temp sensor | °C | 45-70 | 1min | Température eau chaude départ (récupération) |
| hw_return_temp | hot water entering temp sensor | °C | 35-55 | 1min | Température eau chaude retour |
| hw_flow | hot water flow sensor | m³/h | 0-300 | 1min | Débit eau chaude récupérée |
| condenser_entering_temp | condenser entering water temp sensor | °C | 20-35 | 1min | Température entrée condenseur (tour) |
| condenser_leaving_temp | condenser leaving water temp sensor | °C | 25-40 | 1min | Température sortie condenseur |
| refrigerant_hp | refrig discharge pressure sensor | bar | 10-25 | 30sec | Pression haute (refoulement) |
| refrigerant_lp | refrig suction pressure sensor | bar | 2-6 | 30sec | Pression basse (aspiration) |
| compressor_current | compressor elec current sensor | A | 0-500 | 1min | Courant compresseur |
| compressor_power | compressor elec power sensor | kW | 0-1000 | 5min | Puissance électrique compresseur |
| cooling_capacity | cooling capacity sensor | kW | 0-3000 | 5min | Puissance frigorifique produite |
| heat_recovery_capacity | heat recovery capacity sensor | kW | 0-3500 | 5min | Puissance thermique récupérée |
| cop | cop sensor | - | 2-8 | 5min | Coefficient de performance |
| oil_temp | compressor oil temp sensor | °C | 40-80 | 1min | Température huile compresseur |
| oil_pressure | compressor oil pressure sensor | bar | 1-5 | 1min | Pression huile compresseur |
| evaporator_approach | evaporator approach temp sensor | K | 1-5 | 5min | Approche évaporateur |

## Points de Commande (Actionneurs/Consignes)

| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| chiller_enable_cmd | chiller enable cmd | - | 0/1 | Actionneur | Commande marche/arrêt chiller |
| chw_temp_sp | chilled water temp sp | °C | 5-12 | Consigne | Consigne température eau glacée |
| hw_temp_sp | hot water temp sp | °C | 45-70 | Consigne | Consigne température eau chaude |
| heat_recovery_enable_cmd | heat recovery enable cmd | - | 0/1 | Actionneur | Activation récupération de chaleur |
| cooling_capacity_cmd | cooling capacity cmd | % | 0-100 | Actionneur | Demande capacité frigorifique |
| heat_recovery_priority_cmd | heat recovery priority cmd | - | 0/1 | Actionneur | Priorité récupération vs refroidissement |
| condenser_fan_speed_cmd | condenser fan speed cmd | % | 0-100 | Actionneur | Vitesse ventilateur tour (si air-cooled) |
| chw_valve_cmd | chilled water valve cmd | % | 0-100 | Actionneur | Position vanne eau glacée |

## Points d'État

| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| chiller_run | chiller run status | Boolean | true/false | Chiller en marche |
| compressor_run | compressor run status | Boolean | true/false | Compresseur en marche |
| heat_recovery_active | heat recovery run status | Boolean | true/false | Récupération de chaleur active |
| condenser_pump_run | condenser pump run status | Boolean | true/false | Pompe condenseur en marche |
| chiller_mode | chiller mode status | Enum | cooling/heat_recovery/both | Mode de fonctionnement |
| hp_alarm | high pressure alarm | Boolean | true/false | Alarme haute pression |
| lp_alarm | low pressure alarm | Boolean | true/false | Alarme basse pression |
| chw_low_temp_alarm | chilled water low temp alarm | Boolean | true/false | Alarme T° eau glacée basse |
| oil_fault | oil fault alarm | Boolean | true/false | Défaut huile |
| general_fault | chiller fault alarm | Boolean | true/false | Défaut général chiller |

## Mappings Protocoles

| Point | BACnet Object | Modbus Register | KNX GA |
|-------|---------------|-----------------|--------|
| chw_supply_temp | AI:1 | 40001 (HR) | 1/1/1 |
| chw_return_temp | AI:2 | 40002 (HR) | 1/1/2 |
| chw_flow | AI:3 | 40003 (HR) | 1/1/3 |
| hw_supply_temp | AI:4 | 40004 (HR) | 1/1/4 |
| hw_return_temp | AI:5 | 40005 (HR) | 1/1/5 |
| hw_flow | AI:6 | 40006 (HR) | 1/1/6 |
| condenser_entering_temp | AI:7 | 40007 (HR) | 1/1/7 |
| condenser_leaving_temp | AI:8 | 40008 (HR) | 1/1/8 |
| refrigerant_hp | AI:9 | 40009 (HR) | 1/1/9 |
| refrigerant_lp | AI:10 | 40010 (HR) | 1/1/10 |
| compressor_current | AI:11 | 40011 (HR) | 1/1/11 |
| compressor_power | AI:12 | 40012 (HR) | 1/1/12 |
| cooling_capacity | AV:1 | 40101 (HR) | 1/1/13 |
| heat_recovery_capacity | AV:2 | 40102 (HR) | 1/1/14 |
| cop | AV:3 | 40103 (HR) | 1/1/15 |
| oil_temp | AI:13 | 40013 (HR) | 1/1/16 |
| oil_pressure | AI:14 | 40014 (HR) | 1/1/17 |
| evaporator_approach | AV:4 | 40104 (HR) | 1/1/18 |
| chiller_enable_cmd | BO:1 | 00001 (Coil) | 1/2/1 |
| chw_temp_sp | AV:5 | 40105 (HR) | 1/2/2 |
| hw_temp_sp | AV:6 | 40106 (HR) | 1/2/3 |
| heat_recovery_enable_cmd | BO:2 | 00002 (Coil) | 1/2/4 |
| cooling_capacity_cmd | AO:1 | 40201 (HR) | 1/2/5 |
| heat_recovery_priority_cmd | BO:3 | 00003 (Coil) | 1/2/6 |
| condenser_fan_speed_cmd | AO:2 | 40202 (HR) | 1/2/7 |
| chw_valve_cmd | AO:3 | 40203 (HR) | 1/2/8 |
| chiller_run | BI:1 | 10001 (DI) | 1/3/1 |
| compressor_run | BI:2 | 10002 (DI) | 1/3/2 |
| heat_recovery_active | BI:3 | 10003 (DI) | 1/3/3 |
| condenser_pump_run | BI:4 | 10004 (DI) | 1/3/4 |
| chiller_mode | MSV:1 | 40301 (HR) | 1/3/5 |
| hp_alarm | BI:5 | 10005 (DI) | 1/3/6 |
| lp_alarm | BI:6 | 10006 (DI) | 1/3/7 |
| chw_low_temp_alarm | BI:7 | 10007 (DI) | 1/3/8 |
| oil_fault | BI:8 | 10008 (DI) | 1/3/9 |
| general_fault | BI:9 | 10009 (DI) | 1/3/10 |

**Notes sur les mappings :**
- BACnet : AI = Analog Input, AO = Analog Output, AV = Analog Value, BI = Binary Input, BO = Binary Output, MSV = Multi-State Value
- Modbus : HR = Holding Register (40001+), Coil = Digital Output (00001+), DI = Discrete Input (10001+)
- KNX : GA = Group Address (format Area/Line/Device)

## Modes de Fonctionnement

| Mode | Eau Glacée | Eau Chaude | Application |
|------|------------|------------|-------------|
| Cooling Only | Production | Tour de refroidissement | Été, pas de besoin chaud |
| Heat Recovery | Production | Récupération | Besoins simultanés chaud/froid |
| Priority Heat | Production partielle | Maximum | Priorité eau chaude |
| Priority Cooling | Maximum | Partielle | Priorité eau glacée |

## Sources
- Carrier / Trane / Daikin - Heat Recovery Chiller Technical Manuals
- ASHRAE Handbook - Heat Recovery Systems
- Project Haystack - Chiller Tags
- BACnet Standard - Chiller Control Objects
