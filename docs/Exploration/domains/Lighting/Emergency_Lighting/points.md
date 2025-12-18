# Points - Emergency Lighting

## Résumé
- **Points de mesure** : 11
- **Points de commande** : 5
- **Points d'état** : 10
- **Total** : 26

## Points de Mesure (Capteurs)

| Code | Nom | Quantité | Unité | Plage | Fréquence | Description |
|------|-----|----------|-------|-------|-----------|-------------|
| EMERG_BATT_V | Tension Batterie | 1 | V | 0-48 | 5 min | Tension de la batterie de secours |
| EMERG_BATT_I | Courant Batterie | 1 | A | -5-5 | 5 min | Courant de charge/décharge batterie (+ = charge) |
| EMERG_BATT_SOC | État de Charge Batterie | 1 | % | 0-100 | 5 min | Niveau de charge de la batterie |
| EMERG_BATT_TEMP | Température Batterie | 1 | °C | -10-60 | 5 min | Température de la batterie |
| EMERG_LAMP_V | Tension Lampe Secours | 1 | V | 0-48 | 10 min | Tension d'alimentation de la lampe en mode secours |
| EMERG_LAMP_I | Courant Lampe Secours | 1 | A | 0-5 | 10 min | Courant consommé par la lampe en mode secours |
| EMERG_RUNTIME_REMAIN | Autonomie Restante | 1 | min | 0-180 | 1 min | Temps d'autonomie restant estimé |
| EMERG_RUNTIME_TOTAL | Durée Test Autonomie | 1 | min | 0-180 | On Test | Durée totale du dernier test d'autonomie |
| EMERG_CHARGE_TIME | Temps Recharge | 1 | hour | 0-48 | 1 hour | Temps de recharge depuis dernier test |
| EMERG_LAMP_HOURS | Heures Lampe Secours | 1 | hour | 0-100000 | 1 hour | Heures de fonctionnement cumulées lampe secours |
| EMERG_TEST_COUNT | Compteur Tests | 1 | - | 0-9999 | On Test | Nombre de tests effectués depuis installation |

## Points de Commande

| Code | Nom | Quantité | Unité | Plage | Type | Description |
|------|-----|----------|-------|-------|------|-------------|
| EMERG_TEST_FUNC | Test Fonctionnel | 1 | - | 0-1 | Digital | Lancement test fonctionnel court (30 sec - 5 min) |
| EMERG_TEST_DURATION | Test Autonomie | 1 | - | 0-1 | Digital | Lancement test d'autonomie complet (90-180 min) |
| EMERG_LAMP_ON | Activation Lampe Manuel | 1 | - | 0-1 | Digital | Activation manuelle de la lampe de secours |
| EMERG_INHIBIT_TEST | Inhibition Test Auto | 1 | - | 0-1 | Digital | Désactivation temporaire des tests automatiques |
| EMERG_RESET_FAULT | Réinitialisation Défauts | 1 | - | 0-1 | Digital | Acquittement et réinitialisation des alarmes |

## Points d'État

| Code | Nom | Type | Valeurs | Fréquence | Description |
|------|-----|------|---------|-----------|-------------|
| EMERG_STATUS | État Général | Enum | Normal/Emergency/Test/Fault/Charging | COV | État opérationnel de l'éclairage de secours |
| EMERG_MODE | Mode Fonctionnement | Enum | Maintained/Non-Maintained/Combined | On Request | Type de luminaire d'urgence |
| EMERG_BATT_STATUS | État Batterie | Enum | OK/Low/Charging/Fault/Missing | COV | État de la batterie de secours |
| EMERG_LAMP_STATUS | État Lampe | Enum | OK/Failed/Missing | COV | État de la lampe/LED de secours |
| EMERG_LAST_TEST_DATE | Date Dernier Test | DateTime | - | On Test | Date et heure du dernier test |
| EMERG_LAST_TEST_RESULT | Résultat Dernier Test | Enum | Pass/Fail/Partial | On Test | Résultat du dernier test d'autonomie |
| EMERG_NEXT_TEST_DATE | Prochain Test Prévu | DateTime | - | On Change | Date du prochain test automatique programmé |
| EMERG_MAINS_STATUS | État Secteur | Binary | Present/Absent | COV | Présence de l'alimentation secteur normale |
| EMERG_CHARGER_STATUS | État Chargeur | Enum | Charging/Trickle/Fault/Off | COV | État du chargeur de batterie |
| EMERG_COMPLIANCE | Conformité Réglementaire | Binary | Compliant/Non-Compliant | Daily | Conformité aux exigences réglementaires |

## Points d'Alarme

| Code | Nom | Sévérité | Condition | Description |
|------|-----|----------|-----------|-------------|
| EMERG_ALM_BATT_LOW | Alarme Batterie Faible | Critique | BATT_SOC < 20% | Batterie déchargée, autonomie insuffisante |
| EMERG_ALM_BATT_FAULT | Alarme Défaut Batterie | Critique | BATT_STATUS = Fault | Batterie défectueuse ou hors service |
| EMERG_ALM_LAMP_FAIL | Alarme Lampe Défectueuse | Critique | LAMP_STATUS = Failed | Lampe de secours grillée ou défaillante |
| EMERG_ALM_TEST_FAIL | Alarme Échec Test | Majeure | LAST_TEST_RESULT = Fail | Dernier test d'autonomie échoué |
| EMERG_ALM_CHARGER | Alarme Défaut Chargeur | Majeure | CHARGER_STATUS = Fault | Chargeur de batterie en défaut |
| EMERG_ALM_RUNTIME | Alarme Autonomie Insuffisante | Majeure | RUNTIME_TOTAL < 90 min | Autonomie mesurée inférieure à 90 minutes réglementaires |
| EMERG_ALM_TEST_OVERDUE | Alarme Test en Retard | Mineure | Test non effectué > 35 jours | Test automatique en retard |
| EMERG_ALM_MAINS_FAIL | Alarme Défaut Secteur | Info | MAINS_STATUS = Absent | Passage en mode secours (coupure secteur) |
| EMERG_ALM_COMPLIANCE | Alarme Non-Conformité | Majeure | COMPLIANCE = Non-Compliant | Non-conformité réglementaire détectée |

## Sources
- [BACnet Interface for Emergency Lighting - Teknoware](https://www.teknoware.com/en/emergency-lighting/central-monitoring-emergency-lighting/central-monitoring-central-battery-systems/bacnet-interface)
- [VisionGuard BACnet/IP Interface - Eaton](https://www.eaton.com/content/dam/eaton/products/safety-security-emergency-communications/emergency-lighting/central-battery-systems/vis/visionguard/en/eaton-ceag-el-cps-visionguard-bacnet-interface.pdf)
- [L-DALI: BACnet/DALI Controllers - LOYTEC](https://www.loytec.com/products/dali/l-dali-wired/l-dali-bacnet)
- IEC 60598-2-22 - Luminaires for emergency lighting
- IEC 62386-202 - DALI Part 202: Self-contained emergency lighting
- NFPA 101 - Life Safety Code (emergency lighting requirements)
- UL 924 - Emergency lighting and power equipment
