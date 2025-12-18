# Chiller (Refroidisseur d'eau)

## Identifiant
- **Code** : CH / CHW
- **Haystack** : `chiller-equip`
- **Brick** : `brick:Chiller`

## Description
Machine frigorifique qui produit de l'eau glacée (typiquement 5-7°C) pour alimenter les systèmes de climatisation du bâtiment. Utilise un cycle frigorifique à compression ou absorption pour refroidir l'eau.

## Fonction
Production centralisée d'eau glacée pour les besoins de refroidissement du bâtiment (AHU, FCU, Chilled Beams, etc.). Rejette la chaleur vers une cooling tower ou un aérorefroidisseur.

## Variantes Courantes
- **Chiller à compression** : Compresseur électrique (centrifuge, scroll, vis)
- **Chiller à absorption** : Utilise la chaleur comme source d'énergie (gaz, vapeur)
- **Chiller refroidi par air** : Condenseur à air (air-cooled)
- **Chiller refroidi par eau** : Condenseur à eau, nécessite une cooling tower
- **Chiller à vitesse variable** : Avec VFD pour modulation de capacité
- **Chiller avec free-cooling intégré** : Peut refroidir sans compresseur en hiver

## Caractéristiques Techniques Typiques
- Puissance frigorifique : 100 kW - 5 MW (30 - 1,400 TR)
- COP/EER : 2.5 - 7.0 selon technologie
- Fluide frigorigène : R134a, R410A, R1234ze, R513A
- Débit d'eau glacée : 50 - 1,000 m³/h
- Protocoles : BACnet, Modbus, LON, propriétaire
- Points de supervision : température eau glacée entrée/sortie, puissance, COP, alarmes, mode opératoire

## Localisation Typique
- Sous-sol technique (plantroom)
- Toiture (pour chillers refroidis par air)
- Local technique dédié

## Relations avec Autres Équipements
- **Alimente** : AHU, FCU, Chilled Beams, Radiant Panels (circuit eau glacée)
- **Alimenté par** : Cooling Tower (eau condenseur), Pompes primaires/secondaires
- **Contrôlé par** : Plant Controller, BMS
- **Interagit avec** : Pompes, Vannes, Systèmes de gestion d'énergie

## Quantité Typique par Bâtiment
- Petit (5 étages) : 1-2 unités
- Moyen (15 étages) : 2-4 unités (redondance)
- Grand (30+ étages) : 4-8 unités (banc de chillers)

## Sources
- Haystack Project - Chilled Water Plant
- Brick Schema - Chiller Equipment
- BACnet Standard - Central Plant Control
- ASHRAE Handbook - HVAC Systems (Chilled Water Systems)
