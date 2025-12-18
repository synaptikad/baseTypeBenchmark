# Points - LED Luminaire

## Résumé
- **Points de mesure** : 12
- **Points de commande** : 8
- **Points d'État** : 10
- **Total** : 30

## Points de Mesure (Capteurs)

| Code | Nom | Quantité | Unité | Plage | Fréquence | Description |
|------|-----|----------|-------|-------|-----------|-------------|
| LED_LEVEL_FB | Retour Niveau Lumineux | 1 | % | 0-100 | COV | Niveau d'intensité lumineuse réel (feedback) |
| LED_POWER | Puissance Consommée | 1 | W | 0-200 | 1 min | Puissance électrique consommée par le luminaire |
| LED_ENERGY | Énergie Cumulée | 1 | kWh | 0-99999 | 15 min | Énergie totale consommée depuis installation |
| LED_CURRENT | Courant LED | 1 | mA | 0-5000 | 1 min | Courant d'alimentation des LED |
| LED_VOLTAGE | Tension LED | 1 | V | 0-48 | 1 min | Tension d'alimentation des LED |
| LED_HOURS | Heures Fonctionnement | 1 | hour | 0-100000 | 1 hour | Heures cumulées de fonctionnement du luminaire |
| LED_TEMP_DRIVER | Température Driver | 1 | °C | 0-100 | 5 min | Température du driver LED |
| LED_TEMP_MODULE | Température Module LED | 1 | °C | 0-90 | 5 min | Température du module LED |
| LED_FLUX_OUTPUT | Flux Lumineux | 1 | lm | 0-20000 | 1 min | Flux lumineux émis par le luminaire |
| LED_CCT | Température Couleur | 1 | K | 2700-6500 | COV | Température de couleur actuelle (tunable white) |
| LED_COLOR_X | Coordonnée Couleur X | 1 | - | 0-1 | COV | Coordonnée chromatique x (RGB/RGBW) |
| LED_COLOR_Y | Coordonnée Couleur Y | 1 | - | 0-1 | COV | Coordonnée chromatique y (RGB/RGBW) |

## Points de Commande

| Code | Nom | Quantité | Unité | Plage | Type | Description |
|------|-----|----------|-------|-------|------|-------------|
| LED_CMD | Commande Niveau | 1 | % | 0-100 | Analog | Consigne de niveau d'intensité lumineuse (0-100%) |
| LED_ON_OFF | Marche/Arrêt | 1 | - | 0-1 | Digital | Commande binaire marche (1) ou arrêt (0) |
| LED_CCT_CMD | Commande Température Couleur | 1 | K | 2700-6500 | Analog | Consigne de température de couleur (tunable white) |
| LED_RGB_R | Commande Rouge | 1 | - | 0-255 | Analog | Niveau de rouge (RGB/RGBW) |
| LED_RGB_G | Commande Vert | 1 | - | 0-255 | Analog | Niveau de vert (RGB/RGBW) |
| LED_RGB_B | Commande Bleu | 1 | - | 0-255 | Analog | Niveau de bleu (RGB/RGBW) |
| LED_FADE_TIME | Temps de Transition | 1 | sec | 0-60 | Analog | Durée de transition vers nouveau niveau/couleur |
| LED_MIN_LEVEL | Niveau Minimum | 1 | % | 0-10 | Analog | Niveau de gradation minimum autorisé |

## Points d'État

| Code | Nom | Type | Valeurs | Fréquence | Description |
|------|-----|------|---------|-----------|-------------|
| LED_STATUS | État Luminaire | Enum | On/Off/Dimming/Fault | COV | État opérationnel du luminaire LED |
| LED_DRIVER_STATUS | État Driver LED | Enum | OK/Fault/Overheat/Offline | COV | État du driver LED (D4i diagnostics) |
| LED_MODULE_STATUS | État Module LED | Enum | OK/Degraded/Fault | COV | État du module/strip LED |
| LED_DRIVER_TYPE | Type de Driver | Enum | DALI/DALI-2/0-10V/PWM | On Request | Type de driver/contrôle installé |
| LED_COLOR_MODE | Mode Couleur | Enum | Fixed/Tunable-White/RGB/RGBW | On Request | Capacité de variation de couleur |
| LED_LIFE_REMAIN | Durée Vie Restante | Float | 0-100 | Daily | Pourcentage de durée de vie restante estimé |
| LED_DEGRADATION | Dégradation Flux | Float | 0-30 | Daily | Pourcentage de dégradation du flux lumineux (L70) |
| LED_SENSOR_PRESENT | Capteur Intégré | Binary | Yes/No | On Request | Présence de capteur occupation/lumière intégré |
| LED_SENSOR_OCC | Occupation Détectée | Binary | Occupied/Vacant | COV | État d'occupation (si capteur intégré) |
| LED_COMM_STATUS | État Communication | Enum | Online/Offline/Fault | COV | État de communication DALI/BACnet |

## Points d'Alarme

| Code | Nom | Sévérité | Condition | Description |
|------|-----|----------|-----------|-------------|
| LED_ALM_DRIVER | Alarme Défaut Driver | Critique | DRIVER_STATUS = Fault | Driver LED en défaut ou hors ligne |
| LED_ALM_MODULE | Alarme Défaut Module | Majeure | MODULE_STATUS = Fault | Module LED défectueux |
| LED_ALM_OVERHEAT_DRV | Alarme Surchauffe Driver | Majeure | TEMP_DRIVER > 90°C | Température driver excessive |
| LED_ALM_OVERHEAT_MOD | Alarme Surchauffe Module | Majeure | TEMP_MODULE > 80°C | Température module LED excessive |
| LED_ALM_DEGRADATION | Alarme Dégradation Flux | Mineure | DEGRADATION > 20% | Dégradation flux lumineux significative (>L80) |
| LED_ALM_EOL | Alarme Fin de Vie | Mineure | HOURS > 80000 ou LIFE_REMAIN < 20% | Luminaire approche fin de vie estimée |
| LED_ALM_COMM | Alarme Communication | Mineure | COMM_STATUS = Fault | Perte de communication avec contrôleur |
| LED_ALM_OVERVOLTAGE | Alarme Surtension | Majeure | VOLTAGE > 50V | Surtension détectée sur alimentation LED |
| LED_ALM_UNDERVOLTAGE | Alarme Sous-tension | Majeure | VOLTAGE < 10V | Sous-tension détectée sur alimentation LED |

## Sources
- [L-DALI: BACnet/DALI Controllers - LOYTEC](https://www.loytec.com/products/dali/56-l-dali-bacnet)
- [BACnet Data Point Testing - Dynalite](https://docs.dynalite.com/system-builder/latest/ethernet_gateways/bacnet/bacnet_testing.html)
- [DALI Gateways & Integration with KNX, BACnet & IoT - KNX Hub](https://www.knxhub.com/dali-gateways-integration-knx-bacnet-iot/)
- [DALI Ballasts & Drivers Guide - KNX Hub](https://www.knxhub.com/dali-ballasts-drivers-guide/)
- [DALI Data (251/252/253) Driver - Bridgelux](https://www.bridgelux.com/dali-data-251252253-driver)
- IEC 62386 - DALI standard series
- DALI Alliance - D4i specification for diagnostics
