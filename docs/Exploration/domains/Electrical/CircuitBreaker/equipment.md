# Disjoncteur Intelligent (Smart Circuit Breaker / Communicating Circuit Breaker)

## Identifiant
- **Code** : CB
- **Haystack** : breaker, switch
- **Brick** : Circuit_Breaker

## Description
Dispositif de protection électrique qui interrompt automatiquement le courant en cas de surcharge ou de court-circuit. Les disjoncteurs intelligents modernes intègrent des capacités de mesure, communication et commande à distance, permettant supervision et contrôle depuis un système de gestion technique.

## Fonction
Protéger les circuits électriques contre les surintensités et courts-circuits. Permettre l'isolation manuelle ou automatique de circuits pour maintenance ou sécurité. Dans leur version communicante, ils fournissent des mesures électriques et permettent le délestage, la commande à distance et la remontée d'alarmes.

## Variantes Courantes
- **Disjoncteur modulaire communicant** : Rail DIN avec Modbus/KNX (6-125A)
- **Disjoncteur boîtier** : MCCB avec communication (125-1600A)
- **Disjoncteur ouvert** : ACB avec contrôleur électronique (630-6300A)
- **Disjoncteur différentiel** : Protection personnes + surintensité
- **Disjoncteur motorisé** : Télécommande ouverture/fermeture

## Caractéristiques Techniques Typiques
- Courant nominal : 6A à 6300A
- Pouvoir de coupure : 3kA à 150kA (Icu)
- Types : B, C, D, MA (courbes déclenchement)
- Communication : Modbus RTU/TCP, KNX, BACnet, contacts secs
- Mesures : I, P, kWh (sur modèles avancés)
- Commande : Manuelle, motorisée, électronique
- Signalisation : Position, défaut, alarme prédéclenchement

## Localisation Typique
- TGBT (départs principaux)
- Tableaux divisionnaires
- Armoires électriques
- Coffrets de distribution
- À tous niveaux de la distribution électrique

## Relations avec Autres Équipements
- **Protège** : Tous circuits en aval (câbles, équipements)
- **Alimenté par** : Jeu de barres, circuits amont
- **Contrôlé par** : GTB/GTC, système de délestage, relais protection
- **Associé à** : Compteurs d'énergie, contacteurs, relais

## Quantité Typique par Bâtiment
- Petit (5 étages) : 50-150
- Moyen (15 étages) : 200-500
- Grand (30+ étages) : 500-2000

## Sources
- Brick Schema (Circuit_Breaker class)
- Haystack v4 (breaker, switch tags)
- Standards IEC 60947-2 (disjoncteurs BT)
- Documentation technique protection électrique
