# Boiler (Chaudière)

## Identifiant
- **Code** : BLR / HW
- **Haystack** : `boiler-equip`
- **Brick** : `brick:Boiler`

## Description
Générateur de chaleur qui produit de l'eau chaude ou de la vapeur pour alimenter les systèmes de chauffage du bâtiment. Utilise généralement du gaz naturel, du fioul, ou de l'électricité comme source d'énergie.

## Fonction
Production centralisée d'eau chaude (60-90°C) ou de vapeur pour les besoins de chauffage du bâtiment (AHU, FCU, radiateurs, planchers chauffants, etc.).

## Variantes Courantes
- **Chaudière eau chaude** : Circuit eau chaude basse ou haute température
- **Chaudière vapeur** : Production de vapeur (basse ou haute pression)
- **Chaudière à condensation** : Récupère la chaleur latente (rendement >95%)
- **Chaudière modulante** : Puissance variable selon besoin
- **Chaudière électrique** : Résistances électriques (appoint ou principal)
- **Chaudière biomasse** : Combustible renouvelable (granulés, bois)

## Caractéristiques Techniques Typiques
- Puissance thermique : 50 kW - 10 MW
- Rendement : 85-98% (selon technologie)
- Température eau chaude : 60-90°C (bâtiments tertiaires)
- Pression vapeur : 1-15 bar (si vapeur)
- Combustible : Gaz naturel, fioul, électricité, biomasse
- Protocoles : BACnet, Modbus, LON
- Points de supervision : température départ/retour, puissance, rendement, débit, alarmes

## Localisation Typique
- Sous-sol technique (chaufferie)
- Local technique dédié avec ventilation
- Réglementation stricte (distance sécurité, ventilation)

## Relations avec Autres Équipements
- **Alimente** : AHU, FCU, Radiateurs, Planchers chauffants, Préchauffage air neuf
- **Alimenté par** : Réseau gaz, Cuve fioul, Réseau électrique
- **Contrôlé par** : Plant Controller, BMS, Régulation cascade
- **Interagit avec** : Pompes de circulation, Vannes, Ballons tampons

## Quantité Typique par Bâtiment
- Petit (5 étages) : 1-2 unités
- Moyen (15 étages) : 2-4 unités (redondance)
- Grand (30+ étages) : 4-8 unités (banc de chaudières)

## Sources
- Haystack Project - Hot Water Plant
- Brick Schema - Boiler Equipment
- BACnet Standard - Central Plant Control
- ASHRAE Handbook - Heating Systems
