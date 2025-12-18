# Contacteur (Contactor / Relay)

## Identifiant
- **Code** : CONTACTOR
- **Haystack** : relay, actuator
- **Brick** : Relay

## Description
Appareil électromécanique de commutation permettant d'ouvrir et fermer un circuit électrique de puissance par une commande à distance. Utilisé pour l'enclenchement et le déclenchement de charges importantes (moteurs, chauffage, éclairage) depuis un système d'automatisme ou de gestion technique.

## Fonction
Commander à distance l'alimentation d'équipements électriques. Permet l'automatisation, le délestage, la programmation horaire et l'intégration des charges dans les systèmes GTB/GTC. Essentiel pour les stratégies d'optimisation énergétique et le pilotage centralisé.

## Variantes Courantes
- **Contacteur de puissance** : Commutation moteurs, chauffage (9-1000A)
- **Contacteur modulaire** : Montage rail DIN pour tableaux (16-63A)
- **Contacteur jour/nuit** : Programmation horaire simple
- **Contacteur avec auxiliaires** : Retours d'état pour supervision
- **Contacteur statique** : Commutation électronique sans usure

## Caractéristiques Techniques Typiques
- Courant nominal : 9A à 1000A
- Tension de commande : 24V DC, 230V AC
- Catégorie d'emploi : AC-1 (résistif), AC-3 (moteurs), AC-5 (LED)
- Endurance : 1 à 10 millions de manoeuvres
- Contacts auxiliaires : NO/NF pour retour d'état
- Communication : Via contacts secs, modules de communication
- Temps de commutation : 10-50ms

## Localisation Typique
- Tableaux électriques divisionnaires
- Armoires de commande CVC
- Coffrets éclairage
- Tableaux de distribution étages
- Armoires pompes et ventilateurs

## Relations avec Autres Équipements
- **Commande** : Moteurs, chauffages, éclairages, prises pilotées
- **Alimenté par** : Circuit puissance + circuit commande
- **Contrôlé par** : Automates GTB, horloges, détecteurs, systèmes BMS
- **Protégé par** : Disjoncteurs, relais thermiques

## Quantité Typique par Bâtiment
- Petit (5 étages) : 20-50
- Moyen (15 étages) : 50-150
- Grand (30+ étages) : 150-400

## Sources
- Brick Schema (Relay class)
- Haystack v4 (relay, actuator tags)
- Standards IEC 60947-4-1 (contacteurs)
- Documentation technique automatisme électrique
