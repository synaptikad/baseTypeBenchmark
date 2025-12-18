# Points de Capteur de Qualité d'Air (Air Quality Sensor)

## Synthèse
- **Total points mesure** : 10
- **Total points commande** : 2
- **Total points état** : 4

## Points de Mesure (Capteurs)

| Point | Tag Haystack | Unité | Plage Typique | Fréquence | Description |
|-------|--------------|-------|---------------|-----------|-------------|
| co2 | co2 sensor | ppm | 400-5000 | 1min | Concentration CO2 |
| voc | voc sensor | ppb | 0-2000 | 1min | Composés organiques volatils |
| voc_co2eq | voc co2 equivalent sensor | ppm | 400-5000 | 1min | COV en équivalent CO2 |
| pm25 | pm25 sensor | µg/m³ | 0-500 | 1min | Particules fines PM2.5 |
| pm10 | pm10 sensor | µg/m³ | 0-500 | 1min | Particules PM10 |
| temp | air temp sensor | °C | 15-35 | 1min | Température ambiante |
| humidity | air humidity sensor | %RH | 20-80 | 1min | Humidité relative |
| iaq_index | iaq index sensor | - | 0-500 | 1min | Index qualité air global |
| formaldehyde | formaldehyde sensor | ppb | 0-500 | 5min | Concentration formaldéhyde |
| ozone | ozone sensor | ppb | 0-200 | 5min | Concentration ozone |

## Points de Commande (Actionneurs/Consignes)

| Point | Tag Haystack | Unité | Plage | Type | Description |
|-------|--------------|-------|-------|------|-------------|
| co2_sp | co2 sp | ppm | 600-1200 | Consigne | Seuil CO2 pour ventilation DCV |
| calibration_cmd | calibration cmd | - | 0/1 | Actionneur | Déclenchement calibration |

## Points d'État

| Point | Tag Haystack | Type | Valeurs | Description |
|-------|--------------|------|---------|-------------|
| co2_high_alarm | co2 high alarm | Boolean | true/false | Alarme CO2 élevé |
| voc_high_alarm | voc high alarm | Boolean | true/false | Alarme COV élevé |
| pm_high_alarm | pm high alarm | Boolean | true/false | Alarme particules élevées |
| sensor_fault | sensor fault alarm | Boolean | true/false | Défaut capteur |

## Mappings Protocoles

| Point | BACnet Object | Modbus Register | Signal Analogique |
|-------|---------------|-----------------|-------------------|
| co2 | AI:1 | 40001 (HR) | 0-10V = 0-5000 ppm |
| voc | AI:2 | 40002 (HR) | 0-10V = 0-2000 ppb |
| voc_co2eq | AI:3 | 40003 (HR) | 0-10V = 0-5000 ppm |
| pm25 | AI:4 | 40004 (HR) | 0-10V = 0-500 µg/m³ |
| pm10 | AI:5 | 40005 (HR) | 0-10V = 0-500 µg/m³ |
| temp | AI:6 | 40006 (HR) | 0-10V = -10-50°C |
| humidity | AI:7 | 40007 (HR) | 0-10V = 0-100% |
| iaq_index | AV:1 | 40101 (HR) | - |
| formaldehyde | AI:8 | 40008 (HR) | - |
| ozone | AI:9 | 40009 (HR) | - |
| co2_sp | AV:2 | 40102 (HR) | - |
| calibration_cmd | BO:1 | 00001 (Coil) | - |
| co2_high_alarm | BI:1 | 10001 (DI) | Contact sec |
| voc_high_alarm | BI:2 | 10002 (DI) | Contact sec |
| pm_high_alarm | BI:3 | 10003 (DI) | Contact sec |
| sensor_fault | BI:4 | 10004 (DI) | Contact sec |

**Notes sur les mappings :**
- BACnet : AI = Analog Input, AV = Analog Value, BI = Binary Input, BO = Binary Output
- Modbus : HR = Holding Register (40001+), DI = Discrete Input (10001+)
- Analogique : 0-10V ou 4-20mA selon configuration

## Seuils ASHRAE/WELL

| Paramètre | Bon | Acceptable | Mauvais | Action DCV |
|-----------|-----|------------|---------|------------|
| CO2 | < 800 ppm | 800-1000 ppm | > 1000 ppm | Augmenter ventilation |
| COV | < 500 ppb | 500-1000 ppb | > 1000 ppb | Augmenter ventilation |
| PM2.5 | < 12 µg/m³ | 12-35 µg/m³ | > 35 µg/m³ | Filtration/ventilation |
| PM10 | < 50 µg/m³ | 50-100 µg/m³ | > 100 µg/m³ | Filtration/ventilation |

## Calcul Index IAQ

| IAQ Index | Qualité | Couleur | Action |
|-----------|---------|---------|--------|
| 0-50 | Excellente | Vert | Aucune |
| 51-100 | Bonne | Jaune-vert | Aucune |
| 101-150 | Modérée | Jaune | Surveillance |
| 151-200 | Mauvaise | Orange | Ventilation accrue |
| 201-300 | Très mauvaise | Rouge | Évacuation si prolongé |
| > 300 | Dangereuse | Violet | Évacuation |

## Sources
- ASHRAE Standard 62.1 - Ventilation for Acceptable IAQ
- WELL Building Standard v2 - Air Concept
- EPA Air Quality Index (AQI)
- Project Haystack - Air Quality Sensor Tags
