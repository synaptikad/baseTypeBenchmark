# Points de Terminal Double Gaine (Dual Duct Terminal)

## Synthèse
- **Total points mesure** : 10
- **Total points commande** : 8
- **Total points état** : 5

## Points de Mesure (Capteurs)

| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| zone_temp | zone air temp sensor | °C | 18-28 | 1min | Température de la zone |
| discharge_temp | discharge air temp sensor | °C | 14-35 | 1min | Température air mélangé soufflé |
| hot_deck_temp | hot entering air temp sensor | °C | 28-40 | 1min | Température air chaud entrant |
| cold_deck_temp | cold entering air temp sensor | °C | 12-18 | 1min | Température air froid entrant |
| hot_deck_flow | hot air flow sensor | m³/h | 0-2500 | 1min | Débit d'air chaud |
| cold_deck_flow | cold air flow sensor | m³/h | 0-2500 | 1min | Débit d'air froid |
| total_flow | discharge air flow sensor | m³/h | 200-5000 | 1min | Débit total soufflé |
| hot_deck_dp | hot inlet differential pressure sensor | Pa | 0-500 | 1min | Pression différentielle entrée air chaud |
| cold_deck_dp | cold inlet differential pressure sensor | Pa | 0-500 | 1min | Pression différentielle entrée air froid |
| zone_co2 | zone co2 sensor | ppm | 400-2000 | 5min | Concentration CO2 zone (optionnel) |

## Points de Commande (Actionneurs/Consignes)

| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| zone_temp_cooling_sp | zone air temp cooling sp | °C | 22-28 | Consigne | Consigne température refroidissement |
| zone_temp_heating_sp | zone air temp heating sp | °C | 18-22 | Consigne | Consigne température chauffage |
| hot_damper_cmd | hot damper cmd | % | 0-100 | Actionneur | Position registre air chaud |
| cold_damper_cmd | cold damper cmd | % | 0-100 | Actionneur | Position registre air froid |
| hot_flow_min_sp | hot air flow min sp | m³/h | 0-500 | Consigne | Débit minimum air chaud |
| hot_flow_max_sp | hot air flow max sp | m³/h | 500-2500 | Consigne | Débit maximum air chaud |
| cold_flow_min_sp | cold air flow min sp | m³/h | 100-500 | Consigne | Débit minimum air froid |
| cold_flow_max_sp | cold air flow max sp | m³/h | 500-2500 | Consigne | Débit maximum air froid |

## Points d'État

| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| heating_mode | heating mode status | Boolean | true/false | Mode chauffage actif (air chaud dominant) |
| cooling_mode | cooling mode status | Boolean | true/false | Mode refroidissement actif (air froid dominant) |
| deadband_mode | deadband mode status | Boolean | true/false | Dans la bande morte (mélange minimal) |
| zone_occupied | zone occupied status | Boolean | true/false | Zone occupée |
| damper_fault | damper fault alarm | Boolean | true/false | Défaut registre (chaud ou froid) |

## Mappings Protocoles

| Point | BACnet Object | Modbus Register | KNX GA |
|-------|---------------|-----------------|--------|
| zone_temp | AI:1 | 40001 (HR) | 1/1/1 |
| discharge_temp | AI:2 | 40002 (HR) | 1/1/2 |
| hot_deck_temp | AI:3 | 40003 (HR) | 1/1/3 |
| cold_deck_temp | AI:4 | 40004 (HR) | 1/1/4 |
| hot_deck_flow | AI:5 | 40005 (HR) | 1/1/5 |
| cold_deck_flow | AI:6 | 40006 (HR) | 1/1/6 |
| total_flow | AI:7 | 40007 (HR) | 1/1/7 |
| hot_deck_dp | AI:8 | 40008 (HR) | 1/1/8 |
| cold_deck_dp | AI:9 | 40009 (HR) | 1/1/9 |
| zone_co2 | AI:10 | 40010 (HR) | 1/1/10 |
| zone_temp_cooling_sp | AV:1 | 40101 (HR) | 1/2/1 |
| zone_temp_heating_sp | AV:2 | 40102 (HR) | 1/2/2 |
| hot_damper_cmd | AO:1 | 40201 (HR) | 1/2/3 |
| cold_damper_cmd | AO:2 | 40202 (HR) | 1/2/4 |
| hot_flow_min_sp | AV:3 | 40103 (HR) | 1/2/5 |
| hot_flow_max_sp | AV:4 | 40104 (HR) | 1/2/6 |
| cold_flow_min_sp | AV:5 | 40105 (HR) | 1/2/7 |
| cold_flow_max_sp | AV:6 | 40106 (HR) | 1/2/8 |
| heating_mode | BI:1 | 10001 (DI) | 1/3/1 |
| cooling_mode | BI:2 | 10002 (DI) | 1/3/2 |
| deadband_mode | BI:3 | 10003 (DI) | 1/3/3 |
| zone_occupied | BI:4 | 10004 (DI) | 1/3/4 |
| damper_fault | BI:5 | 10005 (DI) | 1/3/5 |

**Notes sur les mappings :**
- BACnet : AI = Analog Input, AO = Analog Output, AV = Analog Value, BI = Binary Input, BO = Binary Output, MSV = Multi-State Value
- Modbus : HR = Holding Register (40001+), DI = Discrete Input (10001+)
- KNX : GA = Group Address (format Area/Line/Device)

## Séquence de Contrôle Typique

| Zone Température | Air Chaud | Air Froid | Mode |
|------------------|-----------|-----------|------|
| T < Heating SP - 2°C | Maximum | Minimum | Chauffage fort |
| Heating SP - 2°C < T < Heating SP | Modulé | Minimum | Chauffage |
| Heating SP < T < Cooling SP | Minimum | Minimum | Bande morte |
| Cooling SP < T < Cooling SP + 2°C | Minimum | Modulé | Refroidissement |
| T > Cooling SP + 2°C | Minimum | Maximum | Refroidissement fort |

## Sources
- [Trane VariTrane Dual Duct](https://www.trane.com/commercial/north-america/us/en/products-systems/air-handlers/variable-air-volume/dual-duct.html) - Terminaux double gaine VAV
- [KMC SimplyVAV Dual Duct](https://www.kmccontrols.com/product/bacnet-asc-simplyvav-dual-duct-40-in-lbs-90-sec/) - Contrôleur BACnet double gaine
- [Johnson Controls Dual Duct VAV](https://www.johnsoncontrols.com/hvac-equipment/air-distribution/terminal-units/variable-air-volume-terminals/dual-duct-vav) - Terminaux VAV double gaine
- [Neptronic Dual Duct Terminals](https://www.neptronic.com/TechTime/20180105/HVAC_Controls/TechTime_Dec-2017_HVAC_Controls.pdf) - Configuration maître/esclave
- [Johnson Controls VAV Terminal Control](https://docs.johnsoncontrols.com/bas/api/khub/documents/7P5eJSg3kyQBhl9W2JgkPA/content) - Séquences de contrôle
