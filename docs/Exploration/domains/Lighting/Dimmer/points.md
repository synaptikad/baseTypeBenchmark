# Points - Dimmer

## Résumé
- **Points de mesure** : 6
- **Points de commande** : 7
- **Points d'état** : 8
- **Total** : 21

## Points de Mesure (Capteurs)

| Code | Nom | Quantité | Unité | Plage | Fréquence | Description |
|------|-----|----------|-------|-------|-----------|-------------|
| DIMMER_LEVEL_FB | Retour Niveau Gradation | 1-12 | % | 0-100 | COV | Niveau réel de gradation appliqué (feedback) |
| DIMMER_POWER | Puissance Consommée | 1-12 | W | 0-3000 | 1 min | Puissance électrique consommée par canal |
| DIMMER_ENERGY | Énergie Cumulée | 1-12 | kWh | 0-999999 | 15 min | Compteur d'énergie cumulée par canal |
| DIMMER_CURRENT | Courant Charge | 1-12 | A | 0-15 | 1 min | Courant électrique de la charge |
| DIMMER_TEMP | Température Dissipateur | 1 | °C | 0-100 | 5 min | Température du dissipateur thermique |
| DIMMER_HOURS | Heures Fonctionnement | 1-12 | h | 0-999999 | 1 hour | Heures cumulées de fonctionnement par canal |

## Points de Commande

| Code | Nom | Quantité | Unité | Plage | Type | Description |
|------|-----|----------|-------|-------|------|-------------|
| DIMMER_CMD | Commande Niveau | 1-12 | % | 0-100 | Analog | Consigne de niveau de gradation (0-100%) |
| DIMMER_ON_OFF | Marche/Arrêt | 1-12 | - | 0-1 | Digital | Commande binaire marche (1) ou arrêt (0) |
| DIMMER_FADE_TIME | Temps de Transition | 1-12 | sec | 0-60 | Analog | Durée de la transition vers le nouveau niveau |
| DIMMER_FADE_RATE | Vitesse de Gradation | 1-12 | %/s | 1-100 | Analog | Vitesse de variation de l'intensité |
| DIMMER_MIN_LEVEL | Niveau Minimum | 1-12 | % | 0-30 | Analog | Niveau de gradation minimum autorisé |
| DIMMER_MAX_LEVEL | Niveau Maximum | 1-12 | % | 50-100 | Analog | Niveau de gradation maximum autorisé |
| DIMMER_CURVE | Courbe de Gradation | 1-12 | - | 0-3 | Multi-State | Type de courbe: Linéaire/Log/Exp/Custom |

## Points d'État

| Code | Nom | Type | Valeurs | Fréquence | Description |
|------|-----|------|---------|-----------|-------------|
| DIMMER_STATUS | État Dimmer | Enum | On/Off/Dimming/Fault | COV | État opérationnel du dimmer |
| DIMMER_LOAD_TYPE | Type de Charge | Enum | LED/Incandescent/Halogen/Fluorescent | On Request | Type de charge détecté ou configuré |
| DIMMER_OVERLOAD | Surcharge | Binary | Normal/Overload | COV | Détection de surcharge sur le canal |
| DIMMER_OVERHEAT | Surchauffe | Binary | Normal/Overheat | COV | Température dissipateur excessive |
| DIMMER_SHORT_CIRCUIT | Court-Circuit | Binary | Normal/Short | COV | Détection de court-circuit |
| DIMMER_LOAD_FAULT | Défaut Charge | Binary | Normal/Fault | COV | Défaut de la charge connectée (lampe grillée) |
| DIMMER_MODE | Mode Opératoire | Enum | Auto/Manual/Scene/Override | COV | Mode de fonctionnement actuel |
| DIMMER_COMM_STATUS | État Communication | Enum | Online/Offline/Fault | COV | État de communication DALI/BACnet/Modbus |

## Points d'Alarme

| Code | Nom | Sévérité | Condition | Description |
|------|-----|----------|-----------|-------------|
| DIMMER_ALM_OVERLOAD | Alarme Surcharge | Majeure | OVERLOAD = 1 | Courant de charge supérieur au nominal |
| DIMMER_ALM_OVERHEAT | Alarme Surchauffe | Critique | TEMP > 85°C | Température dissipateur excessive, risque de coupure |
| DIMMER_ALM_SHORT | Alarme Court-Circuit | Critique | SHORT_CIRCUIT = 1 | Court-circuit détecté sur la sortie |
| DIMMER_ALM_LOAD | Alarme Défaut Charge | Mineure | LOAD_FAULT = 1 | Lampe grillée ou charge déconnectée |
| DIMMER_ALM_COMM | Alarme Communication | Majeure | COMM_STATUS = Fault | Perte de communication avec contrôleur |
| DIMMER_ALM_CONFIG | Alarme Configuration | Mineure | Type charge incompatible | Configuration dimmer incompatible avec charge |

## Sources
- [L-DALI: BACnet/DALI Controllers - LOYTEC](https://www.loytec.com/products/dali/56-l-dali-bacnet)
- [DALION: DALI Room Lighting Application Controller - bacmove](https://bacmove.com/bacnet-dali-on/)
- [Everything You Need to Know About DALI Dimming - LEDYi Lighting](https://www.ledyilighting.com/everything-you-need-to-know-about-dali-dimming/)
- [DALI Gateways & Integration with KNX, BACnet & IoT - KNX Hub](https://www.knxhub.com/dali-gateways-integration-knx-bacnet-iot/)
- IEC 62386 - DALI standard series
- NEMA SSL 7A - Phase-cut dimming for LED lamps
