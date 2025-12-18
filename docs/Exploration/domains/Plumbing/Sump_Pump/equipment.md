# Sump Pump

## Identifiant
- **Code** : SUMP-PUMP
- **Haystack** : `water`, `sump`, `pump`, `equip`
- **Brick** : `brick:Sump_Pump`

## Description
Pompe d'évacuation submersible ou semi-submersible installée dans un puisard pour évacuer les eaux d'infiltration, de ruissellement ou de drainage vers le réseau d'évacuation. Protège les sous-sols et parkings contre les inondations.

## Fonction
Collecter et évacuer automatiquement les eaux de drainage, d'infiltration ou de surface accumulées dans un puisard vers le réseau d'assainissement ou l'extérieur. Démarrage automatique par flotteur ou capteur de niveau.

## Variantes Courantes
- **Pompe vide-cave** : Eaux claires, usage domestique
- **Pompe de relevage eaux usées** : Eaux chargées avec broyeur
- **Pompe de puisard immergée** : Installation permanente en fosse
- **Station de relevage double** : Redondance avec alternance/secours

## Caractéristiques Techniques Typiques
- Débit : 5-100 m³/h selon application
- Hauteur de refoulement : 3-15 mètres
- Puissance : 0.3-5 kW
- Passage de particules : 10-50 mm
- Commande : Flotteur, capteur niveau, contrôle intelligent
- Communication : Contact sec alarme, Modbus pour supervision

## Localisation Typique
- Puisard sous-sol
- Parking souterrain
- Fosse d'ascenseur
- Local technique en point bas
- Vide sanitaire

## Relations avec Autres Équipements
- **Alimente** : Réseau d'évacuation EU/EP
- **Alimenté par** : Collecte gravitaire puisard
- **Contrôlé par** : Level Sensor, flotteur, supervision alarmes
- **Associé à** : Drain Pump (backup), clapet anti-retour refoulement

## Quantité Typique par Bâtiment
- Petit (5 étages) : 1-2 pumps (puisard principal + ascenseur)
- Moyen (15 étages) : 2-4 pumps (sous-sol, parkings, multiples points bas)
- Grand (30+ étages) : 4-10 pumps (multiples niveaux parking, redondance)

## Sources
- Haystack Project - Pump equipment
- Brick Schema - Sump_Pump class
- Plumbing codes - Drainage and sump systems
- Building flood protection standards
