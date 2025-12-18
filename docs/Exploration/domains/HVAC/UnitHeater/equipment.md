# Unit Heater (Aérotherme)

## Identifiant
- **Code** : UH / AERO
- **Haystack** : `unitHeater-equip`
- **Brick** : `brick:Unit_Heater`

## Description
Appareil de chauffage autonome qui souffle de l'air chaud dans un local. Comprend une batterie de chauffe (eau chaude, vapeur, électrique, ou gaz) et un ventilateur. Utilisé principalement dans les espaces industriels, commerciaux, ou non occupés en permanence.

## Fonction
Chauffer rapidement des espaces de grands volumes ou intermittents (entrepôts, ateliers, quais de chargement, garages). Solution simple et économique pour espaces ne nécessitant pas de confort élevé.

## Variantes Courantes
- **Aérotherme eau chaude** : Batterie alimentée par chaudière
- **Aérotherme vapeur** : Batterie alimentée par vapeur
- **Aérotherme électrique** : Résistances électriques
- **Aérotherme gaz** : Brûleur gaz intégré (avec ou sans évacuation)
- **Aérotherme suspendu** : Fixation haute (entrepôts)
- **Aérotherme mural** : Fixation murale

## Caractéristiques Techniques Typiques
- Puissance : 5 - 100 kW
- Débit d'air : 500 - 10,000 m³/h
- Portée de jet : 5 - 30 mètres
- Source énergie : Eau chaude, vapeur, électricité, gaz
- Protocoles : BACnet, Modbus (si contrôle centralisé)
- Points de supervision : état marche/arrêt, température soufflage, alarmes

## Localisation Typique
- Entrepôts et zones de stockage
- Ateliers industriels
- Quais de chargement
- Garages et parkings
- Zones de production

## Relations avec Autres Équipements
- **Alimente** : Zone locale (air chaud soufflé)
- **Alimenté par** : Boiler (eau chaude/vapeur), Réseau électrique, Réseau gaz
- **Contrôlé par** : Thermostat local, Contrôleur, BMS
- **Interagit avec** : Vannes (si hydraulique), Détecteurs de présence

## Quantité Typique par Bâtiment
- Petit (5 étages) : 0-5 unités (si zones industrielles)
- Moyen (15 étages) : 5-20 unités (parkings, locaux techniques)
- Grand (30+ étages) : 20-50 unités

## Sources
- Haystack Project - Unit Heater Equipment
- Brick Schema - Unit Heater
- BACnet Standard - Heating Equipment
- ASHRAE Handbook - Space Heating Equipment
