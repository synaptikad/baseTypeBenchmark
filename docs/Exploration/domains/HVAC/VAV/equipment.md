# Variable Air Volume Box (VAV)

## Identifiant
- **Code** : VAV
- **Haystack** : `vav-equip`
- **Brick** : `brick:VAV`

## Description
Terminal à débit d'air variable qui régule le débit d'air fourni à une zone en fonction des besoins thermiques. Module automatiquement l'ouverture d'un registre motorisé pour ajuster le débit.

## Fonction
Assurer le contrôle de température d'une zone individuelle en modulant le débit d'air traité provenant de l'AHU. Permet une régulation zone par zone économe en énergie.

## Variantes Courantes
- **VAV Cooling Only** : Refroidissement seul (air froid de l'AHU)
- **VAV Reheat** : Avec batterie de réchauffage électrique ou eau chaude
- **VAV Dual Duct** : Mélange air chaud et air froid
- **VAV Fan Powered (Series/Parallel)** : Avec ventilateur intégré pour recycler l'air de la pièce
- **VAV Bypass** : Avec sortie de décharge vers le plénum

## Caractéristiques Techniques Typiques
- Débit d'air : 200 - 5,000 m³/h
- Plage de modulation : 20-100% du débit nominal
- Registre motorisé avec actionneur DDC
- Capteur de débit intégré
- Protocoles : BACnet, Modbus, LON
- Points de supervision : débit, température zone, position registre, commande ventilateur (si FPV)

## Localisation Typique
- Plénum au-dessus de faux plafond
- Locaux techniques de zone
- Un VAV par zone thermique (bureau, salle de réunion, open space)

## Relations avec Autres Équipements
- **Alimente** : Diffuseurs d'air de la zone
- **Alimenté par** : AHU (air primaire), Boiler/Heat Pump (si reheat)
- **Contrôlé par** : Thermostat de zone, Capteur de température
- **Interagit avec** : Dampers, VFD de l'AHU (cascade)

## Quantité Typique par Bâtiment
- Petit (5 étages) : 20-50 unités
- Moyen (15 étages) : 100-300 unités
- Grand (30+ étages) : 500-1,500 unités

## Sources
- Haystack Project - VAV Equipment
- Brick Schema - Terminal Unit Classes
- BACnet Standard - Zone Control
- ASHRAE Handbook - Air Distribution Systems
