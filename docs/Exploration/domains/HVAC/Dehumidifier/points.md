# Points de Déshumidificateur (Dehumidifier)

## Synthèse
- **Total points mesure** : 10
- **Total points commande** : 4
- **Total points état** : 6

## Points de Mesure (Capteurs)

| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| zone_humidity | zone air humidity sensor | %RH | 30-80 | 1min | Humidité relative de la zone |
| return_humidity | return air humidity sensor | %RH | 30-80 | 1min | Humidité air de reprise |
| discharge_humidity | discharge air humidity sensor | %RH | 20-60 | 1min | Humidité air déshumidifié |
| zone_temp | zone air temp sensor | °C | 15-30 | 1min | Température de la zone |
| return_temp | return air temp sensor | °C | 15-30 | 1min | Température air reprise |
| discharge_temp | discharge air temp sensor | °C | 10-25 | 1min | Température air sortie |
| condensate_level | condensate level sensor | % | 0-100 | 5min | Niveau bac à condensats |
| condensate_flow | condensate flow sensor | l/h | 0-50 | 5min | Débit condensats évacués |
| power_consumption | elec power sensor | kW | 0-50 | 5min | Puissance électrique consommée |
| regen_temp | regen heater temp sensor | °C | 80-150 | 1min | Température régénération (roue déshydratante) |

## Points de Commande (Actionneurs/Consignes)

| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| humidity_sp | zone humidity sp | %RH | 30-70 | Consigne | Consigne humidité relative |
| dehumid_capacity_cmd | dehumidification cmd | % | 0-100 | Actionneur | Commande capacité déshumidification |
| enable_cmd | enable cmd | - | 0/1 | Actionneur | Commande marche/arrêt |
| regen_enable_cmd | regen enable cmd | - | 0/1 | Actionneur | Activation régénération (roue) |

## Points d'État

| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| unit_run | run status | Boolean | true/false | Unité en marche |
| compressor_run | compressor run status | Boolean | true/false | Compresseur en marche (type DX) |
| regen_active | regen run status | Boolean | true/false | Régénération active (roue déshydratante) |
| condensate_full_alarm | condensate high alarm | Boolean | true/false | Alarme bac condensats plein |
| condensate_pump_fault | condensate pump fault alarm | Boolean | true/false | Défaut pompe condensats |
| unit_fault | unit fault alarm | Boolean | true/false | Défaut général unité |

## Mappings Protocoles

| Point | BACnet Object | Modbus Register | KNX GA |
|-------|---------------|-----------------|--------|
| zone_humidity | AI:1 | 40001 (HR) | 1/1/1 |
| return_humidity | AI:2 | 40002 (HR) | 1/1/2 |
| discharge_humidity | AI:3 | 40003 (HR) | 1/1/3 |
| zone_temp | AI:4 | 40004 (HR) | 1/1/4 |
| return_temp | AI:5 | 40005 (HR) | 1/1/5 |
| discharge_temp | AI:6 | 40006 (HR) | 1/1/6 |
| condensate_level | AI:7 | 40007 (HR) | 1/1/7 |
| condensate_flow | AI:8 | 40008 (HR) | 1/1/8 |
| power_consumption | AI:9 | 40009 (HR) | 1/1/9 |
| regen_temp | AI:10 | 40010 (HR) | 1/1/10 |
| humidity_sp | AV:1 | 40101 (HR) | 1/2/1 |
| dehumid_capacity_cmd | AO:1 | 40201 (HR) | 1/2/2 |
| enable_cmd | BO:1 | 00001 (Coil) | 1/2/3 |
| regen_enable_cmd | BO:2 | 00002 (Coil) | 1/2/4 |
| unit_run | BI:1 | 10001 (DI) | 1/3/1 |
| compressor_run | BI:2 | 10002 (DI) | 1/3/2 |
| regen_active | BI:3 | 10003 (DI) | 1/3/3 |
| condensate_full_alarm | BI:4 | 10004 (DI) | 1/3/4 |
| condensate_pump_fault | BI:5 | 10005 (DI) | 1/3/5 |
| unit_fault | BI:6 | 10006 (DI) | 1/3/6 |

**Notes sur les mappings :**
- BACnet : AI = Analog Input, AO = Analog Output, AV = Analog Value, BI = Binary Input, BO = Binary Output, MSV = Multi-State Value
- Modbus : HR = Holding Register (40001+), Coil = Digital Output (00001+), DI = Discrete Input (10001+)
- KNX : GA = Group Address (format Area/Line/Device)

## Seuils de Contrôle Typiques

| Application | Consigne HR | Différentiel | Alarme Haute |
|-------------|-------------|--------------|--------------|
| Bureaux/Tertiaire | 50% | ±5% | 65% |
| Piscine intérieure | 60% | ±5% | 70% |
| Musée/Archives | 45% | ±3% | 55% |
| Salle blanche | 40-45% | ±3% | 50% |
| Sous-sol/Parking | 55% | ±5% | 70% |

## Sources
- [Greenheck DOAS BACnet Guide](https://content.greenheck.com/public/DAMProd/Original/10017/485940_BACnetGuide.pdf) - Points BACnet pour déshumidification DOAS
- [Greystone NTRC Series](https://shop.greystoneenergy.com/shop/ntrc-series-temphumidity-sensor-w-bacnet-and-modbus/) - Capteurs température/humidité BACnet
- [ANDIVI BACnet Sensors](https://www.andivi.com/bacnet-sensors/) - Capteurs BACnet pour HVAC
- [VisionAQ Desiccant Dehumidifiers](https://www.visionaq.com/desiccant-dehumidifiers/) - Déshumidificateurs industriels avec BACnet
