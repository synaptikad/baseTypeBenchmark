# Points de Récupérateur de Chaleur Sensible (HRV - Heat Recovery Ventilator)

## Synthèse
- **Total points mesure** : 10
- **Total points commande** : 5
- **Total points état** : 6

## Points de Mesure (Capteurs)

| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| oa_entering_temp | outside entering air temp sensor | °C | -20-45 | 1min | Température air neuf avant récupération |
| oa_leaving_temp | outside leaving air temp sensor | °C | -10-35 | 1min | Température air neuf après récupération |
| exhaust_entering_temp | exhaust entering air temp sensor | °C | 18-28 | 1min | Température air extrait avant récupération |
| exhaust_leaving_temp | exhaust leaving air temp sensor | °C | 0-35 | 1min | Température air extrait après récupération |
| supply_flow | supply air flow sensor | m³/h | 300-30000 | 1min | Débit air neuf |
| exhaust_flow | exhaust air flow sensor | m³/h | 300-30000 | 1min | Débit air extrait |
| sensible_efficiency | sensible efficiency sensor | % | 50-95 | 5min | Efficacité sensible calculée |
| filter_dp | filter differential pressure sensor | Pa | 50-500 | 5min | Pression différentielle filtres |
| supply_fan_speed | supply fan speed sensor | % | 0-100 | 1min | Vitesse ventilateur soufflage |
| exhaust_fan_speed | exhaust fan speed sensor | % | 0-100 | 1min | Vitesse ventilateur extraction |

## Points de Commande (Actionneurs/Consignes)

| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| supply_fan_speed_cmd | supply fan speed cmd | % | 0-100 | Actionneur | Vitesse ventilateur soufflage |
| exhaust_fan_speed_cmd | exhaust fan speed cmd | % | 0-100 | Actionneur | Vitesse ventilateur extraction |
| bypass_damper_cmd | bypass damper cmd | % | 0-100 | Actionneur | Position registre bypass |
| enable_cmd | enable cmd | - | 0/1 | Actionneur | Commande marche/arrêt unité |
| defrost_enable_cmd | defrost enable cmd | - | 0/1 | Actionneur | Activation mode dégivrage |

## Points d'État

| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| supply_fan_run | supply fan run status | Boolean | true/false | Ventilateur soufflage en marche |
| exhaust_fan_run | exhaust fan run status | Boolean | true/false | Ventilateur extraction en marche |
| bypass_active | bypass active status | Boolean | true/false | Mode bypass actif (échangeur court-circuité) |
| defrost_active | defrost run status | Boolean | true/false | Dégivrage en cours |
| frost_alarm | frost alarm | Boolean | true/false | Alarme risque de givre |
| unit_fault | unit fault alarm | Boolean | true/false | Défaut général unité |

## Mappings Protocoles

| Point | BACnet Object | Modbus Register | KNX GA |
|-------|---------------|-----------------|--------|
| oa_entering_temp | AI:1 | 40001 (HR) | 1/1/1 |
| oa_leaving_temp | AI:2 | 40002 (HR) | 1/1/2 |
| exhaust_entering_temp | AI:3 | 40003 (HR) | 1/1/3 |
| exhaust_leaving_temp | AI:4 | 40004 (HR) | 1/1/4 |
| supply_flow | AI:5 | 40005 (HR) | 1/1/5 |
| exhaust_flow | AI:6 | 40006 (HR) | 1/1/6 |
| sensible_efficiency | AV:1 | 40101 (HR) | 1/1/7 |
| filter_dp | AI:7 | 40007 (HR) | 1/1/8 |
| supply_fan_speed | AI:8 | 40008 (HR) | 1/1/9 |
| exhaust_fan_speed | AI:9 | 40009 (HR) | 1/1/10 |
| supply_fan_speed_cmd | AO:1 | 40201 (HR) | 1/2/1 |
| exhaust_fan_speed_cmd | AO:2 | 40202 (HR) | 1/2/2 |
| bypass_damper_cmd | AO:3 | 40203 (HR) | 1/2/3 |
| enable_cmd | BO:1 | 00001 (Coil) | 1/2/4 |
| defrost_enable_cmd | BO:2 | 00002 (Coil) | 1/2/5 |
| supply_fan_run | BI:1 | 10001 (DI) | 1/3/1 |
| exhaust_fan_run | BI:2 | 10002 (DI) | 1/3/2 |
| bypass_active | BI:3 | 10003 (DI) | 1/3/3 |
| defrost_active | BI:4 | 10004 (DI) | 1/3/4 |
| frost_alarm | BI:5 | 10005 (DI) | 1/3/5 |
| unit_fault | BI:6 | 10006 (DI) | 1/3/6 |

**Notes sur les mappings :**
- BACnet : AI = Analog Input, AO = Analog Output, AV = Analog Value, BI = Binary Input, BO = Binary Output, MSV = Multi-State Value
- Modbus : HR = Holding Register (40001+), Coil = Digital Output (00001+), DI = Discrete Input (10001+)
- KNX : GA = Group Address (format Area/Line/Device)

## Différences HRV vs ERV

| Caractéristique | HRV | ERV |
|-----------------|-----|-----|
| Transfert chaleur sensible | Oui | Oui |
| Transfert humidité (latent) | Non | Oui |
| Application climat | Climats secs | Climats humides |
| Type échangeur | Plaques aluminium/roue thermique | Membrane perméable/roue enthalpique |

## Calcul d'Efficacité Sensible

| Formule | Description |
|---------|-------------|
| η_s = (T_oa_out - T_oa_in) / (T_exh_in - T_oa_in) | Efficacité basée sur l'air neuf (hiver) |
| η_s = (T_exh_in - T_exh_out) / (T_exh_in - T_oa_in) | Efficacité basée sur l'air extrait |

## Sources
- ASHRAE Handbook - Heat Recovery Systems
- Project Haystack - HRV Equipment Tags
- Brick Schema - Heat_Recovery_Ventilator Class
- CSA C439 - Standard for Rating the Performance of Heat-Recovery Ventilators
