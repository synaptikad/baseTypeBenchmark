# Floor Heating System (Plancher chauffant)

## Identifiant
- **Code** : FHS / UFH
- **Haystack** : `floorHeating-equip`
- **Brick** : `brick:Radiant_Floor_Heating`

## Description
Système de chauffage par le sol utilisant des tubes noyés dans la dalle ou la chape qui diffusent la chaleur par rayonnement et convection. Alimenté par eau chaude basse température ou résistances électriques.

## Fonction
Chauffer une zone par rayonnement depuis le sol, offrant un confort thermique optimal avec des températures d'air plus basses. Permet l'utilisation de sources basse température (pompes à chaleur, condensation).

## Variantes Courantes
- **Plancher chauffant eau** : Tubes PER ou multicouche en serpentin
- **Plancher chauffant électrique** : Câbles ou trames chauffantes
- **Plancher chauffant-rafraîchissant** : Réversible avec eau glacée
- **Plancher sec** : Pose sur isolant sans chape
- **Plancher humide** : Tubes noyés dans chape

## Caractéristiques Techniques Typiques
- Puissance surfacique : 50-100 W/m² (chauffage)
- Température eau : 30-45°C (basse température)
- Température surface sol : 26-29°C max (zones occupées)
- Inertie : Élevée (plusieurs heures)
- Protocoles : BACnet, Modbus, KNX (via collecteur)
- Points de supervision : température départ/retour, température sol, vanne zone

## Localisation Typique
- Sols de logements
- Bureaux
- Halls d'entrée
- Zones commerciales
- Salles de bains

## Relations avec Autres Équipements
- **Alimente** : Zone (chaleur rayonnante)
- **Alimenté par** : Chaudière, Pompe à chaleur, Réseau électrique
- **Contrôlé par** : Thermostat de zone, Collecteur, BMS
- **Interagit avec** : Pompes, Vannes de zone, Régulation climatique

## Quantité Typique par Bâtiment
- Petit (5 étages) : 5-20 zones
- Moyen (15 étages) : 20-80 zones
- Grand (30+ étages) : 80-300 zones

## Sources
- ASHRAE Handbook - Radiant Heating and Cooling
- EN 1264 - Water Based Surface Embedded Heating
- Project Haystack - Radiant Floor Equipment
- Uponor / Rehau - Floor Heating Documentation
