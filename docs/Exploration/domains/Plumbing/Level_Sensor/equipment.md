# Level Sensor

## Identifiant
- **Code** : LEVEL-SNS
- **Haystack** : `water`, `level`, `sensor`, `equip`
- **Brick** : `brick:Water_Level_Sensor`

## Description
Capteur mesurant le niveau d'eau dans les réservoirs, ballons, puisards et cuves. Permet le monitoring des volumes stockés, la gestion du remplissage/vidange, et la protection contre débordements ou fonctionnement à sec.

## Fonction
Mesurer en continu ou par seuils le niveau d'eau dans les capacités, transmettre les données au système de contrôle, gérer automatiquement les vannes de remplissage et pompes de vidange, déclencher des alarmes en cas de niveau anormal.

## Variantes Courantes
- **Flotteur mécanique** : Simple, fiable, contacts TOR
- **Capteur ultrasonique** : Sans contact, mesure continue
- **Capteur de pression hydrostatique** : Immergé, précis
- **Sonde capacitive** : Détection présence/absence par niveaux
- **Radar guidé (TDR)** : Haute précision, conditions difficiles
- **Capteur optique** : Compact, multi-points

## Caractéristiques Techniques Typiques
- Plage de mesure : 0-10m (fonction hauteur capacité)
- Précision : ±5mm (ultrasonique), ±1mm (pression)
- Sortie : Contact sec, 4-20mA, 0-10V, Modbus, BACnet
- Installation : Montage vertical haut de cuve ou immergé
- Matériaux : Inox, PVDF (contact eau potable)
- Alimentation : 24VDC, batterie (wireless)

## Localisation Typique
- Water Tank (réserve eau froide)
- DHW Tank (niveau eau chaude)
- Rainwater Harvesting Tank (gestion récupération)
- Greywater System (stockage eau traitée)
- Sump Pump (puisard, gestion vidange)
- Expansion Tank (optionnel)

## Relations avec Autres Équipements
- **Alimente** : N/A (capteur)
- **Alimenté par** : N/A
- **Contrôlé par** : Automate gestion remplissage/vidange, supervision
- **Associé à** : Motorized Valve (remplissage), Sump Pump (vidange), Potable Water Pump, alarmes

## Quantité Typique par Bâtiment
- Petit (5 étages) : 2-5 capteurs (réservoirs principaux)
- Moyen (15 étages) : 5-12 capteurs (multi-réservoirs + puisards)
- Grand (30+ étages) : 12-30 capteurs (tous réservoirs + gestion multi-zones)

## Sources
- Haystack Project - Level sensors
- Brick Schema - Level_Sensor class
- ISA standards - Level measurement
- Tank monitoring and automation standards
