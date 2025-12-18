# Terminal Unit (Unité terminale)

## Identifiant
- **Code** : TU / TRM
- **Haystack** : `terminalUnit-equip`
- **Brick** : `brick:Terminal_Unit`

## Description
Équipement HVAC situé en bout de réseau de distribution d'air ou d'eau, qui conditionne localement l'air d'une zone. Catégorie générique englobant VAV, CAV, FCU, diffuseurs actifs, etc.

## Fonction
Assurer le conditionnement d'air final d'une zone en adaptant les paramètres (température, débit) aux besoins locaux. Point de contrôle zone par zone du système HVAC.

## Variantes Courantes
- **VAV** : Terminal à débit d'air variable (voir fiche dédiée)
- **CAV** : Terminal à débit d'air constant (voir fiche dédiée)
- **FCU** : Fan Coil Unit (voir fiche dédiée)
- **Dual Duct Terminal** : Mélange air chaud et air froid
- **Induction Unit** : Induction d'air de zone dans jet d'air primaire
- **Chilled Beam** : Poutre froide active ou passive (voir fiche dédiée)
- **Radiant Panel** : Panneaux rayonnants (voir fiche dédiée)

## Caractéristiques Techniques Typiques
- Puissance : 0.5 - 20 kW (selon type)
- Débit d'air : 100 - 5,000 m³/h (si aéraulique)
- Protocoles : BACnet, Modbus, LON
- Points de supervision : température zone, débit/puissance, modes, alarmes

## Localisation Typique
- Plénum faux plafond
- Locaux techniques de zone
- Visible en zone (console, cassette)

## Relations avec Autres Équipements
- **Alimente** : Zone locale (air/eau conditionné)
- **Alimenté par** : AHU (air primaire), Chiller/Boiler (eau si hydraulique)
- **Contrôlé par** : Thermostat de zone, DDC Controller
- **Interagit avec** : Dampers, Vannes, Capteurs de zone

## Quantité Typique par Bâtiment
- Petit (5 étages) : 20-100 unités
- Moyen (15 étages) : 100-500 unités
- Grand (30+ étages) : 500-2,000 unités

## Sources
- Haystack Project - Terminal Unit Equipment
- Brick Schema - Terminal Unit Classes
- BACnet Standard - Zone Terminal Equipment
- ASHRAE Handbook - Air Distribution
