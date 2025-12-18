# Steam Boiler (Chaudière vapeur)

## Identifiant
- **Code** : STB / SB
- **Haystack** : `steamBoiler-equip`
- **Brick** : `brick:Steam_Boiler`

## Description
Générateur de vapeur sous pression pour le chauffage, l'humidification ou les process industriels. Produit de la vapeur saturée ou surchauffée à partir d'eau et d'un combustible (gaz, fioul, électricité). Équipement critique soumis à réglementation stricte.

## Fonction
Produire de la vapeur à pression et température contrôlées pour alimenter les échangeurs de chaleur, humidificateurs vapeur, process industriels ou réseaux de chauffage vapeur. Assurer la sécurité par contrôle de niveau, pression et qualité de combustion.

## Variantes Courantes
- **Chaudière à tubes de fumée** : Fumées dans tubes, eau autour (firetube)
- **Chaudière à tubes d'eau** : Eau dans tubes, fumées autour (watertube)
- **Chaudière électrique** : Résistances ou électrodes
- **Chaudière à vapeur flash** : Production rapide, petites capacités
- **Générateur de vapeur instantané** : Sans réserve d'eau

## Caractéristiques Techniques Typiques
- Puissance : 50 kW - 50 MW
- Pression vapeur : 0.5-20 bar (basse/moyenne pression bâtiment)
- Température vapeur : 110-250°C
- Rendement : 80-95%
- Combustible : Gaz naturel, fioul, électricité
- Protocoles : BACnet, Modbus
- Points de supervision : pression, niveau, températures, état brûleur, alarmes sécurité

## Localisation Typique
- Chaufferie centrale
- Local technique dédié (réglementation)
- Bâtiments industriels
- Hôpitaux (stérilisation, humidification)

## Relations avec Autres Équipements
- **Alimente** : Échangeurs vapeur, Humidificateurs, Process, Réseau vapeur
- **Alimenté par** : Gaz, Électricité, Fioul, Eau traitée
- **Contrôlé par** : Régulateur chaudière, Automate sécurité, BMS
- **Interagit avec** : Bâche alimentaire, Pompes alimentaires, Dégazeur, Purgeurs, Détendeurs

## Quantité Typique par Bâtiment
- Petit (5 étages) : 0-1 unité (rare)
- Moyen (15 étages) : 1-2 unités
- Grand (30+ étages) : 2-4 unités (redondance)
- Hôpital/Industrie : 2-6 unités

## Sources
- ASHRAE Handbook - HVAC Systems and Equipment
- EN 12953 - Shell Boilers
- EN 12952 - Water-tube Boilers
- Project Haystack - Steam Boiler Equipment
- Brick Schema - Steam_Boiler Class
