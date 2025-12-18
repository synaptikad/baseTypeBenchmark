# Dual Duct Terminal (Terminal double gaine)

## Identifiant
- **Code** : DDT / DDVAV
- **Haystack** : `dualDuctTerminal-equip`
- **Brick** : `brick:Dual_Duct_Terminal`

## Description
Terminal qui reçoit simultanément de l'air chaud et de l'air froid via deux gaines séparées, puis mélange les deux flux dans les proportions adéquates pour atteindre la température de zone souhaitée. Permet un contrôle précis zone par zone.

## Fonction
Assurer le conditionnement d'air d'une zone en mélangeant air chaud et air froid selon les besoins thermiques instantanés. Offre une grande flexibilité (zones simultanément en chaud et en froid) au prix d'une complexité accrue.

## Variantes Courantes
- **Dual Duct VAV** : Débit variable sur chaque gaine
- **Dual Duct CAV** : Débit constant, mélange modulé
- **Dual Duct avec bypass** : Évacuation excédent d'air vers plénum
- **Dual Duct mixing box** : Caisson de mélange simple

## Caractéristiques Techniques Typiques
- Débit d'air : 200 - 5,000 m³/h
- Deux registres motorisés (air chaud / air froid)
- Capteur de débit
- Actuateurs DDC
- Protocoles : BACnet, Modbus, LON
- Points de supervision : débit total, positions registres chaud/froid, température zone

## Localisation Typique
- Plénum au-dessus de faux plafond
- Locaux techniques de zone
- Bâtiments anciens avec systèmes double gaine (moins courant aujourd'hui)

## Relations avec Autres Équipements
- **Alimente** : Zone (air mélangé conditionné)
- **Alimenté par** : AHU double gaine (gaine air chaud + gaine air froid)
- **Contrôlé par** : Thermostat de zone, DDC Controller
- **Interagit avec** : Dampers (2 registres), Capteurs température

## Quantité Typique par Bâtiment
- Petit (5 étages) : 10-40 unités (si système double gaine)
- Moyen (15 étages) : 40-150 unités
- Grand (30+ étages) : 150-500 unités

## Sources
- Haystack Project - Dual Duct Terminal Equipment
- Brick Schema - Dual Duct Terminal
- BACnet Standard - Dual Duct Systems
- ASHRAE Handbook - Dual Duct Systems
