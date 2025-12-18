# Heat Recovery Chiller (Chiller à récupération de chaleur)

## Identifiant
- **Code** : HRC / HRCH
- **Haystack** : `heatRecoveryChiller-equip`
- **Brick** : `brick:Heat_Recovery_Chiller`

## Description
Chiller équipé d'un échangeur de chaleur supplémentaire qui permet de récupérer la chaleur rejetée au condenseur pour produire simultanément de l'eau chaude (typiquement 50-60°C) et de l'eau glacée. Maximise l'efficacité énergétique en valorisant la chaleur fatale.

## Fonction
Produire simultanément du froid (eau glacée) et du chaud (eau chaude) en récupérant la chaleur normalement rejetée à la cooling tower. Idéal pour bâtiments avec besoins simultanés chaud/froid (hôtels, hôpitaux, piscines).

## Variantes Courantes
- **Chiller avec désurchauffeur** : Récupération partielle (eau chaude 50-60°C)
- **Chiller full heat recovery** : Récupération totale de la chaleur condenseur
- **Chiller réversible avec récupération** : Peut fonctionner en pompe à chaleur
- **Chiller cascade** : Production eau chaude haute température (70-80°C)

## Caractéristiques Techniques Typiques
- Puissance frigorifique : 100 kW - 3 MW
- Puissance calorifique récupérée : 120 kW - 3.5 MW (COP apparent très élevé)
- Température eau chaude : 50-70°C
- Température eau glacée : 5-7°C
- COP global : 5-8 (valorisation chaleur incluse)
- Protocoles : BACnet, Modbus, LON
- Points de supervision : T° eau glacée/chaude, puissances, COP, modes, alarmes

## Localisation Typique
- Sous-sol technique (plantroom)
- Local technique central

## Relations avec Autres Équipements
- **Alimente** : AHU/FCU (eau glacée), AHU/FCU/ECS (eau chaude récupérée)
- **Alimenté par** : Cooling Tower (si rejet chaleur excédentaire), Pompes
- **Contrôlé par** : Plant Controller, BMS
- **Interagit avec** : Pompes, Vannes, Ballons tampons, ECS

## Quantité Typique par Bâtiment
- Petit (5 étages) : 0-1 unité (si besoins simultanés)
- Moyen (15 étages) : 1-2 unités
- Grand (30+ étages) : 2-4 unités

## Sources
- Haystack Project - Heat Recovery Chiller
- Brick Schema - Chiller with Heat Recovery
- BACnet Standard - Chiller Control
- ASHRAE Handbook - Heat Recovery Systems
