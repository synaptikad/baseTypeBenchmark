# Points - Lighting Relay

## Résumé
- **Points de mesure** : 7
- **Points de commande** : 5
- **Points d'État** : 8
- **Total** : 20

## Points de Mesure (Capteurs)

| Code | Nom | Quantité | Unité | Plage | Fréquence | Description |
|------|-----|----------|-------|-------|-----------|-------------|
| RELAY_STATUS_FB | Retour État Relais | 1-16 | - | 0-1 | COV | État réel du contact relais (0=ouvert, 1=fermé) |
| RELAY_CURRENT | Courant Charge | 1-16 | A | 0-30 | 1 min | Courant électrique traversant le relais |
| RELAY_POWER | Puissance Charge | 1-16 | W | 0-6600 | 1 min | Puissance de la charge commutée |
| RELAY_ENERGY | Énergie Cumulée | 1-16 | kWh | 0-99999 | 15 min | Énergie totale commutée par le relais |
| RELAY_CYCLES | Compteur Commutations | 1-16 | - | 0-10000000 | On Change | Nombre de cycles de commutation effectués |
| RELAY_ON_TIME | Temps Marche Cumulé | 1-16 | hour | 0-999999 | 1 hour | Heures cumulées en position fermée (ON) |
| RELAY_TEMP | Température Module | 1 | °C | 0-80 | 5 min | Température du module de relais |

## Points de Commande

| Code | Nom | Quantité | Unité | Plage | Type | Description |
|------|-----|----------|-------|-------|------|-------------|
| RELAY_CMD | Commande Relais | 1-16 | - | 0-1 | Digital | Commande d'ouverture (0) ou fermeture (1) du relais |
| RELAY_PULSE | Commande Impulsion | 1-16 | sec | 0.1-60 | Analog | Fermeture temporaire du relais (durée en secondes) |
| RELAY_PRIORITY | Priorité Commande | 1-16 | - | 0-16 | Multi-State | Niveau de priorité BACnet (1=manuel, 8=auto, 16=min) |
| RELAY_RELINQUISH | Abandon Priorité | 1-16 | - | 0-1 | Digital | Libération de la priorité de commande courante |
| RELAY_RESET_COUNTERS | RAZ Compteurs | 1-16 | - | 0-1 | Digital | Réinitialisation des compteurs cycles et heures |

## Points d'État

| Code | Nom | Type | Valeurs | Fréquence | Description |
|------|-----|------|---------|-----------|-------------|
| RELAY_STATUS | État Relais | Enum | Open/Closed/Fault/Unknown | COV | État opérationnel du contact relais |
| RELAY_MODE | Mode Opératoire | Enum | Auto/Manual/Override/Schedule | COV | Mode de fonctionnement du relais |
| RELAY_TYPE | Type de Relais | Enum | Electromechanical/SSR/Latching/Contactor | On Request | Type de relais installé |
| RELAY_LOAD_TYPE | Type de Charge | Enum | Resistive/Inductive/LED/Fluorescent | On Request | Type de charge connectée |
| RELAY_OVERLOAD | Surcharge Détectée | Binary | Normal/Overload | COV | Détection de surcharge sur le contact |
| RELAY_CONTACT_WEAR | Usure Contacts | Float | 0-100 | Daily | Estimation de l'usure des contacts (%) |
| RELAY_LIFE_REMAIN | Durée Vie Restante | Float | 0-100 | Daily | Pourcentage de durée de vie restante estimée |
| RELAY_COMM_STATUS | État Communication | Enum | Online/Offline/Fault | COV | État de communication avec contrôleur |

## Points d'Alarme

| Code | Nom | Sévérité | Condition | Description |
|------|-----|----------|-----------|-------------|
| RELAY_ALM_FAULT | Alarme Défaut Relais | Critique | STATUS = Fault | Relais défectueux ou collé |
| RELAY_ALM_OVERLOAD | Alarme Surcharge | Majeure | CURRENT > nominal + 20% | Courant de charge excessif |
| RELAY_ALM_OVERHEAT | Alarme Surchauffe | Majeure | TEMP > 70°C | Température module excessive |
| RELAY_ALM_CONTACT_WEAR | Alarme Usure Contacts | Mineure | CONTACT_WEAR > 80% | Contacts approchent fin de vie |
| RELAY_ALM_CYCLES_HIGH | Alarme Cycles Élevés | Mineure | CYCLES > 80% durée vie nominale | Nombre élevé de commutations |
| RELAY_ALM_COMM | Alarme Communication | Majeure | COMM_STATUS = Fault | Perte de communication avec contrôleur |
| RELAY_ALM_NO_LOAD | Alarme Absence Charge | Mineure | STATUS = Closed && CURRENT = 0 | Relais fermé mais pas de courant détecté |
| RELAY_ALM_STUCK | Alarme Relais Collé | Critique | Commande != Status pendant > 10 sec | Relais ne répond pas aux commandes |

## Sources
- [LightLEEDer Advanced BACnet-IP Gateway Module - ILC](https://www.ilc-usa.com/LLABG)
- [BACnet Integration Guide - Acuity Brands](https://www.acuitybrands.com/brands/lighting-controls/-/media/abl/acuitybrands/files/synergy/spec-docs/bacnet-integration-interoperation-guide.pdf)
- [BACnet Integration - zencontrol](https://zencontrol.com/bacnet/)
- [BACnet Supra Universal 32 Relay Panel - Touch-Plate](https://touchplate.com/product/supra-universal-bacnet-32-relay-panel/)
- [MACH-ProLight BACnet Controller - Reliable Controls](https://www.reliablecontrols.com/products/controllers/MPL/)
- IEC 61810 - Electromechanical elementary relays
- UL 508 - Industrial control equipment (relay modules)
