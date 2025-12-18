# Hot Water Boiler (Chaudière eau chaude)

## Identifiant
- **Code** : HWB / CHWB
- **Haystack** : `hotWaterBoiler-equip`
- **Brick** : `brick:Hot_Water_Boiler`

## Description
Générateur de chaleur qui produit de l'eau chaude (non pressurisée, < 110°C) pour le chauffage des bâtiments. Alimenté par gaz, fioul, électricité ou biomasse. Équipement central des systèmes de chauffage hydrauliques.

## Fonction
Produire l'eau chaude nécessaire au chauffage du bâtiment via les émetteurs (radiateurs, planchers chauffants, batteries AHU). Maintenir une température d'eau adaptée aux besoins selon la loi d'eau.

## Variantes Courantes
- **Chaudière gaz à condensation** : Haute efficacité (> 100% PCI)
- **Chaudière gaz standard** : Rendement 85-95%
- **Chaudière fioul** : Fuel domestique ou lourd
- **Chaudière électrique** : Résistances électriques
- **Chaudière biomasse** : Granulés, plaquettes, bûches
- **Chaudière murale** : Petites puissances, logements
- **Chaudière au sol** : Moyennes et grandes puissances

## Caractéristiques Techniques Typiques
- Puissance : 20 kW - 5 MW
- Température eau : 40-90°C (modulable)
- Rendement : 85-110% PCI (condensation)
- Combustible : Gaz naturel, propane, fioul, électricité, biomasse
- Protocoles : BACnet, Modbus, OpenTherm, eBUS
- Points de supervision : température départ/retour, pression, état brûleur, alarmes

## Localisation Typique
- Chaufferie centrale
- Local technique
- Toiture (petites unités modulaires)

## Relations avec Autres Équipements
- **Alimente** : AHU, FCU, Radiateurs, Planchers chauffants, ECS
- **Alimenté par** : Gaz, Électricité, Fioul, Biomasse
- **Contrôlé par** : Régulateur chaudière, BMS, Thermostat d'ambiance
- **Interagit avec** : Pompes, Vannes mélangeuses, Ballon tampon, Cheminée

## Quantité Typique par Bâtiment
- Petit (5 étages) : 1-2 unités
- Moyen (15 étages) : 2-4 unités (cascade)
- Grand (30+ étages) : 4-10 unités (cascade)

## Sources
- ASHRAE Handbook - HVAC Systems and Equipment
- EN 303 - Boiler Efficiency Standards
- Project Haystack - Boiler Equipment
- Viessmann / Buderus / De Dietrich - Boiler Documentation
