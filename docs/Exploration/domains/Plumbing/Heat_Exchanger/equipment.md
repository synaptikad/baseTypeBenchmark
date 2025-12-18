# Heat Exchanger

## Identifiant
- **Code** : HX-DHW
- **Haystack** : `domesticWater`, `hot`, `heatExchanger`, `equip`
- **Brick** : `brick:Heat_Exchanger`

## Description
Échangeur thermique qui transfère la chaleur d'un fluide primaire (eau chaude de chauffage, vapeur) vers l'eau sanitaire froide pour produire de l'eau chaude sanitaire. Sépare physiquement les deux circuits pour raisons sanitaires.

## Fonction
Chauffer l'eau sanitaire froide par transfert thermique depuis un circuit primaire (chaudière, réseau de chaleur urbain) sans mélange des fluides. Permet production instantanée ou semi-instantanée d'ECS avec efficacité énergétique élevée.

## Variantes Courantes
- **Échangeur à plaques** : Compact, haute efficacité, démontable
- **Échangeur tubulaire** : Robuste, grandes puissances
- **Échangeur instantané** : Production à la demande sans stockage
- **Échangeur semi-instantané** : Petit ballon tampon intégré
- **Échangeur solaire** : Transfert chaleur capteurs solaires vers ballon

## Caractéristiques Techniques Typiques
- Puissance : 20 kW à 500 kW (tertiaire)
- Surface d'échange : Fonction puissance (m²)
- Type : Plaques brasées, à joints, tubes et calandre
- Matériaux : Inox contact eau sanitaire (316L)
- Rendement : 85-95%
- Delta T primaire/secondaire : 5-10°C

## Localisation Typique
- Chaufferie intégré ou proche chaudière
- Local sous-station (réseau chaleur urbain)
- Sur ou intégré au DHW Tank
- Salle des machines

## Relations avec Autres Équipements
- **Alimente** : DHW Tank, réseau ECS instantané
- **Alimenté par** : Chaudière, réseau chaleur, circuit primaire chauffage, capteurs solaires
- **Contrôlé par** : Régulation température, vanne 3 voies motorisée primaire
- **Associé à** : Temperature Sensor (primaire/secondaire), Motorized Valve, DHW Circulation Pump

## Quantité Typique par Bâtiment
- Petit (5 étages) : 1 échangeur (30-60 kW)
- Moyen (15 étages) : 1-2 échangeurs (100-200 kW) avec backup
- Grand (30+ étages) : 2-4 échangeurs (200-500 kW) cascade ou redondance

## Sources
- Haystack Project - Heat exchanger equipment
- Brick Schema - Heat_Exchanger class
- ASHRAE Handbook - Heat exchangers and DHW production
- EN 806 - Specifications for installations inside buildings for water
