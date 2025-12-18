# Points - Fluorescent Luminaire

## Résumé
- **Points de mesure** : 8
- **Points de commande** : 5
- **Points d'État** : 8
- **Total** : 21

## Points de Mesure (Capteurs)

| Code | Nom | Quantité | Unité | Plage | Fréquence | Description |
|------|-----|----------|-------|-------|-----------|-------------|
| FLUOR_LEVEL_FB | Retour Niveau Lumineux | 1 | % | 0-100 | COV | Niveau d'intensité lumineuse réel (feedback) |
| FLUOR_POWER | Puissance Consommée | 1 | W | 0-120 | 1 min | Puissance électrique consommée par le luminaire |
| FLUOR_ENERGY | Énergie Cumulée | 1 | kWh | 0-99999 | 15 min | Énergie totale consommée depuis installation |
| FLUOR_LAMP_HOURS | Heures Fonctionnement Lampe | 1 | hour | 0-30000 | 1 hour | Heures cumulées de fonctionnement du tube |
| FLUOR_BALLAST_HOURS | Heures Fonctionnement Ballast | 1 | hour | 0-50000 | 1 hour | Heures cumulées de fonctionnement du ballast |
| FLUOR_START_COUNT | Compteur Allumages | 1 | - | 0-999999 | On Change | Nombre de cycles d'allumage du luminaire |
| FLUOR_BURN_IN_TIME | Temps de Rodage | 1 | hour | 0-100 | 1 hour | Heures de rodage effectuées (100h requis avant dimming) |
| FLUOR_TEMP | Température Ballast | 1 | °C | 0-90 | 5 min | Température du ballast électronique |

## Points de Commande

| Code | Nom | Quantité | Unité | Plage | Type | Description |
|------|-----|----------|-------|-------|------|-------------|
| FLUOR_CMD | Commande Niveau | 1 | % | 0-100 | Analog | Consigne de niveau d'intensité lumineuse (0-100%) |
| FLUOR_ON_OFF | Marche/Arrêt | 1 | - | 0-1 | Digital | Commande binaire marche (1) ou arrêt (0) |
| FLUOR_DIM_ENABLE | Activation Dimming | 1 | - | 0-1 | Digital | Autorisation de la gradation (après rodage 100h) |
| FLUOR_MIN_LEVEL | Niveau Minimum | 1 | % | 10-30 | Analog | Niveau de gradation minimum autorisé |
| FLUOR_FADE_TIME | Temps de Transition | 1 | sec | 0-60 | Analog | Durée de transition vers nouveau niveau |

## Points d'État

| Code | Nom | Type | Valeurs | Fréquence | Description |
|------|-----|------|---------|-----------|-------------|
| FLUOR_STATUS | État Luminaire | Enum | On/Off/Dimming/Fault | COV | État opérationnel du luminaire fluorescent |
| FLUOR_LAMP_STATUS | État Tube Fluorescent | Enum | OK/Fault/End-of-Life/Missing | COV | État du tube fluorescent |
| FLUOR_BALLAST_STATUS | État Ballast | Enum | OK/Fault/Overheat | COV | État du ballast électronique |
| FLUOR_BALLAST_TYPE | Type de Ballast | Enum | Electronic/Magnetic/DALI | On Request | Type de ballast installé |
| FLUOR_DIMMABLE | Gradation Disponible | Binary | Yes/No | On Request | Capacité de gradation du ballast |
| FLUOR_BURN_IN_COMPLETE | Rodage Complet | Binary | Complete/Incomplete | COV | Indique si le rodage de 100h est terminé |
| FLUOR_LAMP_LIFE_REMAIN | Durée Vie Restante | Float | 0-100 | Daily | Pourcentage de durée de vie restante du tube |
| FLUOR_COMM_STATUS | État Communication | Enum | Online/Offline/Fault | COV | État de communication DALI/DSI |

## Points d'Alarme

| Code | Nom | Sévérité | Condition | Description |
|------|-----|----------|-----------|-------------|
| FLUOR_ALM_LAMP_FAULT | Alarme Défaut Lampe | Majeure | LAMP_STATUS = Fault | Tube fluorescent défectueux |
| FLUOR_ALM_LAMP_EOL | Alarme Fin de Vie Lampe | Mineure | LAMP_HOURS > 25000 | Tube approche fin de vie (>25000h) |
| FLUOR_ALM_BALLAST | Alarme Défaut Ballast | Critique | BALLAST_STATUS = Fault | Ballast électronique en défaut |
| FLUOR_ALM_OVERHEAT | Alarme Surchauffe Ballast | Majeure | TEMP > 80°C | Température ballast excessive |
| FLUOR_ALM_COMM | Alarme Communication | Mineure | COMM_STATUS = Fault | Perte de communication avec contrôleur |
| FLUOR_ALM_START_FAIL | Alarme Échec Allumage | Mineure | START_COUNT incrementé sans allumage | Échec d'allumage du tube |

## Sources
- [L-DALI: BACnet/DALI Controllers - LOYTEC](https://www.loytec.com/products/dali/56-l-dali-bacnet)
- [Understand BACnet communications for control and monitoring of networked lighting - LEDs Magazine](https://www.ledsmagazine.com/smart-lighting-iot/article/16695631/understand-bacnet-communications-for-control-and-monitoring-of-networked-lighting)
- [The Role of BACnet in lighting controls integration - Calon Controls](https://caloncontrols.com/lighting-controls-integration/)
- IEC 60929 - Electronic ballasts for tubular fluorescent lamps
- IEC 62386 - DALI standard series
- DALI Alliance - Fluorescent ballast control specifications
