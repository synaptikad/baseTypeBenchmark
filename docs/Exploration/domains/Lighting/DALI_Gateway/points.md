# Points - DALI Gateway

## Résumé
- **Points de mesure** : 8
- **Points de commande** : 6
- **Points d'état** : 12
- **Total** : 26

## Points de Mesure (Capteurs)

| Code | Nom | Quantité | Unité | Plage | Fréquence | Description |
|------|-----|----------|-------|-------|-----------|-------------|
| DALI_GW_PWR | Puissance Totale DALI | 1 | W | 0-2000 | 1 min | Consommation électrique totale de la ligne DALI |
| DALI_GW_ENERGY | Énergie Consommée | 1 | kWh | 0-999999 | 15 min | Compteur d'énergie cumulée de la ligne DALI |
| DALI_GW_V_LINE | Tension Ligne DALI | 1 | V | 0-22 | 5 min | Tension sur le bus DALI (nominal 16V) |
| DALI_GW_I_LINE | Courant Ligne DALI | 1 | mA | 0-300 | 5 min | Courant total sur le bus DALI (max 250mA) |
| DALI_GW_TEMP | Température Interne | 1 | °C | -10-70 | 5 min | Température interne du gateway |
| DALI_GW_DEVICE_CNT | Nombre Dispositifs Actifs | 1 | - | 0-64 | 1 min | Nombre de dispositifs DALI détectés et opérationnels |
| DALI_GW_LAMP_FAIL_CNT | Compteur Défauts Lampes | 1 | - | 0-64 | 1 min | Nombre de lampes/luminaires en défaut |
| DALI_GW_BALLAST_FAIL_CNT | Compteur Défauts Ballasts | 1 | - | 0-64 | 1 min | Nombre de ballasts/drivers en défaut |

## Points de Commande

| Code | Nom | Quantité | Unité | Plage | Type | Description |
|------|-----|----------|-------|-------|------|-------------|
| DALI_GW_SCAN | Scan Bus DALI | 1 | - | 0-1 | Digital | Lancement d'un scan pour détecter les dispositifs DALI |
| DALI_GW_RESET | Réinitialisation Gateway | 1 | - | 0-1 | Digital | Réinitialisation logicielle du gateway |
| DALI_GW_GROUP_LVL | Niveau Groupe DALI | 16 | % | 0-100 | Analog | Commande de niveau d'intensité par groupe (1-16) |
| DALI_GW_SCENE_RECALL | Rappel Scène DALI | 16 | - | 0-15 | Multi-State | Activation d'une scène DALI préprogrammée (0-15) |
| DALI_GW_EMERGENCY_TEST | Test Éclairage Secours | 1 | - | 0-2 | Multi-State | Lancement test fonction/durée éclairage secours |
| DALI_GW_ADDR_LVL | Niveau Adresse Individuelle | 64 | % | 0-100 | Analog | Commande de niveau par adresse DALI (0-63) |

## Points d'État

| Code | Nom | Type | Valeurs | Fréquence | Description |
|------|-----|------|---------|-----------|-------------|
| DALI_GW_STATUS | État Gateway | Enum | Online/Offline/Error | COV | État général de communication du gateway |
| DALI_GW_COMM_FAULT | Défaut Communication | Binary | Normal/Fault | COV | Défaut de communication avec le système superviseur |
| DALI_GW_LINE_FAULT | Défaut Ligne DALI | Binary | Normal/Fault | COV | Court-circuit ou défaut électrique sur la ligne DALI |
| DALI_GW_OVERVOLT | Surtension Ligne | Binary | Normal/Overvoltage | COV | Détection de surtension sur le bus DALI |
| DALI_GW_OVERLOAD | Surcharge Ligne | Binary | Normal/Overload | COV | Courant ligne DALI supérieur à 250mA |
| DALI_GW_FW_VERSION | Version Firmware | String | x.x.x | On Request | Version du firmware du gateway |
| DALI_GW_DEVICE_STATUS | État Dispositifs DALI | Array[64] | OK/Fault/Missing | 1 min | État individuel de chaque adresse DALI (0-63) |
| DALI_GW_LAMP_STATUS | État Lampes | Array[64] | OK/Fail/Missing | 1 min | État des lampes par adresse DALI |
| DALI_GW_BALLAST_STATUS | État Ballasts | Array[64] | OK/Fail/Missing | 1 min | État des ballasts/drivers par adresse DALI |
| DALI_GW_GROUP_STATUS | État Groupes | Array[16] | Enabled/Disabled | On Request | Configuration des groupes DALI (1-16) |
| DALI_GW_SCENE_STATUS | État Scènes | Array[16] | Configured/Empty | On Request | Configuration des scènes DALI (0-15) |
| DALI_GW_UPTIME | Temps de Fonctionnement | Counter | 0-999999 | 1 hour | Heures de fonctionnement depuis dernière réinitialisation |

## Points d'Alarme

| Code | Nom | Sévérité | Condition | Description |
|------|-----|----------|-----------|-------------|
| DALI_GW_ALM_COMM | Alarme Communication | Majeure | COMM_FAULT = 1 | Perte de communication avec le système superviseur |
| DALI_GW_ALM_LINE | Alarme Ligne DALI | Critique | LINE_FAULT = 1 | Court-circuit ou rupture de la ligne DALI |
| DALI_GW_ALM_OVERVOLT | Alarme Surtension | Majeure | OVERVOLT = 1 | Tension ligne DALI > 22V |
| DALI_GW_ALM_OVERLOAD | Alarme Surcharge | Majeure | OVERLOAD = 1 | Courant ligne > 250mA |
| DALI_GW_ALM_TEMP | Alarme Température | Mineure | TEMP > 60°C | Température interne excessive |
| DALI_GW_ALM_DEVICE_FAIL | Alarme Défaut Dispositif | Mineure | DEVICE_FAIL_CNT > 0 | Un ou plusieurs dispositifs DALI en défaut |
| DALI_GW_ALM_LAMP_FAIL | Alarme Défaut Lampe | Mineure | LAMP_FAIL_CNT > 0 | Une ou plusieurs lampes en défaut |
| DALI_GW_ALM_BALLAST_FAIL | Alarme Défaut Ballast | Mineure | BALLAST_FAIL_CNT > 0 | Un ou plusieurs ballasts/drivers en défaut |

## Sources
- [DALI-2 to BACnet/IP Server Gateway - HMS Networks](https://www.hms-networks.com/p/inbacdal0640500-dali-2-to-bacnet-ip-server-gateway)
- [L-DALI: BACnet/DALI Controllers - LOYTEC](https://www.loytec.com/products/dali/56-l-dali-bacnet)
- [DALI Gateways & Integration with KNX, BACnet & IoT - KNX Hub](https://www.knxhub.com/dali-gateways-integration-knx-bacnet-iot/)
- [DALION: DALI Room Lighting Application Controller - bacmove](https://bacmove.com/bacnet-dali-on/)
- IEC 62386 - Digital Addressable Lighting Interface (DALI) standard
- BACnet standard ASHRAE 135
