# Constant Air Volume Terminal (CAV)

## Identifiant
- **Code** : CAV
- **Haystack** : `cav-equip`
- **Brick** : `brick:CAV`

## Description
Terminal de distribution d'air à débit constant qui maintient un débit d'air fixe dans une zone, indépendamment de la charge thermique. La régulation de température se fait par modulation de la température de l'air soufflé central ou par réchauffage local.

## Fonction
Distribuer un débit d'air constant à une zone, assurant une ventilation stable. Utilisé lorsque les variations de charge sont faibles ou lorsque la constance du débit est requise (laboratoires, salles blanches).

## Variantes Courantes
- **CAV simple** : Débit fixe sans réchauffage
- **CAV avec réchauffage** : Batterie eau chaude ou électrique
- **CAV à induction** : Induit l'air de la zone
- **CAV double flux** : Air chaud et air froid
- **CAV multi-zones** : Plusieurs départs à débits fixes

## Caractéristiques Techniques Typiques
- Débit d'air : 100 - 5,000 m³/h
- Pression statique : 50 - 300 Pa
- Réchauffage : 0 - 10 kW (si équipé)
- Registre : Fixe ou réglable manuellement
- Protocoles : BACnet, Modbus, LON
- Points de supervision : température zone, débit, vanne réchauffage

## Localisation Typique
- Plénum faux plafond
- Gaines de distribution
- Laboratoires, salles blanches
- Zones à charge stable

## Relations avec Autres Équipements
- **Alimente** : Zone (air conditionné à débit constant)
- **Alimenté par** : AHU (air primaire traité)
- **Contrôlé par** : Thermostat de zone (via réchauffage), BMS
- **Interagit avec** : Capteurs température, Batteries de réchauffage

## Quantité Typique par Bâtiment
- Petit (5 étages) : 20-50 unités
- Moyen (15 étages) : 50-200 unités
- Grand (30+ étages) : 200-800 unités

## Sources
- ASHRAE Handbook - Air Distribution
- Project Haystack - CAV Equipment
- Brick Schema - CAV Class
- Trane / Carrier - CAV Terminal Documentation
