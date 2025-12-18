# Points - Photocell (Light Sensor)

## Résumé
- **Points de mesure** : 9
- **Points de commande** : 5
- **Points d'État** : 6
- **Total** : 20

## Points de Mesure (Capteurs)

| Code | Nom | Quantité | Unité | Plage | Fréquence | Description |
|------|-----|----------|-------|-------|-----------|-------------|
| PHOTO_LUX | Niveau Éclairement | 1 | lux | 0-100000 | 10 sec | Niveau d'éclairement ambiant mesuré |
| PHOTO_LUX_AVG | Éclairement Moyen | 1 | lux | 0-100000 | 1 min | Moyenne mobile sur 1 minute (filtrage) |
| PHOTO_LUX_MIN | Éclairement Minimum | 1 | lux | 0-100000 | 1 hour | Niveau minimum mesuré dans la dernière heure |
| PHOTO_LUX_MAX | Éclairement Maximum | 1 | lux | 0-100000 | 1 hour | Niveau maximum mesuré dans la dernière heure |
| PHOTO_LUX_NATURAL | Lumière Naturelle Estimée | 1 | lux | 0-100000 | 10 sec | Estimation de l'apport de lumière naturelle seule |
| PHOTO_LUX_ARTIFICIAL | Lumière Artificielle Estimée | 1 | lux | 0-2000 | 10 sec | Estimation de l'apport de lumière artificielle |
| PHOTO_SUNRISE_LUX | Éclairement Lever Soleil | 1 | lux | 0-20000 | Daily | Niveau d'éclairement au lever du soleil |
| PHOTO_SUNSET_LUX | Éclairement Coucher Soleil | 1 | lux | 0-20000 | Daily | Niveau d'éclairement au coucher du soleil |
| PHOTO_CLOUD_FACTOR | Facteur Nébulosité | 1 | % | 0-100 | 5 min | Estimation de la couverture nuageuse (variation lux) |

## Points de Commande

| Code | Nom | Quantité | Unité | Plage | Type | Description |
|------|-----|----------|-------|-------|------|-------------|
| PHOTO_ENABLE | Activation Capteur | 1 | - | 0-1 | Digital | Activation/désactivation de la photocellule |
| PHOTO_THRESHOLD_ON | Seuil Allumage | 1 | lux | 3-1000 | Analog | Niveau de lumière en dessous duquel allumer |
| PHOTO_THRESHOLD_OFF | Seuil Extinction | 1 | lux | 10-2000 | Analog | Niveau de lumière au-dessus duquel éteindre |
| PHOTO_DEADBAND | Bande Morte | 1 | lux | 10-100 | Analog | Hystérésis entre seuils ON et OFF |
| PHOTO_FILTER_TIME | Temps de Filtrage | 1 | sec | 1-300 | Analog | Durée de filtrage pour éviter variations rapides |

## Points d'État

| Code | Nom | Type | Valeurs | Fréquence | Description |
|------|-----|------|---------|-----------|-------------|
| PHOTO_STATUS | État Capteur | Enum | Active/Inactive/Fault/Disabled | COV | État opérationnel de la photocellule |
| PHOTO_DAYLIGHT | État Jour/Nuit | Binary | Day/Night | COV | Indique si niveau de lumière = jour ou nuit |
| PHOTO_LOCATION | Emplacement Capteur | Enum | Indoor/Outdoor/Window/Roof | On Request | Emplacement du capteur de lumière |
| PHOTO_SPECTRAL_RESPONSE | Réponse Spectrale | Enum | Broadband/V-Lambda/Custom | On Request | Type de réponse spectrale du capteur |
| PHOTO_CALIBRATION_DATE | Date Calibration | DateTime | - | On Calibration | Date de la dernière calibration |
| PHOTO_COMM_STATUS | État Communication | Enum | Online/Offline/Fault | COV | État de communication DALI/BACnet |

## Points d'Alarme

| Code | Nom | Sévérité | Condition | Description |
|------|-----|----------|-----------|-------------|
| PHOTO_ALM_FAULT | Alarme Défaut Capteur | Majeure | STATUS = Fault | Photocellule défectueuse ou hors service |
| PHOTO_ALM_COMM | Alarme Communication | Majeure | COMM_STATUS = Offline > 5 min | Perte de communication avec le capteur |
| PHOTO_ALM_OUT_OF_RANGE | Alarme Hors Plage | Mineure | LUX < 0 ou LUX > max_range | Mesure aberrante hors plage |
| PHOTO_ALM_STUCK | Alarme Valeur Bloquée | Mineure | LUX inchangé > 2 heures | Valeur ne varie pas (capteur potentiellement bloqué) |
| PHOTO_ALM_CALIBRATION | Alarme Calibration Requise | Mineure | Calibration > 1 an | Calibration nécessaire pour précision |
| PHOTO_ALM_THRESHOLD_ERROR | Alarme Erreur Seuils | Mineure | THRESHOLD_ON >= THRESHOLD_OFF | Configuration des seuils incohérente |

## Sources
- [BACnet Integration - zencontrol](https://zencontrol.com/bacnet/)
- [DALI-2 Light Level Sensor - Ozuno](https://ozuno.com/product/rapix-dali-occupancy-ll-sensor/)
- [L-DALI: BACnet/DALI Controllers - LOYTEC](https://www.loytec.com/products/dali/l-dali-wired/l-dali-bacnet)
- [Measuring Light with Photocells - Adafruit](https://learn.adafruit.com/photocells/measuring-light)
- [Outdoor Lux Meter Sensor - Current Lighting](https://www.currentlighting.com/outdoor-lux-meter-sensor/220984)
- IEC 62386-304 - DALI Part 304: Light sensor control interface
- ASHRAE 90.1 - Automatic daylight control requirements
- EN 12464 - Light and lighting standard
