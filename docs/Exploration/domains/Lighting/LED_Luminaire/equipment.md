# LED Luminaire

## Identifiant
- **Code** : LED_LUM
- **Haystack** : luminaire, led, light
- **Brick** : brick:LED_Lighting_Equipment, brick:Luminaire

## Description
Appareil d'éclairage à diodes électroluminescentes (LED) conçu pour l'éclairage général ou ciblé dans les bâtiments. Les LED luminaires modernes sont généralement communicants et peuvent être contrôlés individuellement via des protocoles tels que DALI, KNX ou BACnet.

## Fonction
Fournir un éclairage artificiel dans les espaces intérieurs et extérieurs du bâtiment. Ils convertissent l'électricité en lumière avec une haute efficacité énergétique et permettent un contrôle précis de l'intensité, de la température de couleur et parfois de la direction du faisceau lumineux.

## Variantes Courantes
- **LED Downlight** : Encastré au plafond pour éclairage directionnel vers le bas
- **LED Panel** : Panneau plat pour éclairage diffus uniforme
- **LED Linear** : Format linéaire pour éclairage continu des couloirs et espaces de travail
- **LED Troffer** : Format encastré dans faux-plafond modulaire
- **LED High Bay** : Haute puissance pour espaces industriels et entrepôts
- **LED Track Light** : Monté sur rail pour éclairage d'accentuation
- **LED Wall Washer** : Éclairage mural indirect
- **LED Tunable White** : Température de couleur ajustable (2700K-6500K)
- **LED RGB/RGBW** : Couleur variable pour éclairage d'ambiance

## Caractéristiques Techniques Typiques
- Tension d'alimentation: 24V DC, 48V DC ou 120-277V AC
- Puissance: 5W à 200W selon application
- Flux lumineux: 500 à 20,000 lumens
- Efficacité lumineuse: 80-150 lm/W
- Température de couleur: 2700K à 6500K
- IRC (CRI): >80, haute qualité >90
- Durée de vie: 50,000-100,000 heures
- Gradation: 0-100% (DALI, 0-10V, PWM)
- Communication: DALI, DALI-2, DMX512, KNX, BACnet, Zigbee, Bluetooth Mesh
- Détection de présence intégrée (optionnel)
- Capteur de luminosité intégré (optionnel)

## Localisation Typique
- Bureaux ouverts et individuels
- Salles de réunion
- Couloirs et circulations
- Espaces commerciaux
- Halls d'entrée et lobbies
- Salles de classe
- Espaces de vente
- Parkings intérieurs
- Espaces techniques
- Zones de stockage

## Relations avec Autres Équipements
- **Alimente** : N/A (équipement terminal)
- **Alimenté par** : Lighting Panel, Lighting Power Supply, PoE Switch (pour certains modèles basse tension)
- **Contrôlé par** : Lighting Controller, DALI Controller, Dimmer, Occupancy Sensor, Photocell, Scene Controller, Building Automation System

## Quantité Typique par Bâtiment
- Petit (5 étages) : 500-1,500
- Moyen (15 étages) : 2,000-8,000
- Grand (30+ étages) : 10,000-50,000

## Sources
- Haystack Project - Lighting equipment definitions
- Brick Schema - LED Lighting Equipment class
- DALI Alliance - Digital Addressable Lighting Interface specifications
- IEC 62386 - DALI standard series
- Building automation industry best practices
