# Air Handling Unit (AHU)

## Identifiant
- **Code** : AHU
- **Haystack** : `ahu-equip`
- **Brick** : `brick:AHU`

## Description
Centrale de traitement d'air qui conditionne et distribue l'air dans le bâtiment. L'AHU aspire l'air extérieur et/ou l'air de reprise, le filtre, le chauffe ou le refroidit, contrôle l'humidité, puis le distribue via un réseau de gaines.

## Fonction
Assurer le conditionnement d'air (température, humidité, qualité) pour des zones importantes du bâtiment. Point central de distribution d'air traité.

## Variantes Courantes
- **AHU Simple zone** : Dessert une seule zone thermique
- **AHU Multi-zones** : Dessert plusieurs zones avec régulation différenciée
- **AHU à débit constant (CAV)** : Débit d'air fixe
- **AHU à débit variable (VAV)** : Débit d'air modulable
- **AHU avec récupération d'énergie** : Intègre un échangeur de chaleur air-air
- **AHU 100% air neuf** : Sans recyclage d'air
- **AHU avec économiseur** : Utilise l'air extérieur pour refroidissement gratuit

## Caractéristiques Techniques Typiques
- Débit d'air : 5,000 - 100,000 m³/h
- Pression statique : 500 - 2,500 Pa
- Composants : ventilateurs (soufflage/reprise), batteries (chaud/froid), filtres, humidificateur, registres
- Protocoles : BACnet, Modbus, LON
- Points de supervision : températures, débits, pressions, états ventilateurs, positions registres/vannes

## Localisation Typique
- Locaux techniques en toiture
- Sous-sols techniques
- Locaux techniques d'étage (pour AHU d'étage)

## Relations avec Autres Équipements
- **Alimente** : VAV, CAV, Diffuseurs d'air, Gaines de distribution
- **Alimenté par** : Chiller (eau glacée), Boiler/Heat Pump (eau chaude), Réseau vapeur, Humidifier
- **Contrôlé par** : DDC (Direct Digital Controller), Thermostat de zone
- **Interagit avec** : Economizer, Dampers, VFD

## Quantité Typique par Bâtiment
- Petit (5 étages) : 1-3 unités
- Moyen (15 étages) : 5-15 unités
- Grand (30+ étages) : 15-50 unités

## Sources
- Haystack Project - Equipment Definitions
- Brick Schema - HVAC Equipment Classes
- BACnet Standard - HVAC Applications
- ASHRAE Handbooks - HVAC Systems and Equipment
