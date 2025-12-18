# Chilled Beam (Poutre froide)

## Identifiant
- **Code** : CB / CHLB
- **Haystack** : `chilledBeam-equip`
- **Brick** : `brick:Chilled_Beam`

## Description
Terminal HVAC installé au plafond qui conditionne l'air d'une zone principalement par convection naturelle (passive) ou forcée (active) via un échangeur eau glacée. Complété par un apport d'air neuf primaire traité (débit réduit).

## Fonction
Assurer le refroidissement et parfois le chauffage d'une zone avec un débit d'air primaire réduit (économie énergie ventilateurs), en utilisant l'eau glacée comme vecteur principal. Efficace pour charges sensibles élevées.

## Variantes Courantes
- **Poutre froide passive** : Convection naturelle uniquement
- **Poutre froide active** : Induction d'air de zone par jet d'air primaire
- **Poutre réversible** : Chaud et froid (eau chaude/glacée)
- **Poutre multi-services** : Intègre éclairage, diffusion air, acoustique
- **Poutre encastrée** : Intégrée au faux plafond
- **Poutre apparente** : Suspendue, visible

## Caractéristiques Techniques Typiques
- Puissance : 200 - 2,000 W par poutre
- Débit d'air primaire : 10 - 50 l/s par poutre (active uniquement)
- Température eau glacée : 14-16°C (anti-condensation)
- Température eau chaude : 35-50°C (si réversible)
- Induction ratio (active) : 1:2 à 1:4 (air primaire : air induit)
- Protocoles : BACnet, Modbus (via vannes)
- Points de supervision : température zone, vanne eau glacée, débit air primaire (si active)

## Localisation Typique
- Plafond de bureaux, salles de réunion, open spaces
- Principalement tertiaire haut de gamme

## Relations avec Autres Équipements
- **Alimente** : Zone (air conditionné)
- **Alimenté par** : Chiller (eau glacée), Boiler/Heat Pump (eau chaude si réversible), DOAS/AHU (air primaire)
- **Contrôlé par** : Vanne motorisée, Thermostat de zone, BMS
- **Interagit avec** : Pompes, Capteur humidité (anti-condensation), DOAS

## Quantité Typique par Bâtiment
- Petit (5 étages) : 20-100 poutres
- Moyen (15 étages) : 100-500 poutres
- Grand (30+ étages) : 500-2,000 poutres

## Sources
- Haystack Project - Chilled Beam Equipment
- Brick Schema - Chilled Beam Classes
- BACnet Standard - Chilled Beam Control
- ASHRAE Handbook - Chilled Beam Systems
