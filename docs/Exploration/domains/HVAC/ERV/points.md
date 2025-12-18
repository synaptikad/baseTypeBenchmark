# Points de Récupérateur d'Énergie (ERV - Energy Recovery Ventilator)

## Synthèse
- **Total points mesure** : 14
- **Total points commande** : 6
- **Total points état** : 7

## Points de Mesure (Capteurs)

| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| oa_entering_temp | outside entering air temp sensor | °C | -20-45 | 1min | Température air neuf avant récupération |
| oa_leaving_temp | outside leaving air temp sensor | °C | -10-35 | 1min | Température air neuf après récupération |
| oa_entering_humidity | outside entering air humidity sensor | %RH | 10-100 | 1min | Humidité air neuf avant récupération |
| oa_leaving_humidity | outside leaving air humidity sensor | %RH | 20-80 | 1min | Humidité air neuf après récupération |
| exhaust_entering_temp | exhaust entering air temp sensor | °C | 18-28 | 1min | Température air extrait avant récupération |
| exhaust_leaving_temp | exhaust leaving air temp sensor | °C | 5-35 | 1min | Température air extrait après récupération |
| exhaust_entering_humidity | exhaust entering air humidity sensor | %RH | 30-70 | 1min | Humidité air extrait avant récupération |
| exhaust_leaving_humidity | exhaust leaving air humidity sensor | %RH | 30-90 | 1min | Humidité air extrait après récupération |
| supply_flow | supply air flow sensor | m³/h | 500-50000 | 1min | Débit air neuf |
| exhaust_flow | exhaust air flow sensor | m³/h | 500-50000 | 1min | Débit air extrait |
| wheel_speed | wheel speed sensor | rpm | 0-30 | 1min | Vitesse rotation roue enthalpique |
| sensible_efficiency | sensible efficiency sensor | % | 40-90 | 5min | Efficacité sensible calculée |
| total_efficiency | total efficiency sensor | % | 30-80 | 5min | Efficacité totale (enthalpique) calculée |
| filter_dp | filter differential pressure sensor | Pa | 50-500 | 5min | Pression différentielle filtres |

## Points de Commande (Actionneurs/Consignes)

| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| supply_fan_speed_cmd | supply fan speed cmd | % | 0-100 | Actionneur | Vitesse ventilateur soufflage |
| exhaust_fan_speed_cmd | exhaust fan speed cmd | % | 0-100 | Actionneur | Vitesse ventilateur extraction |
| wheel_speed_cmd | wheel speed cmd | % | 0-100 | Actionneur | Vitesse rotation roue |
| bypass_damper_cmd | bypass damper cmd | % | 0-100 | Actionneur | Position registre bypass |
| enable_cmd | enable cmd | - | 0/1 | Actionneur | Commande marche/arrêt unité |
| defrost_enable_cmd | defrost enable cmd | - | 0/1 | Actionneur | Activation mode dégivrage |

## Points d'État

| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| supply_fan_run | supply fan run status | Boolean | true/false | Ventilateur soufflage en marche |
| exhaust_fan_run | exhaust fan run status | Boolean | true/false | Ventilateur extraction en marche |
| wheel_run | wheel run status | Boolean | true/false | Roue en rotation |
| bypass_active | bypass active status | Boolean | true/false | Mode bypass actif |
| defrost_active | defrost run status | Boolean | true/false | Dégivrage en cours |
| frost_alarm | frost alarm | Boolean | true/false | Alarme risque de givre |
| unit_fault | unit fault alarm | Boolean | true/false | Défaut général unité |

## Mappings Protocoles

| Point | BACnet Object | Modbus Register | KNX GA |
|-------|---------------|-----------------|--------|
| oa_entering_temp | AI:1 | 40001 (HR) | 1/1/1 |
| oa_leaving_temp | AI:2 | 40002 (HR) | 1/1/2 |
| oa_entering_humidity | AI:3 | 40003 (HR) | 1/1/3 |
| oa_leaving_humidity | AI:4 | 40004 (HR) | 1/1/4 |
| exhaust_entering_temp | AI:5 | 40005 (HR) | 1/1/5 |
| exhaust_leaving_temp | AI:6 | 40006 (HR) | 1/1/6 |
| exhaust_entering_humidity | AI:7 | 40007 (HR) | 1/1/7 |
| exhaust_leaving_humidity | AI:8 | 40008 (HR) | 1/1/8 |
| supply_flow | AI:9 | 40009 (HR) | 1/1/9 |
| exhaust_flow | AI:10 | 40010 (HR) | 1/1/10 |
| wheel_speed | AI:11 | 40011 (HR) | 1/1/11 |
| sensible_efficiency | AV:1 | 40101 (HR) | 1/1/12 |
| total_efficiency | AV:2 | 40102 (HR) | 1/1/13 |
| filter_dp | AI:12 | 40012 (HR) | 1/1/14 |
| supply_fan_speed_cmd | AO:1 | 40201 (HR) | 1/2/1 |
| exhaust_fan_speed_cmd | AO:2 | 40202 (HR) | 1/2/2 |
| wheel_speed_cmd | AO:3 | 40203 (HR) | 1/2/3 |
| bypass_damper_cmd | AO:4 | 40204 (HR) | 1/2/4 |
| enable_cmd | BO:1 | 00001 (Coil) | 1/2/5 |
| defrost_enable_cmd | BO:2 | 00002 (Coil) | 1/2/6 |
| supply_fan_run | BI:1 | 10001 (DI) | 1/3/1 |
| exhaust_fan_run | BI:2 | 10002 (DI) | 1/3/2 |
| wheel_run | BI:3 | 10003 (DI) | 1/3/3 |
| bypass_active | BI:4 | 10004 (DI) | 1/3/4 |
| defrost_active | BI:5 | 10005 (DI) | 1/3/5 |
| frost_alarm | BI:6 | 10006 (DI) | 1/3/6 |
| unit_fault | BI:7 | 10007 (DI) | 1/3/7 |

**Notes sur les mappings :**
- BACnet : AI = Analog Input, AO = Analog Output, AV = Analog Value, BI = Binary Input, BO = Binary Output, MSV = Multi-State Value
- Modbus : HR = Holding Register (40001+), Coil = Digital Output (00001+), DI = Discrete Input (10001+)
- KNX : GA = Group Address (format Area/Line/Device)

## Calcul d'Efficacité

| Type | Formule | Application |
|------|---------|-------------|
| Efficacité sensible | η_s = (T_oa_out - T_oa_in) / (T_exh_in - T_oa_in) | Transfert de chaleur |
| Efficacité latente | η_l = (w_oa_out - w_oa_in) / (w_exh_in - w_oa_in) | Transfert d'humidité |
| Efficacité totale | η_t = (h_oa_out - h_oa_in) / (h_exh_in - h_oa_in) | Transfert enthalpie |

## Modes de Fonctionnement

| Condition | Mode | Action |
|-----------|------|--------|
| T_ext < -5°C | Dégivrage | Réduction vitesse roue ou bypass partiel |
| T_ext entre limites économiseur | Bypass | Roue arrêtée, bypass ouvert |
| T_ext > limite chauffage ou T_ext < limite refroid. | Récupération | Roue active, bypass fermé |

## Sources
- [RenewAire BACnet Fan Control](https://renewaire.com/bacnetfancontrol/) - Contrôle BACnet pour ERV
- [Greenheck Energy Recovery Application Manual](https://content.greenheck.com/public/DAMProd/Original/10002/ERVApplManual_catalog.pdf) - Guide d'application
- [How ERVs Work - RenewAire](https://renewaire.com/how-ervs-work/) - Fonctionnement des ERV
- [AHRI Energy Recovery Ventilators](https://www.ahrinet.org/scholarships-education/education/contractors-and-specifiers/hvacr-equipmentcomponents/air-air-energy-recovery-ventilators-ervs) - Standards AHRI
- [DRI Rotors ERV Systems](https://www.drirotors.com/product/energy-recovery-ventilators-erv/) - Roues enthalpiques
