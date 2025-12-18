# Pump (Pompe)

## Identifiant
- **Code** : PMP / P
- **Haystack** : `pump-equip`
- **Brick** : `brick:Pump`

## Description
Équipement mécanique qui assure la circulation des fluides (eau chaude, eau glacée, eau condenseur) dans les circuits hydrauliques du système HVAC. Peut être à vitesse fixe ou variable (VFD).

## Fonction
Maintenir la circulation et la pression nécessaires dans les boucles hydrauliques pour distribuer l'énergie thermique (chaud/froid) aux équipements terminaux et centraux.

## Variantes Courantes
- **Pompe primaire** : Circuit production (chiller/boiler)
- **Pompe secondaire** : Circuit distribution (découplage hydraulique)
- **Pompe de charge** : Remplissage/maintien pression
- **Pompe à vitesse fixe** : Débit constant
- **Pompe à vitesse variable (VFD)** : Débit modulable selon besoin
- **Pompes en parallèle** : Redondance et modulation de débit
- **Pompe condenseur** : Circuit cooling tower

## Caractéristiques Techniques Typiques
- Débit : 5 - 500 m³/h
- Hauteur manométrique totale (HMT) : 10 - 100 mCE
- Puissance moteur : 0.5 - 100 kW
- Rendement : 60-85%
- Protocoles : BACnet, Modbus (via VFD ou contrôleur)
- Points de supervision : état marche/arrêt, vitesse (si VFD), débit, pression différentielle, alarmes

## Localisation Typique
- Sous-sol technique (plantroom)
- Chaufferie/centrale frigorifique
- Proximité des équipements de production (chillers, boilers)

## Relations avec Autres Équipements
- **Alimente** : AHU, FCU, Radiant systems, Terminaux (circuits hydrauliques)
- **Alimenté par** : Chiller, Boiler, Heat Pump, Cooling Tower
- **Contrôlé par** : Plant Controller, VFD, BMS
- **Interagit avec** : Vannes de régulation, Capteurs de pression différentielle, Ballons tampons

## Quantité Typique par Bâtiment
- Petit (5 étages) : 4-10 pompes (chaud/froid/condenseur)
- Moyen (15 étages) : 10-30 pompes
- Grand (30+ étages) : 30-100 pompes

## Sources
- Haystack Project - Water Equipment
- Brick Schema - Pump Classes
- BACnet Standard - Hydronic Systems
- ASHRAE Handbook - Hydronic Heating and Cooling
