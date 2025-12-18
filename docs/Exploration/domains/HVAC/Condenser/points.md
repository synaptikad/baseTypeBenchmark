# Points de Condenseur (Condenser)

## Synthèse
- **Total points mesure** : 10
- **Total points commande** : 4
- **Total points état** : 6

## Points de Mesure (Capteurs)

| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| refrig_entering_temp | refrig entering temp sensor | °C | 60-90 | 30sec | Température réfrigérant entrée (gaz surchauffé) |
| refrig_leaving_temp | refrig leaving temp sensor | °C | 35-50 | 30sec | Température réfrigérant sortie (liquide) |
| condensing_pressure | refrig condensing pressure sensor | bar | 15-30 | 30sec | Pression de condensation |
| condensing_temp | refrig condensing temp sensor | °C | 35-50 | 30sec | Température de condensation (saturation) |
| subcooling | refrig subcooling sensor | K | 3-10 | 1min | Sous-refroidissement |
| ambient_temp | outside air temp sensor | °C | -20-45 | 1min | Température air extérieur (air-cooled) |
| water_entering_temp | entering water temp sensor | °C | 25-35 | 1min | Température eau entrée (water-cooled) |
| water_leaving_temp | leaving water temp sensor | °C | 30-40 | 1min | Température eau sortie (water-cooled) |
| fan_speed | fan speed sensor | % | 0-100 | 1min | Vitesse ventilateurs (air-cooled) |
| approach_temp | condenser approach temp sensor | K | 5-15 | 5min | Approche condenseur |

## Points de Commande (Actionneurs/Consignes)

| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| fan_speed_cmd | condenser fan speed cmd | % | 0-100 | Actionneur | Commande vitesse ventilateurs |
| fan_enable_cmd | condenser fan enable cmd | - | 0/1 | Actionneur | Commande marche ventilateurs |
| condensing_pressure_sp | condensing pressure sp | bar | 15-28 | Consigne | Consigne pression condensation |
| water_flow_cmd | condenser water valve cmd | % | 0-100 | Actionneur | Commande vanne eau condenseur |

## Points d'État

| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| fan_run | condenser fan run status | Boolean | true/false | Ventilateur(s) en marche |
| fan_stage | condenser fan stage status | Enum | 0/1/2/3 | Étage ventilateurs actif |
| high_pressure_alarm | high pressure alarm | Boolean | true/false | Alarme haute pression |
| high_temp_alarm | high temp alarm | Boolean | true/false | Alarme haute température |
| fan_fault | condenser fan fault alarm | Boolean | true/false | Défaut ventilateur |
| water_flow_ok | condenser water flow ok status | Boolean | true/false | Débit eau confirmé (water-cooled) |

## Mappings Protocoles

| Point | BACnet Object | Modbus Register | KNX GA |
|-------|---------------|-----------------|--------|
| refrig_entering_temp | AI:1 | 40001 (HR) | 1/1/1 |
| refrig_leaving_temp | AI:2 | 40002 (HR) | 1/1/2 |
| condensing_pressure | AI:3 | 40003 (HR) | 1/1/3 |
| condensing_temp | AI:4 | 40004 (HR) | 1/1/4 |
| subcooling | AV:1 | 40101 (HR) | 1/1/5 |
| ambient_temp | AI:5 | 40005 (HR) | 1/1/6 |
| water_entering_temp | AI:6 | 40006 (HR) | 1/1/7 |
| water_leaving_temp | AI:7 | 40007 (HR) | 1/1/8 |
| fan_speed | AI:8 | 40008 (HR) | 1/1/9 |
| approach_temp | AV:2 | 40102 (HR) | 1/1/10 |
| fan_speed_cmd | AO:1 | 40201 (HR) | 1/2/1 |
| fan_enable_cmd | BO:1 | 00001 (Coil) | 1/2/2 |
| condensing_pressure_sp | AV:3 | 40103 (HR) | 1/2/3 |
| water_flow_cmd | AO:2 | 40202 (HR) | 1/2/4 |
| fan_run | BI:1 | 10001 (DI) | 1/3/1 |
| fan_stage | MSV:1 | 40301 (HR) | 1/3/2 |
| high_pressure_alarm | BI:2 | 10002 (DI) | 1/3/3 |
| high_temp_alarm | BI:3 | 10003 (DI) | 1/3/4 |
| fan_fault | BI:4 | 10004 (DI) | 1/3/5 |
| water_flow_ok | BI:5 | 10005 (DI) | 1/3/6 |

**Notes sur les mappings :**
- BACnet : AI = Analog Input, AO = Analog Output, AV = Analog Value, BI = Binary Input, BO = Binary Output, MSV = Multi-State Value
- Modbus : HR = Holding Register (40001+), Coil = Digital Output (00001+), DI = Discrete Input (10001+)

## Seuils Typiques (R410A)

| Paramètre | Normal | Avertissement | Alarme |
|-----------|--------|---------------|--------|
| Pression condensation | 18-25 bar | > 28 bar | > 32 bar |
| Température condensation | 35-45°C | > 50°C | > 55°C |
| Sous-refroidissement | 5-8 K | < 3 K ou > 12 K | < 1 K |
| Approche | 8-12 K | > 15 K | > 20 K |

## Sources
- ASHRAE Handbook - Refrigeration
- Project Haystack - Condenser Tags
- Brick Schema - Condenser Class
- Carrier / Trane / Daikin - Chiller Technical Documentation
