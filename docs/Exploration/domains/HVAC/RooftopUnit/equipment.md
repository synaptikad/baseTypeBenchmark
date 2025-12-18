# Rooftop Unit (RTU)

## Identifiant
- **Code** : RTU
- **Haystack** : `rtu-equip`
- **Brick** : `brick:Rooftop_Unit`

## Description
Unité de conditionnement d'air autonome tout-en-un installée en toiture. Intègre dans un seul équipement compact la production de froid (compresseur), de chaud (résistances ou brûleur gaz), la ventilation, la filtration et le contrôle.

## Fonction
Assurer le conditionnement d'air complet d'une zone ou de plusieurs zones du bâtiment de manière autonome, sans centrale technique centralisée. Solution packagée pour bâtiments commerciaux et industriels.

## Variantes Courantes
- **RTU DX (Direct Expansion)** : Détente directe du frigorigène
- **RTU gaz/électrique** : Chauffage gaz ou électrique
- **RTU à débit constant (CAV)** : Débit d'air fixe
- **RTU à débit variable (VAV)** : Débit modulable avec VFD
- **RTU avec économiseur** : Free-cooling par air extérieur
- **RTU multi-zones** : Plusieurs zones de soufflage avec régulation différenciée

## Caractéristiques Techniques Typiques
- Puissance frigorifique : 10 - 250 kW (3 - 70 TR)
- Puissance calorifique : 15 - 300 kW
- Débit d'air : 2,000 - 50,000 m³/h
- EER : 2.5 - 3.5
- COP chauffage : 0.9 (résistances) ou 3.0+ (pompe à chaleur)
- Protocoles : BACnet, Modbus, LON
- Points de supervision : températures, débits, états compresseurs, positions registres, alarmes

## Localisation Typique
- Toiture du bâtiment (d'où le nom)
- Parfois au sol extérieur (variante packaged unit)

## Relations avec Autres Équipements
- **Alimente** : VAV ou diffuseurs directs (réseau de gaines)
- **Alimenté par** : Réseau électrique, Réseau gaz (si chauffage gaz)
- **Contrôlé par** : Contrôleur intégré, BMS
- **Interagit avec** : Thermostats de zone, Dampers, Humidificateur (si option)

## Quantité Typique par Bâtiment
- Petit (5 étages) : 1-5 unités
- Moyen (15 étages) : 5-15 unités
- Grand (30+ étages) : 10-30 unités (moins fréquent, privilégié pour bâtiments bas)

## Sources
- Haystack Project - Rooftop Unit
- Brick Schema - RTU Classes
- BACnet Standard - Packaged Units
- ASHRAE Handbook - Unitary Equipment
