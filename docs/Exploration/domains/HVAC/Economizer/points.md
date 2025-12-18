# Points d'Économiseur d'Énergie (Economizer)

## Synthèse
- **Total points mesure** : 12
- **Total points commande** : 7
- **Total points état** : 5

## Points de Mesure (Capteurs)

| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| outdoor_temp | outside air temp sensor | °C | -20-45 | 1min | Température air extérieur |
| outdoor_humidity | outside air humidity sensor | %RH | 10-100 | 1min | Humidité relative extérieure |
| outdoor_enthalpy | outside air enthalpy sensor | kJ/kg | 10-90 | 1min | Enthalpie air extérieur (calculée) |
| return_temp | return air temp sensor | °C | 18-28 | 1min | Température air de reprise |
| return_humidity | return air humidity sensor | %RH | 30-70 | 1min | Humidité air de reprise |
| return_enthalpy | return air enthalpy sensor | kJ/kg | 40-70 | 1min | Enthalpie air de reprise (calculée) |
| mixed_temp | mixed air temp sensor | °C | 10-30 | 1min | Température air mélangé |
| supply_temp | discharge air temp sensor | °C | 12-22 | 1min | Température air soufflé |
| oa_damper_position | outside air damper position sensor | % | 0-100 | 1min | Position registre air neuf |
| ra_damper_position | return air damper position sensor | % | 0-100 | 1min | Position registre air recyclé |
| exhaust_damper_position | exhaust air damper position sensor | % | 0-100 | 1min | Position registre extraction |
| oa_flow | outside air flow sensor | m³/h | 0-50000 | 1min | Débit air neuf mesuré |

## Points de Commande (Actionneurs/Consignes)

| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| oa_damper_cmd | outside air damper cmd | % | 0-100 | Actionneur | Commande registre air neuf |
| ra_damper_cmd | return air damper cmd | % | 0-100 | Actionneur | Commande registre air recyclé |
| exhaust_damper_cmd | exhaust air damper cmd | % | 0-100 | Actionneur | Commande registre extraction |
| oa_damper_min_sp | outside air damper min sp | % | 10-30 | Consigne | Position minimale air neuf (ventilation) |
| economizer_high_limit_sp | economizer high limit sp | °C | 15-24 | Consigne | Température limite haute économiseur |
| enthalpy_high_limit_sp | economizer enthalpy limit sp | kJ/kg | 45-55 | Consigne | Enthalpie limite haute économiseur |
| mixed_temp_sp | mixed air temp sp | °C | 12-18 | Consigne | Consigne température mélange |

## Points d'État

| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| economizer_enable | economizer enable status | Boolean | true/false | Économiseur activé (conditions favorables) |
| freecooling_active | freecooling run status | Boolean | true/false | Mode free-cooling actif (100% air neuf) |
| high_limit_lockout | economizer lockout status | Boolean | true/false | Blocage limite haute dépassée |
| freeze_protect_active | freeze protect alarm | Boolean | true/false | Protection antigel active |
| economizer_fault | economizer fault alarm | Boolean | true/false | Défaut système économiseur |

## Mappings Protocoles

| Point | BACnet Object | Modbus Register | KNX GA |
|-------|---------------|-----------------|--------|
| outdoor_temp | AI:1 | 40001 (HR) | 1/1/1 |
| outdoor_humidity | AI:2 | 40002 (HR) | 1/1/2 |
| outdoor_enthalpy | AV:1 | 40101 (HR) | 1/1/3 |
| return_temp | AI:3 | 40003 (HR) | 1/1/4 |
| return_humidity | AI:4 | 40004 (HR) | 1/1/5 |
| return_enthalpy | AV:2 | 40102 (HR) | 1/1/6 |
| mixed_temp | AI:5 | 40005 (HR) | 1/1/7 |
| supply_temp | AI:6 | 40006 (HR) | 1/1/8 |
| oa_damper_position | AI:7 | 40007 (HR) | 1/1/9 |
| ra_damper_position | AI:8 | 40008 (HR) | 1/1/10 |
| exhaust_damper_position | AI:9 | 40009 (HR) | 1/1/11 |
| oa_flow | AI:10 | 40010 (HR) | 1/1/12 |
| oa_damper_cmd | AO:1 | 40201 (HR) | 1/2/1 |
| ra_damper_cmd | AO:2 | 40202 (HR) | 1/2/2 |
| exhaust_damper_cmd | AO:3 | 40203 (HR) | 1/2/3 |
| oa_damper_min_sp | AV:3 | 40103 (HR) | 1/2/4 |
| economizer_high_limit_sp | AV:4 | 40104 (HR) | 1/2/5 |
| enthalpy_high_limit_sp | AV:5 | 40105 (HR) | 1/2/6 |
| mixed_temp_sp | AV:6 | 40106 (HR) | 1/2/7 |
| economizer_enable | BI:1 | 10001 (DI) | 1/3/1 |
| freecooling_active | BI:2 | 10002 (DI) | 1/3/2 |
| high_limit_lockout | BI:3 | 10003 (DI) | 1/3/3 |
| freeze_protect_active | BI:4 | 10004 (DI) | 1/3/4 |
| economizer_fault | BI:5 | 10005 (DI) | 1/3/5 |

**Notes sur les mappings :**
- BACnet : AI = Analog Input, AO = Analog Output, AV = Analog Value, BI = Binary Input, BO = Binary Output, MSV = Multi-State Value
- Modbus : HR = Holding Register (40001+), DI = Discrete Input (10001+)
- KNX : GA = Group Address (format Area/Line/Device)

## Types de Contrôle ASHRAE 90.1

| Type | Critère d'Activation | Précision Requise |
|------|---------------------|-------------------|
| Fixed Dry-Bulb | T_ext < seuil fixe | ±1°C |
| Differential Dry-Bulb | T_ext < T_return | ±1°C |
| Fixed Enthalpy | H_ext < seuil fixe | ±3 kJ/kg |
| Electronic Enthalpy | H_ext < seuil (capteur intégré) | ±3 kJ/kg |
| Differential Enthalpy | H_ext < H_return | ±3 kJ/kg |
| Dew-Point and Dry-Bulb | T_dp < seuil ET T_ext < seuil | ±1°C |

## Limites Hautes Typiques par Zone Climatique

| Zone Climatique | Limite Dry-Bulb | Limite Enthalpie |
|-----------------|-----------------|------------------|
| 1A-4A (chaud humide) | 21°C | 47 kJ/kg |
| 4B-6B (sec) | 24°C | 52 kJ/kg |
| 5C-8 (froid) | 21°C | 47 kJ/kg |

## Sources
- [PNNL Air-Side Economizers Best Practices](https://www.pnnl.gov/projects/om-best-practices/air-side-economizers) - Guide d'exploitation et maintenance
- [Johnson Controls Enthalpy Economizer](https://docs.johnsoncontrols.com/bas/api/khub/documents/Bt~aJcHXOwQ1XS7_KA_gBg/content) - Contrôle enthalpique
- [ASHRAE Guideline 36 Addendum](https://www.ashrae.org/file library/technical resources/standards and guidelines/standards addenda/g36_2018_s_20210224.pdf) - Séquences haute performance
- [PNNL Building Re-Tuning Guide](https://buildingretuning.pnnl.gov/documents/pnnl_sa_86706.pdf) - Guide de réglage économiseur
- [Trane Engineers Newsletter](https://www.trane.com/content/dam/Trane/Commercial/global/products-systems/education-training/engineers-newsletters/airside-design/ADM-APN054-EN_05202015.pdf) - Conception économiseurs
