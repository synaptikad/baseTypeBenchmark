# Dehumidifier (Déshumidificateur)

## Identifiant
- **Code** : DEHUM
- **Haystack** : `dehumidifier-equip`
- **Brick** : `brick:Dehumidifier`

## Description
Équipement qui retire l'humidité excessive de l'air par condensation (refroidissement sous le point de rosée) ou par dessiccation (roue déshydratante). Maintient l'humidité relative dans la plage de confort et évite la condensation.

## Fonction
Réduire le taux d'humidité relative de l'air, particulièrement en été lors de fortes charges latentes ou dans des zones à risque de condensation (piscines, sous-sols, salles blanches).

## Variantes Courantes
- **Déshumidificateur à condensation (DX)** : Refroidit l'air pour condenser l'humidité
- **Déshumidificateur à roue déshydratante** : Adsorption chimique, régénération thermique
- **Déshumidificateur avec réchauffage** : Évite le sur-refroidissement après condensation
- **Déshumidificateur de piscine** : Traite l'air très humide (70-80% HR)
- **Déshumidificateur autonome** : Unité indépendante portable ou fixe

## Caractéristiques Techniques Typiques
- Capacité de déshumidification : 5 - 200 litres/jour
- Puissance : 1 - 50 kW
- Type : Condensation (DX), Roue déshydratante
- Plage HR : 30-80% HR
- Protocoles : BACnet, Modbus, 0-10V
- Points de supervision : capacité (%), HR zone, condensats collectés, alarmes

## Localisation Typique
- Piscines intérieures
- Sous-sols et parkings
- Salles blanches et laboratoires
- Locaux archives et musées
- Intégré dans AHU (zones à charge latente élevée)

## Relations avec Autres Équipements
- **Alimente** : Zone déshumidifiée (air traité)
- **Alimenté par** : Réseau électrique, Source chaleur (si roue déshydratante)
- **Contrôlé par** : Hygromètre (capteur HR), DDC Controller, BMS
- **Interagit avec** : AHU, Pompe de relevage condensats, Réchauffage

## Quantité Typique par Bâtiment
- Petit (5 étages) : 0-2 unités (si besoin spécifique)
- Moyen (15 étages) : 2-5 unités
- Grand (30+ étages) : 5-15 unités

## Sources
- Haystack Project - Dehumidifier Equipment
- Brick Schema - Dehumidifier Classes
- BACnet Standard - Humidity Control
- ASHRAE Handbook - Dehumidification
