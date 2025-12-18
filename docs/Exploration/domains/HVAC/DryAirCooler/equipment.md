# Dry Air Cooler (Aéroréfrigérant)

## Identifiant
- **Code** : DAC / DRY
- **Haystack** : `dryAirCooler-equip`
- **Brick** : `brick:Dry_Cooler`

## Description
Échangeur de chaleur air/eau qui rejette la chaleur d'un circuit d'eau vers l'air extérieur sans évaporation (fonctionnement sec). Alternative aux tours de refroidissement dans les climats froids ou pour les applications ne tolérant pas de panache.

## Fonction
Refroidir un circuit d'eau (condenseur, free-cooling, process) en rejetant la chaleur vers l'air extérieur par convection forcée. Pas de consommation d'eau ni de traitement chimique requis.

## Variantes Courantes
- **Dry cooler standard** : Refroidissement en fonctionnement sec
- **Dry cooler adiabatique** : Pulvérisation d'eau en période chaude
- **Dry cooler pour free-cooling** : Refroidissement direct datacenter
- **Dry cooler glycolé** : Circuit avec antigel pour climats froids

## Caractéristiques Techniques Typiques
- Puissance : 50 kW - 2 MW
- Delta T eau : 5-10°C
- Approche : 5-15°C (T sortie eau - T air ambiant)
- Débit d'air : 10,000 - 200,000 m³/h
- Protocoles : BACnet, Modbus
- Points de supervision : températures eau, air, vitesse ventilateurs

## Localisation Typique
- Toiture
- Sol extérieur
- Proximité des équipements refroidis

## Relations avec Autres Équipements
- **Alimente** : Circuit de refroidissement (eau froide)
- **Alimenté par** : Circuit de rejet (eau chaude)
- **Contrôlé par** : Contrôleur intégré, BMS
- **Interagit avec** : Chillers, Free-cooling, Pompes

## Quantité Typique par Bâtiment
- Petit (5 étages) : 0-2 unités
- Moyen (15 étages) : 2-5 unités
- Grand (30+ étages) : 5-15 unités

## Sources
- ASHRAE Handbook - HVAC Systems
- Güntner / Alfa Laval - Dry Cooler Documentation
- Project Haystack - Dry Cooler Equipment
- Brick Schema - Dry Cooler Class
