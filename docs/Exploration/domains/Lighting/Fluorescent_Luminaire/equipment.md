# Fluorescent Luminaire

## Identifiant
- **Code** : FLUOR_LUM
- **Haystack** : luminaire, fluorescent, light
- **Brick** : brick:Fluorescent_Lighting_Equipment, brick:Luminaire

## Description
Appareil d'éclairage utilisant des tubes fluorescents pour produire de la lumière. Bien que progressivement remplacés par les LED, ces luminaires restent présents dans de nombreux bâtiments existants et peuvent être équipés de ballasts électroniques communicants pour l'intégration dans les systèmes de gestion du bâtiment.

## Fonction
Fournir un éclairage artificiel diffus dans les espaces intérieurs. Les tubes fluorescents fonctionnent par décharge électrique dans un gaz, offrant une efficacité lumineuse correcte et une durée de vie moyenne. Le contrôle se fait via le ballast électronique.

## Variantes Courantes
- **T8 Luminaire** : Tubes de 26mm de diamètre, standard le plus courant
- **T5 Luminaire** : Tubes de 16mm de diamètre, plus efficace et compact
- **T12 Luminaire** : Tubes de 38mm de diamètre, technologie ancienne en voie de disparition
- **Compact Fluorescent (CFL) Luminaire** : Tubes pliés ou spiralés pour format réduit
- **Fluorescent Troffer** : Format encastré dans faux-plafond modulaire
- **Fluorescent High Bay** : Haute puissance pour espaces industriels
- **Wraparound Fluorescent** : Diffuseur enveloppant pour éclairage diffus

## Caractéristiques Techniques Typiques
- Tension d'alimentation: 120-277V AC
- Puissance: 15W à 120W selon type de tube
- Flux lumineux: 1,000 à 8,000 lumens
- Efficacité lumineuse: 60-100 lm/W
- Température de couleur: 2700K à 6500K (selon tube)
- IRC (CRI): 70-85, haute qualité >90
- Durée de vie: 10,000-30,000 heures
- Gradation: 10-100% avec ballast électronique dimmable
- Communication: DALI, 0-10V, DSI (Digital Serial Interface)
- Ballast électronique requis pour contrôle
- Temps de préchauffage: instantané (ballast électronique) à quelques secondes

## Localisation Typique
- Bureaux (installations existantes)
- Salles de classe
- Entrepôts et zones de stockage
- Parkings intérieurs
- Couloirs et circulations
- Espaces techniques
- Cuisines et zones de préparation
- Ateliers et zones industrielles

## Relations avec Autres Équipements
- **Alimente** : N/A (équipement terminal)
- **Alimenté par** : Lighting Panel, Ballast (intégré ou déporté)
- **Contrôlé par** : Lighting Controller, DALI Controller, Dimmer, Ballast Controller, Occupancy Sensor, Photocell, Building Automation System

## Quantité Typique par Bâtiment
- Petit (5 étages) : 300-1,000 (en remplacement progressif)
- Moyen (15 étages) : 1,000-5,000 (en remplacement progressif)
- Grand (30+ étages) : 3,000-20,000 (en remplacement progressif)

## Sources
- Haystack Project - Lighting equipment definitions
- Brick Schema - Fluorescent Lighting Equipment class
- DALI Alliance - Fluorescent ballast control specifications
- IEC 60929 - Electronic ballasts for tubular fluorescent lamps
- Building automation industry best practices
