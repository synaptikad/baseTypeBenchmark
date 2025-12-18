# Points de Chaudière Vapeur (Steam Boiler)

## Synthèse
- **Total points mesure** : 16
- **Total points commande** : 5
- **Total points état** : 12

## Points de Mesure (Capteurs)

| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| steam_pressure | steam pressure sensor | bar | 0.5-20 | 1min | Pression vapeur sortie |
| steam_temp | steam temp sensor | °C | 110-250 | 1min | Température vapeur |
| drum_level | drum water level sensor | % | 30-70 | 1min | Niveau eau ballon |
| drum_pressure | drum pressure sensor | bar | 0.5-20 | 1min | Pression ballon |
| feedwater_temp | feedwater temp sensor | °C | 60-105 | 1min | Température eau alimentaire |
| feedwater_pressure | feedwater pressure sensor | bar | 2-25 | 1min | Pression eau alimentaire |
| flue_temp | flue gas temp sensor | °C | 100-300 | 1min | Température fumées |
| combustion_air_temp | combustion air temp sensor | °C | 10-50 | 5min | Température air comburant |
| burner_power | burner power sensor | % | 0-100 | 1min | Puissance brûleur (modulation) |
| fuel_consumption | fuel flow sensor | m³/h | 0-1000 | 5min | Consommation combustible |
| steam_flow | steam flow sensor | kg/h | 0-50000 | 1min | Débit vapeur produite |
| o2_flue | flue o2 sensor | % | 2-8 | 1min | Teneur O2 fumées |
| co_flue | flue co sensor | ppm | 0-500 | 1min | Teneur CO fumées |
| conductivity | blowdown conductivity sensor | µS/cm | 100-3000 | 5min | Conductivité eau (purge) |
| efficiency | efficiency sensor | % | 75-95 | 5min | Rendement instantané |
| run_hours | run hours sensor | h | 0-99999 | 15min | Heures de fonctionnement |

## Points de Commande (Actionneurs/Consignes)

| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| enable_cmd | boiler enable cmd | - | 0/1 | Actionneur | Commande marche/arrêt |
| steam_pressure_sp | steam pressure sp | bar | 0.5-15 | Consigne | Consigne pression vapeur |
| drum_level_sp | drum level sp | % | 40-60 | Consigne | Consigne niveau ballon |
| burner_modulation_cmd | burner modulation cmd | % | 0-100 | Actionneur | Commande modulation brûleur |
| blowdown_cmd | blowdown valve cmd | - | 0/1 | Actionneur | Commande vanne de purge |

## Points d'État

| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| burner_run | burner run status | Boolean | true/false | Brûleur en marche |
| flame_detected | flame detected status | Boolean | true/false | Flamme détectée |
| feedwater_pump_run | feedwater pump run status | Boolean | true/false | Pompe alimentaire en marche |
| pilot_flame | pilot flame status | Boolean | true/false | Veilleuse allumée |
| low_water_alarm | low water alarm | Boolean | true/false | Alarme niveau bas critique |
| high_pressure_alarm | high pressure alarm | Boolean | true/false | Alarme haute pression |
| flame_fault | flame fault alarm | Boolean | true/false | Défaut flamme |
| flue_fault | flue fault alarm | Boolean | true/false | Défaut évacuation fumées |
| low_feedwater_pressure | low feedwater pressure alarm | Boolean | true/false | Alarme basse pression alimentation |
| high_conductivity_alarm | high conductivity alarm | Boolean | true/false | Alarme conductivité élevée |
| safety_lockout | safety lockout status | Boolean | true/false | Verrouillage sécurité actif |
| general_fault | boiler fault alarm | Boolean | true/false | Défaut général |

## Mappings Protocoles

| Point | BACnet Object | Modbus Register |
|-------|---------------|-----------------|
| steam_pressure | AI:1 | 40001 (HR) |
| steam_temp | AI:2 | 40002 (HR) |
| drum_level | AI:3 | 40003 (HR) |
| drum_pressure | AI:4 | 40004 (HR) |
| feedwater_temp | AI:5 | 40005 (HR) |
| feedwater_pressure | AI:6 | 40006 (HR) |
| flue_temp | AI:7 | 40007 (HR) |
| burner_power | AI:8 | 40008 (HR) |
| fuel_consumption | AI:9 | 40009 (HR) |
| steam_flow | AI:10 | 40010 (HR) |
| o2_flue | AI:11 | 40011 (HR) |
| co_flue | AI:12 | 40012 (HR) |
| conductivity | AI:13 | 40013 (HR) |
| efficiency | AV:1 | 40101 (HR) |
| enable_cmd | BO:1 | 00001 (Coil) |
| steam_pressure_sp | AV:2 | 40102 (HR) |
| drum_level_sp | AV:3 | 40103 (HR) |
| burner_modulation_cmd | AO:1 | 40201 (HR) |
| blowdown_cmd | BO:2 | 00002 (Coil) |
| burner_run | BI:1 | 10001 (DI) |
| flame_detected | BI:2 | 10002 (DI) |
| feedwater_pump_run | BI:3 | 10003 (DI) |
| low_water_alarm | BI:4 | 10004 (DI) |
| high_pressure_alarm | BI:5 | 10005 (DI) |
| flame_fault | BI:6 | 10006 (DI) |
| safety_lockout | BI:7 | 10007 (DI) |
| general_fault | BI:8 | 10008 (DI) |

## Classes de Pression Vapeur

| Classe | Pression | Température | Application |
|--------|----------|-------------|-------------|
| Basse pression | < 1 bar | < 120°C | Chauffage bâtiment |
| Moyenne pression | 1-10 bar | 120-184°C | HVAC, humidification |
| Haute pression | 10-40 bar | 184-250°C | Process industriel |

## Séquence de Sécurité (Typique)

1. Vérification niveau eau (low water cutoff)
2. Purge pré-allumage (pre-purge)
3. Allumage veilleuse
4. Détection flamme
5. Allumage brûleur principal
6. Modulation selon demande
7. Post-purge à l'arrêt

## Sources
- EN 12953 - Shell Boilers Safety Requirements
- EN 12952 - Water-tube Boilers
- ASHRAE Handbook - HVAC Systems and Equipment
- ASME Boiler and Pressure Vessel Code
- Project Haystack - Steam Boiler Tags
