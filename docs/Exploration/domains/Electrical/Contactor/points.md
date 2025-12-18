# Points - Contactor

## Résumé
- **Points de mesure** : 6
- **Points de commande** : 3
- **Points d'état** : 6
- **Total** : 15

## Points de Mesure (Capteurs)

| Code | Nom | Quantité | Unité | Plage | Fréquence | Description |
|------|-----|----------|-------|-------|-----------|-------------|
| CONT-I-L1 | Current Phase L1 | 1 | A | 0-1000 | 5s | Courant phase L1 en sortie contacteur |
| CONT-I-L2 | Current Phase L2 | 1 | A | 0-1000 | 5s | Courant phase L2 en sortie contacteur |
| CONT-I-L3 | Current Phase L3 | 1 | A | 0-1000 | 5s | Courant phase L3 en sortie contacteur |
| CONT-OP-COUNT | Operation Counter | 1 | - | 0-999999 | On event | Nombre de manoeuvres cumulées (cycles O/C) |
| CONT-ON-TIME | Total ON Time | 1 | h | 0-999999 | Hourly | Temps de fonctionnement cumulé (heures) |
| CONT-TEMP | Temperature | 1 | °C | -20 à 150 | 60s | Température bobine/contacts |

## Points de Commande

| Code | Nom | Quantité | Unité | Plage | Type | Description |
|------|-----|----------|-------|-------|------|-------------|
| CONT-CMD | Contactor Command | 1 | - | 0/1 | Binary | Commande d'ouverture (0) ou fermeture (1) |
| CONT-AUTO | Auto Mode | 1 | - | 0/1 | Binary | Mode automatique (pilotage GTB/automate) |
| CONT-RESET | Reset Counter | 1 | - | 0/1 | Binary | Réinitialisation compteurs et alarmes |

## Points d'État

| Code | Nom | Type | Valeurs | Fréquence | Description |
|------|-----|------|---------|-----------|-------------|
| CONT-STATUS | Contact Status | Binary | 0=OPEN/1=CLOSED | 1s | État des contacts principaux (retour auxiliaire) |
| CONT-READY | Ready Status | Binary | 0=NOT READY/1=READY | 5s | Contacteur prêt (pas de défaut) |
| CONT-FAULT | Fault Status | Binary | 0=OK/1=FAULT | 1s | Défaut détecté (soudure, bobine, surcharge) |
| CONT-MODE | Operating Mode | Enum | MANUAL/AUTO/FAULT | 5s | Mode de fonctionnement actuel |
| CONT-AUX-NO | Auxiliary Contact NO | Binary | 0=OPEN/1=CLOSED | 1s | Contact auxiliaire normalement ouvert |
| CONT-AUX-NC | Auxiliary Contact NC | Binary | 0=CLOSED/1=OPEN | 1s | Contact auxiliaire normalement fermé |

## Points d'Alarme

| Code | Nom | Sévérité | Condition | Description |
|------|-----|----------|-----------|-------------|
| CONT-ALM-WELD | Welded Contacts | CRITICAL | Contacts soudés | Contacts principaux soudés (ne s'ouvrent pas) |
| CONT-ALM-OVERLOAD | Overload | WARNING | I > In | Surcharge détectée sur contacts |
| CONT-ALM-TEMP | High Temperature | WARNING | T > 80°C | Température excessive bobine/contacts |
| CONT-ALM-COIL | Coil Fault | CRITICAL | Défaut bobine | Défaut bobine de commande (coupure, court-circuit) |
| CONT-ALM-PHASE-LOSS | Phase Loss | CRITICAL | Phase absente | Perte de phase en sortie |
| CONT-ALM-MAINT | Maintenance Required | WARNING | Cycles > seuil | Maintenance préventive requise (fin de vie) |
| CONT-ALM-NO-FEEDBACK | Feedback Fault | WARNING | Incohérence | Incohérence commande/retour d'état |

## Sources
- [BACnet MS/TP I/O Modules - Contemporary Controls](https://www.ccontrols.com/basautomation/iobacnet.php)
- [Reliable Controls BACnet Controllers](https://www.reliablecontrols.com/products/bacnet/)
- [Functional Devices RIB Relays](https://www.functionaldevices.com/product/RIBTWX2401B-BC)
- [Eaton CMD Contactor Monitoring Device](https://www.eaton.com/gb/en-gb/catalog/industrial-control--drives--automation---sensors/cmd-contactor-monitoring-device.html)
- [Contactor vs Relay - GEYA](https://www.geya.net/contactor-vs-relay/)
