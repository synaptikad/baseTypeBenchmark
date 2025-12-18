# Points - Daylight Harvesting Controller

## Résumé
- **Points de mesure** : 10
- **Points de commande** : 8
- **Points d'état** : 8
- **Total** : 26

## Points de Mesure (Capteurs)

| Code | Nom | Quantité | Unité | Plage | Fréquence | Description |
|------|-----|----------|-------|-------|-----------|-------------|
| DAYLIGHT_LUX_INDOOR | Éclairement Intérieur | 1-10 | lux | 0-2000 | 10 sec | Niveau de lumière mesuré par photocellules intérieures |
| DAYLIGHT_LUX_OUTDOOR | Éclairement Extérieur | 1 | lux | 0-100000 | 30 sec | Niveau de lumière extérieure (mode open-loop) |
| DAYLIGHT_LUX_TARGET | Consigne Éclairement | 1 | lux | 200-1000 | On Change | Niveau d'éclairement cible configuré |
| DAYLIGHT_LUX_ACTUAL | Éclairement Résultant | 1-10 | lux | 0-2000 | 10 sec | Niveau d'éclairement total (naturel + artificiel) |
| DAYLIGHT_DIM_LEVEL | Niveau Dimming Appliqué | 1-20 | % | 0-100 | 1 min | Niveau de gradation appliqué aux luminaires |
| DAYLIGHT_ENERGY | Énergie Économisée | 1 | kWh | 0-999999 | 15 min | Énergie économisée grâce au daylight harvesting |
| DAYLIGHT_POWER | Puissance Éclairage | 1-20 | W | 0-5000 | 1 min | Puissance consommée par zone contrôlée |
| DAYLIGHT_SAVINGS_PCT | Pourcentage Économie | 1 | % | 0-100 | 15 min | Pourcentage d'économie d'énergie vs éclairage max |
| DAYLIGHT_LOOP_ERROR | Erreur de Régulation | 1-10 | lux | -500-500 | 10 sec | Écart entre consigne et valeur mesurée |
| DAYLIGHT_TIME_RESP | Temps de Réponse | 1 | sec | 10-300 | On Change | Temps de réponse configuré du contrôleur |

## Points de Commande

| Code | Nom | Quantité | Unité | Plage | Type | Description |
|------|-----|----------|-------|-------|------|-------------|
| DAYLIGHT_ENABLE | Activation Contrôle | 1 | - | 0-1 | Digital | Activation/désactivation du daylight harvesting |
| DAYLIGHT_SET_TARGET | Réglage Consigne | 1-10 | lux | 200-1000 | Analog | Définition du niveau d'éclairement cible |
| DAYLIGHT_MODE | Mode Opératoire | 1 | - | 0-3 | Multi-State | Mode: Off/Open-Loop/Closed-Loop/Hybrid |
| DAYLIGHT_DEADBAND | Bande Morte | 1-10 | lux | 10-100 | Analog | Seuil d'hystérésis pour éviter oscillations |
| DAYLIGHT_RAMP_RATE | Vitesse Gradation | 1-20 | %/s | 1-10 | Analog | Vitesse de variation de l'intensité lumineuse |
| DAYLIGHT_MIN_DIM | Dimming Minimum | 1-20 | % | 0-30 | Analog | Niveau minimum de gradation autorisé |
| DAYLIGHT_OVERRIDE | Override Manuel | 1 | - | 0-1 | Digital | Activation du mode override temporaire |
| DAYLIGHT_CALIBRATE | Calibration Auto | 1 | - | 0-1 | Digital | Lancement de la calibration automatique |

## Points d'État

| Code | Nom | Type | Valeurs | Fréquence | Description |
|------|-----|------|---------|-----------|-------------|
| DAYLIGHT_STATUS | État Contrôleur | Enum | Active/Inactive/Override/Fault | COV | État opérationnel du contrôleur |
| DAYLIGHT_SENSOR_STATUS | État Capteurs | Array | OK/Fault/Missing | 1 min | État de chaque photocellule connectée |
| DAYLIGHT_ZONE_STATUS | État Zones | Array | Controlled/Manual/Off | COV | État de chaque zone de contrôle |
| DAYLIGHT_CALIBRATED | État Calibration | Binary | Calibrated/Not Calibrated | On Change | Indique si le système est calibré |
| DAYLIGHT_OVERRIDE_TIME | Temps Override Restant | Counter | 0-3600 | 1 min | Temps restant en mode override (secondes) |
| DAYLIGHT_CONTROL_MODE | Mode Actif | Enum | Closed-Loop/Open-Loop/Hybrid/Manual | COV | Mode de contrôle actuellement actif |
| DAYLIGHT_SAVINGS_TODAY | Économies Jour | Float | 0-999 | 1 hour | Énergie économisée aujourd'hui (kWh) |
| DAYLIGHT_UPTIME | Temps Fonctionnement | Counter | 0-999999 | 1 hour | Heures de fonctionnement du contrôleur |

## Points d'Alarme

| Code | Nom | Sévérité | Condition | Description |
|------|-----|----------|-----------|-------------|
| DAYLIGHT_ALM_SENSOR | Alarme Capteur Défectueux | Majeure | SENSOR_STATUS = Fault | Un ou plusieurs capteurs de lumière en défaut |
| DAYLIGHT_ALM_COMM | Alarme Communication | Majeure | Perte comm > 5 min | Perte de communication avec le BMS |
| DAYLIGHT_ALM_CALIB | Alarme Calibration | Mineure | CALIBRATED = 0 | Système non calibré, performance dégradée |
| DAYLIGHT_ALM_ZONE_FAULT | Alarme Défaut Zone | Mineure | ZONE_STATUS = Fault | Une ou plusieurs zones en défaut |
| DAYLIGHT_ALM_SETPOINT | Alarme Consigne Non Atteinte | Mineure | ABS(LOOP_ERROR) > 100 lux pendant > 10 min | Impossible d'atteindre la consigne d'éclairement |
| DAYLIGHT_ALM_OVERRIDE_LONG | Alarme Override Prolongé | Mineure | OVERRIDE_TIME > 2 heures | Mode override actif depuis trop longtemps |

## Sources
- [DALION: DALI Room Lighting Application Controller - bacmove](https://bacmove.com/bacnet-dali-on/)
- [L-DALI: BACnet/DALI Controllers - LOYTEC](https://www.loytec.com/products/dali/56-l-dali-bacnet)
- [MACH-ProLight BACnet Controller - Reliable Controls](https://www.reliablecontrols.com/products/controllers/MPL/)
- [Aura Interior BACnet Sensors - Touch-Plate](https://touchplate.com/product/aura-interior-bacnet-sensors/)
- ASHRAE 90.1 - Energy Standard for Buildings (daylight control requirements)
- California Title 24 - Daylighting control requirements
- IEC 62386-304 - DALI light sensor control interface
