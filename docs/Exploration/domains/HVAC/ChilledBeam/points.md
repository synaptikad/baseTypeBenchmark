# Points de Poutre Froide (Chilled Beam)

## Synthèse
- **Total points mesure** : 8
- **Total points commande** : 5
- **Total points état** : 5

## Points de Mesure (Capteurs)

| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| zone_temp | zone air temp sensor | °C | 18-28 | 1min | Température de la zone |
| zone_humidity | zone air humidity sensor | %RH | 30-70 | 1min | Humidité relative de la zone |
| dewpoint_temp | zone dewpoint temp sensor | °C | 5-20 | 1min | Température de point de rosée (anti-condensation) |
| chw_entering_temp | entering chilled water temp sensor | °C | 12-18 | 1min | Température eau glacée entrée |
| chw_leaving_temp | leaving chilled water temp sensor | °C | 14-20 | 1min | Température eau glacée sortie |
| hw_entering_temp | entering hot water temp sensor | °C | 35-55 | 1min | Température eau chaude entrée (si réversible) |
| primary_air_temp | discharge air temp sensor | °C | 14-22 | 1min | Température air primaire (active) |
| primary_air_flow | discharge air flow sensor | l/s | 10-50 | 1min | Débit air primaire (active) |

## Points de Commande (Actionneurs/Consignes)

| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| zone_temp_cooling_sp | zone air temp cooling sp | °C | 20-28 | Consigne | Consigne température refroidissement |
| zone_temp_heating_sp | zone air temp heating sp | °C | 18-24 | Consigne | Consigne température chauffage |
| chw_valve_cmd | chilled water valve cmd | % | 0-100 | Actionneur | Position vanne eau glacée |
| hw_valve_cmd | hot water valve cmd | % | 0-100 | Actionneur | Position vanne eau chaude (si réversible) |
| primary_air_damper_cmd | discharge air damper cmd | % | 0-100 | Actionneur | Position registre air primaire (active) |

## Points d'État

| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| condensation_alarm | condensation alarm | Boolean | true/false | Alarme risque de condensation |
| cooling_mode | cooling mode status | Boolean | true/false | Mode refroidissement actif |
| heating_mode | heating mode status | Boolean | true/false | Mode chauffage actif (si réversible) |
| valve_fault | valve fault alarm | Boolean | true/false | Défaut vanne motorisée |
| zone_occupied | zone occupied status | Boolean | true/false | Zone occupée |

## Mappings Protocoles

| Point | BACnet Object | Modbus Register | KNX GA |
|-------|---------------|-----------------|--------|
| zone_temp | AI:1 | 40001 (HR) | 1/1/1 |
| zone_humidity | AI:2 | 40002 (HR) | 1/1/2 |
| dewpoint_temp | AI:3 | 40003 (HR) | 1/1/3 |
| chw_entering_temp | AI:4 | 40004 (HR) | 1/1/4 |
| chw_leaving_temp | AI:5 | 40005 (HR) | 1/1/5 |
| hw_entering_temp | AI:6 | 40006 (HR) | 1/1/6 |
| primary_air_temp | AI:7 | 40007 (HR) | 1/1/7 |
| primary_air_flow | AI:8 | 40008 (HR) | 1/1/8 |
| zone_temp_cooling_sp | AV:1 | 40101 (HR) | 1/2/1 |
| zone_temp_heating_sp | AV:2 | 40102 (HR) | 1/2/2 |
| chw_valve_cmd | AO:1 | 40201 (HR) | 1/3/1 |
| hw_valve_cmd | AO:2 | 40202 (HR) | 1/3/2 |
| primary_air_damper_cmd | AO:3 | 40203 (HR) | 1/3/3 |
| condensation_alarm | BI:1 | 10001 (DI) | 1/4/1 |
| cooling_mode | BI:2 | 10002 (DI) | 1/4/2 |
| heating_mode | BI:3 | 10003 (DI) | 1/4/3 |
| valve_fault | BI:4 | 10004 (DI) | 1/4/4 |
| zone_occupied | BI:5 | 10005 (DI) | 1/4/5 |

**Notes sur les mappings :**
- BACnet : AI = Analog Input, AO = Analog Output, AV = Analog Value, BI = Binary Input, BO = Binary Output, MSV = Multi-State Value
- Modbus : HR = Holding Register (40001+), DI = Discrete Input (10001+)
- KNX : GA = Group Address (format Area/Line/Device)

## Stratégies de Contrôle Anti-Condensation

| Paramètre | Seuil | Action |
|-----------|-------|--------|
| Delta T (dewpoint vs chw_entering) | < 2°C | Fermer vanne eau glacée |
| Humidité zone | > 65% | Réduire débit eau glacée |
| Température eau glacée minimum | 14°C | Limite basse eau glacée |

## Sources
- [Chilled Beam Application & Control](https://www.automatedbuildings.com/news/feb12/articles/alc/120124021101alc.html) - Contrôle des poutres froides
- [Understanding Chilled Beam Systems](https://www.facilitiesnet.com/hvac/article/Understanding-Chilled-Beam-Systems-Passive-and-Active--17468) - Systèmes passifs et actifs
- [SEMCO Neuton Pump Module](https://www.semcohvac.com/chilled-beams/neuton-pump-module) - Module de contrôle intégré
- [Project Haystack - Temp Sensor Tags](https://project-haystack.org/forum/topic/1105) - Tags température pour batteries
- [FläktGroup Chilled Beam Systems](https://www.flaktgroup.com/en/flaktgroup-insights-driving-innovation/optimising-ahu-design-for-active-chilled-beam-systems/) - Optimisation systèmes ACB
