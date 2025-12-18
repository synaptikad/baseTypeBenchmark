# Water Softener

## Identifiant
- **Code** : WATER-SOFT
- **Haystack** : `water`, `softener`, `equip`
- **Brick** : `brick:Water_Treatment_Equipment` (sous-classe softener)

## Description
Équipement de traitement d'eau qui élimine les minéraux responsables de la dureté de l'eau (calcium, magnésium) par échange d'ions. Protège les équipements hydrauliques et thermiques contre l'entartrage et prolonge leur durée de vie.

## Fonction
Réduire la dureté de l'eau par passage sur résine échangeuse d'ions, régénération automatique de la résine avec sel, protection anti-tartre des équipements de production d'eau chaude, chaudières et circuits hydrauliques.

## Variantes Courantes
- **Adoucisseur volumétrique** : Régénération selon volume traité mesuré
- **Adoucisseur chronométrique** : Régénération selon temporisation programmée
- **Adoucisseur duplex** : Double bouteille pour service continu pendant régénération
- **Système anti-tartre alternatif** : Traitement magnétique ou électronique (sans sel)

## Caractéristiques Techniques Typiques
- Capacité de résine : 10-200 litres
- Débit de traitement : 1-20 m³/h
- Dureté résiduelle cible : 5-15°f (français)
- Consommation sel : 100-300g/cycle de régénération
- Fréquence régénération : 1-7 jours selon usage
- Communication : Modbus, contacts secs pour alarmes

## Localisation Typique
- Local technique arrivée d'eau
- Chaufferie (protection chaudières)
- Sous-sol technique
- Avant DHW Tank et chaudières

## Relations avec Autres Équipements
- **Alimente** : Water Heater, DHW Tank, chaudières, réseau eau
- **Alimenté par** : Réseau eau froide, Water Meter
- **Contrôlé par** : Contrôleur intégré, supervision GTB
- **Associé à** : Water Quality Sensor (dureté), saumure tank

## Quantité Typique par Bâtiment
- Petit (5 étages) : 1 adoucisseur (2-5 m³/h) si eau dure
- Moyen (15 étages) : 1-2 adoucisseurs (8-15 m³/h) duplex recommandé
- Grand (30+ étages) : 2-3 adoucisseurs (20-40 m³/h) configuration redondante

## Sources
- Haystack Project - Water treatment equipment
- Brick Schema - Water treatment classes
- Water quality standards and regulations
- Building plumbing codes
