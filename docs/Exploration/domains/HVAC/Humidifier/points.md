# Points d'Humidificateur (Humidifier)

## Synthèse
- **Total points mesure** : 10
- **Total points commande** : 4
- **Total points état** : 7

## Points de Mesure (Capteurs)

| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| duct_humidity | duct air humidity sensor | %RH | 20-80 | 1min | Humidité relative en gaine (après humidificateur) |
| zone_humidity | zone air humidity sensor | %RH | 20-70 | 1min | Humidité relative de la zone |
| duct_temp | duct air temp sensor | °C | 15-35 | 1min | Température en gaine |
| steam_output | steam output sensor | kg/h | 0-200 | 1min | Débit vapeur produit |
| water_consumption | water flow sensor | l/h | 0-250 | 5min | Consommation d'eau |
| power_consumption | elec power sensor | kW | 0-150 | 5min | Puissance électrique consommée |
| cylinder_current | humidifier elec current sensor | A | 0-200 | 1min | Courant cylindre/électrodes |
| water_conductivity | water conductivity sensor | µS/cm | 100-2000 | 15min | Conductivité eau alimentation |
| drain_cycles | drain cycle count sensor | - | 0-9999 | 15min | Nombre de cycles de vidange |
| steam_pressure | steam pressure sensor | kPa | 0-200 | 1min | Pression vapeur (si vapeur externe) |

## Points de Commande (Actionneurs/Consignes)

| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| humidity_sp | humidity sp | %RH | 30-60 | Consigne | Consigne humidité relative |
| humidification_cmd | humidification cmd | % | 0-100 | Actionneur | Commande capacité humidification |
| enable_cmd | enable cmd | - | 0/1 | Actionneur | Commande marche/arrêt |
| drain_cmd | drain cmd | - | 0/1 | Actionneur | Commande vidange forcée |

## Points d'État

| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| unit_run | run status | Boolean | true/false | Unité en production de vapeur |
| steam_production | steam production status | Boolean | true/false | Production vapeur active |
| cylinder_heating | cylinder heating status | Boolean | true/false | Cylindre en chauffe |
| drain_active | drain run status | Boolean | true/false | Vidange en cours |
| cylinder_empty_alarm | cylinder empty alarm | Boolean | true/false | Alarme cylindre vide |
| low_water_alarm | low water alarm | Boolean | true/false | Alarme niveau eau bas |
| unit_fault | unit fault alarm | Boolean | true/false | Défaut général unité |

## Mappings Protocoles

| Point | BACnet Object | Modbus Register | KNX GA |
|-------|---------------|-----------------|--------|
| duct_humidity | AI:1 | 40001 (HR) | 1/1/1 |
| zone_humidity | AI:2 | 40002 (HR) | 1/1/2 |
| duct_temp | AI:3 | 40003 (HR) | 1/1/3 |
| steam_output | AI:4 | 40004 (HR) | 1/1/4 |
| water_consumption | AI:5 | 40005 (HR) | 1/1/5 |
| power_consumption | AI:6 | 40006 (HR) | 1/1/6 |
| cylinder_current | AI:7 | 40007 (HR) | 1/1/7 |
| water_conductivity | AI:8 | 40008 (HR) | 1/1/8 |
| drain_cycles | AI:9 | 40009 (HR) | 1/1/9 |
| steam_pressure | AI:10 | 40010 (HR) | 1/1/10 |
| humidity_sp | AV:1 | 40101 (HR) | 1/2/1 |
| humidification_cmd | AO:1 | 40201 (HR) | 1/2/2 |
| enable_cmd | BO:1 | 00001 (Coil) | 1/2/3 |
| drain_cmd | BO:2 | 00002 (Coil) | 1/2/4 |
| unit_run | BI:1 | 10001 (DI) | 1/3/1 |
| steam_production | BI:2 | 10002 (DI) | 1/3/2 |
| cylinder_heating | BI:3 | 10003 (DI) | 1/3/3 |
| drain_active | BI:4 | 10004 (DI) | 1/3/4 |
| cylinder_empty_alarm | BI:5 | 10005 (DI) | 1/3/5 |
| low_water_alarm | BI:6 | 10006 (DI) | 1/3/6 |
| unit_fault | BI:7 | 10007 (DI) | 1/3/7 |

**Notes sur les mappings :**
- BACnet : AI = Analog Input, AO = Analog Output, AV = Analog Value, BI = Binary Input, BO = Binary Output, MSV = Multi-State Value
- Modbus : HR = Holding Register (40001+), Coil = Digital Output (00001+), DI = Discrete Input (10001+)
- KNX : GA = Group Address (format Area/Line/Device)

## Consignes Typiques par Application

| Application | Consigne HR | Différentiel | Notes |
|-------------|-------------|--------------|-------|
| Bureaux tertiaire | 40-50% | ±5% | Confort général |
| Hôpitaux | 40-60% | ±3% | Zones critiques |
| Musées/Archives | 45-55% | ±3% | Conservation |
| Salles blanches | 40-50% | ±2% | Production électronique |
| Résidentiel | 35-45% | ±5% | Confort hiver |

## Paramètres de Maintenance

| Indicateur | Seuil Avertissement | Seuil Alarme | Action |
|------------|---------------------|--------------|--------|
| Conductivité eau | > 1000 µS/cm | > 1500 µS/cm | Vérifier adoucisseur |
| Cycles vidange/jour | > 10 | > 20 | Vérifier qualité eau |
| Heures cylindre | > 5000h | > 8000h | Remplacement cylindre |

## Sources
- Condair / Carel / Nortec - Steam Humidifier Technical Documentation
- ASHRAE Handbook - Humidification
- Project Haystack - Humidifier Tags
- Brick Schema - Humidifier Class
