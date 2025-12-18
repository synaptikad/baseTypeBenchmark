# Heat Pump (Pompe à Chaleur)

## Identifiant
- **Code** : HP / PAC
- **Haystack** : `heatPump-equip`
- **Brick** : `brick:Heat_Pump`

## Description
Système réversible qui peut à la fois chauffer et refroidir en transférant la chaleur d'un milieu à un autre. Utilise un cycle frigorifique inversible pour extraire la chaleur de l'air, de l'eau ou du sol.

## Fonction
Production de chaud et/ou de froid pour le conditionnement d'air du bâtiment. Alternative énergétiquement efficace aux systèmes séparés (chaudière + chiller).

## Variantes Courantes
- **PAC Air-Eau** : Puise calories dans l'air extérieur, produit eau chaude/glacée
- **PAC Air-Air** : Puise calories dans l'air, distribue air conditionné
- **PAC Eau-Eau** : Source géothermique (sondes, nappe phréatique)
- **PAC réversible** : Chaud et froid (majoritaire dans le tertiaire)
- **PAC haute température** : Eau chaude 60-70°C pour retrofit
- **PAC hybride** : Couplée avec chaudière gaz

## Caractéristiques Techniques Typiques
- Puissance thermique : 10 kW - 1 MW
- COP chauffage : 2.5 - 5.0 (selon température extérieure)
- EER refroidissement : 2.5 - 4.5
- Température eau chaude : 35-70°C
- Température eau glacée : 5-15°C
- Protocoles : BACnet, Modbus, LON
- Points de supervision : modes (chaud/froid), températures, puissances, COP, défauts

## Localisation Typique
- Toiture (unité extérieure)
- Local technique (unité intérieure ou groupe compact)
- Extérieur bâtiment (unité extérieure Air-Air)

## Relations avec Autres Équipements
- **Alimente** : AHU, FCU, Planchers chauffants/rafraîchissants, Radiateurs
- **Alimenté par** : Réseau électrique, Source géothermique (si eau-eau)
- **Contrôlé par** : Régulation intégrée, BMS
- **Interagit avec** : Pompes, Vannes, Ballons tampons, Appoint électrique/gaz

## Quantité Typique par Bâtiment
- Petit (5 étages) : 1-5 unités
- Moyen (15 étages) : 5-15 unités
- Grand (30+ étages) : 15-40 unités

## Sources
- Haystack Project - Heat Pump Equipment
- Brick Schema - Heat Pump Classes
- BACnet Standard - Heat Pump Applications
- ASHRAE Handbook - Heat Pump Systems
