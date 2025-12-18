# Air Quality Sensor (Capteur de qualité d'air)

## Identifiant
- **Code** : AQS / IAQ
- **Haystack** : `airQualitySensor-equip`
- **Brick** : `brick:Air_Quality_Sensor`

## Description
Capteur mesurant un ou plusieurs paramètres de qualité de l'air intérieur (CO2, COV, particules fines, humidité, température). Utilisé pour la ventilation à la demande (DCV), le monitoring IAQ, et l'optimisation énergétique.

## Fonction
Mesurer les indicateurs de qualité d'air intérieur pour piloter la ventilation, alerter sur les conditions dégradées, et assurer le confort et la santé des occupants. Permet d'optimiser l'énergie via la ventilation à la demande.

## Variantes Courantes
- **Capteur CO2** : Mesure concentration CO2 (indicateur d'occupation)
- **Capteur COV** : Mesure composés organiques volatils
- **Capteur PM2.5/PM10** : Mesure particules fines
- **Capteur multi-paramètres** : CO2 + COV + T° + HR
- **Capteur en gaine** : Installation dans gaine d'air
- **Capteur ambiant** : Installation murale en zone
- **Capteur portable** : Mesures ponctuelles

## Caractéristiques Techniques Typiques
- CO2 : 0 - 5,000 ppm (précision ±50 ppm)
- COV : 0 - 2,000 ppb ou équivalent CO2
- PM2.5 : 0 - 500 µg/m³
- Température : -10 - 50°C
- Humidité : 0 - 100% RH
- Protocoles : BACnet, Modbus, LON, 0-10V, 4-20mA
- Points de supervision : mesures temps réel, index qualité air

## Localisation Typique
- Zones occupées (murs, plafonds)
- Gaines de reprise d'air
- Gaines d'air neuf
- Salles de réunion, open spaces

## Relations avec Autres Équipements
- **Alimente** : N/A (capteur passif)
- **Alimenté par** : 24VAC/DC, PoE
- **Contrôlé par** : BMS (lecture des valeurs)
- **Interagit avec** : AHU, VAV, MAU, Dampers (ventilation à la demande)

## Quantité Typique par Bâtiment
- Petit (5 étages) : 10-30 capteurs
- Moyen (15 étages) : 30-100 capteurs
- Grand (30+ étages) : 100-500 capteurs

## Sources
- ASHRAE Standard 62.1 - Ventilation for IAQ
- WELL Building Standard - Air Quality
- Siemens / Honeywell / Schneider - IAQ Sensors
- Project Haystack - Air Quality Tags
