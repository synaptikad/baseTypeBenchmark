# Points - Occupancy Sensor

## Résumé
- **Points de mesure** : 8
- **Points de commande** : 6
- **Points d'État** : 7
- **Total** : 21

## Points de Mesure (Capteurs)

| Code | Nom | Quantité | Unité | Plage | Fréquence | Description |
|------|-----|----------|-------|-------|-----------|-------------|
| OCC_OCCUPIED | Occupation Détectée | 1 | - | 0-1 | COV | État d'occupation (0=vacant, 1=occupé) |
| OCC_MOTION_LEVEL | Niveau d'Activité | 1 | % | 0-100 | 10 sec | Niveau d'activité/mouvement détecté (%) |
| OCC_MOTION_COUNT | Compteur Mouvements | 1 | - | 0-9999 | 1 min | Nombre de mouvements détectés dans la période |
| OCC_TIME_OCCUPIED | Temps Occupation | 1 | min | 0-1440 | 1 min | Durée d'occupation continue depuis détection |
| OCC_TIME_VACANT | Temps Inoccupation | 1 | min | 0-1440 | 1 min | Durée d'inoccupation depuis dernière détection |
| OCC_LUX_LEVEL | Niveau Lumineux Mesuré | 1 | lux | 0-2000 | 10 sec | Éclairement ambiant mesuré (si capteur intégré) |
| OCC_EVENTS_TODAY | Occupations Journalières | 1 | - | 0-999 | 1 hour | Nombre d'événements d'occupation aujourd'hui |
| OCC_OCCUPANCY_RATE | Taux Occupation Journalier | 1 | % | 0-100 | 1 hour | Pourcentage du temps occupé aujourd'hui |

## Points de Commande

| Code | Nom | Quantité | Unité | Plage | Type | Description |
|------|-----|----------|-------|-------|------|-------------|
| OCC_ENABLE | Activation Capteur | 1 | - | 0-1 | Digital | Activation/désactivation du capteur d'occupation |
| OCC_SENSITIVITY | Sensibilité Détection | 1 | % | 10-100 | Analog | Niveau de sensibilité de détection du mouvement |
| OCC_TIMEOUT | Délai avant Extinction | 1 | min | 0.5-30 | Analog | Temps d'attente avant déclaration d'inoccupation |
| OCC_LUX_THRESHOLD | Seuil Lumineux | 1 | lux | 10-2000 | Analog | Seuil au-dessus duquel ne pas allumer l'éclairage |
| OCC_MODE | Mode Opératoire | 1 | - | 0-2 | Multi-State | Mode: Occupancy/Vacancy/Manual-On |
| OCC_HOLD_TIME | Durée Maintien | 1 | min | 1-60 | Analog | Temps de maintien après dernière détection |

## Points d'État

| Code | Nom | Type | Valeurs | Fréquence | Description |
|------|-----|------|---------|-----------|-------------|
| OCC_STATUS | État Capteur | Enum | Active/Inactive/Fault/Disabled | COV | État opérationnel du capteur d'occupation |
| OCC_DETECTION_TYPE | Type de Détection | Enum | PIR/Ultrasonic/Dual-Tech/Microwave | On Request | Technologie de détection utilisée |
| OCC_COVERAGE_AREA | Zone de Couverture | Float | 0-2000 | On Request | Surface couverte par le capteur (sq.ft) |
| OCC_LAST_MOTION_TIME | Dernière Détection | DateTime | - | On Change | Date/heure de la dernière détection de mouvement |
| OCC_OPERATING_MODE | Mode Actif | Enum | Occupancy/Vacancy/Manual-On/Override | COV | Mode de fonctionnement actuel |
| OCC_BATT_STATUS | État Batterie | Enum | OK/Low/Replace/N/A | Daily | État de la batterie (capteurs sans fil) |
| OCC_COMM_STATUS | État Communication | Enum | Online/Offline/Fault | COV | État de communication DALI/BACnet/Zigbee |

## Points d'Alarme

| Code | Nom | Sévérité | Condition | Description |
|------|-----|----------|-----------|-------------|
| OCC_ALM_FAULT | Alarme Défaut Capteur | Majeure | STATUS = Fault | Capteur d'occupation défectueux |
| OCC_ALM_COMM | Alarme Communication | Majeure | COMM_STATUS = Offline > 5 min | Perte de communication avec le capteur |
| OCC_ALM_BATT_LOW | Alarme Batterie Faible | Mineure | BATT_STATUS = Low | Batterie faible (capteurs sans fil) |
| OCC_ALM_BATT_REPLACE | Alarme Remplacement Batterie | Majeure | BATT_STATUS = Replace | Batterie à remplacer immédiatement |
| OCC_ALM_COVERAGE | Alarme Zone Non Couverte | Mineure | Configuration zone incorrecte | Chevauchement ou zone non couverte détectée |
| OCC_ALM_NO_MOTION | Alarme Absence Activité Longue | Info | TIME_VACANT > 24 heures | Aucune occupation détectée depuis 24h (possible défaut) |

## Sources
- [DALI Network Occupancy Sensor - Honeywell](https://buildings.honeywell.com/us/en/products/by-category/sensors/occupancy-sensors/dali-network-sensor)
- [L-DALI: BACnet/DALI Controllers - LOYTEC](https://www.loytec.com/products/dali/l-dali-wired/l-dali-bacnet)
- [DALION: Room Light Control - bacmove](https://bacmove.com/support/docs/dali-on/en/room-light-control/)
- [DALI Occupancy Sensors Guide - KNX Hub](https://www.knxhub.com/dali-occupancy-sensors-types-placement-benefits/)
- [DALI-2 PIR sensors - zencontrol](https://zencontrol.com/products/pir_sensors/)
- IEC 62386-303 - DALI Part 303: Occupancy sensor control interface
- ASHRAE 90.1 - Energy standard (occupancy sensing requirements)
- California Title 24 - Lighting control requirements
