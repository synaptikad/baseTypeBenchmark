# Variable Refrigerant Flow (VRF/VRV)

## Identifiant
- **Code** : VRF / VRV
- **Haystack** : `vrf-equip`
- **Brick** : `brick:VRF`

## Description
Système de climatisation multi-split permettant de connecter plusieurs unités intérieures à une ou plusieurs unités extérieures via des tuyauteries de fluide frigorigène. Moduler individuellement la capacité de chaque unité intérieure avec un débit de réfrigérant variable.

## Fonction
Assurer le conditionnement d'air (chaud et/ou froid) de multiples zones du bâtiment avec régulation individuelle, sans réseau hydraulique. Alternative aux systèmes à eau glacée/eau chaude.

## Variantes Courantes
- **VRF 2 tubes** : Chaud OU froid (toutes les unités dans le même mode)
- **VRF 3 tubes** : Chaud ET froid simultanés (avec récupération d'énergie)
- **VRF à récupération de chaleur** : Transfert énergie entre zones (Heat Recovery)
- **VRF à pompe à chaleur** : Réversible chaud/froid
- **VRF à condensation par air** : Unité extérieure refroidie par air
- **VRF à condensation par eau** : Unité extérieure refroidie par eau

## Caractéristiques Techniques Typiques
- Puissance unité extérieure : 10 - 150 kW
- Nombre d'unités intérieures par extérieure : 3 - 64 unités
- Longueur tuyauterie : jusqu'à 150m (selon fabricant)
- Dénivelé max : 50-90m
- COP/EER : 3.0 - 5.5
- Protocoles : BACnet, Modbus, protocole propriétaire
- Points de supervision : modes unités intérieures, températures zones, puissances, alarmes

## Localisation Typique
- Unité extérieure : toiture, sol extérieur
- Unités intérieures : bureaux, salles de réunion, open spaces (mural, cassette, gainable, console)

## Relations avec Autres Équipements
- **Alimente** : Zones du bâtiment (air conditionné)
- **Alimenté par** : Réseau électrique (unité extérieure)
- **Contrôlé par** : Télécommandes locales, Contrôleur centralisé, BMS (via gateway)
- **Interagit avec** : Thermostats de zone, Systèmes de gestion d'énergie

## Quantité Typique par Bâtiment
- Petit (5 étages) : 1-3 systèmes (3-30 unités intérieures)
- Moyen (15 étages) : 5-15 systèmes (50-200 unités intérieures)
- Grand (30+ étages) : 15-40 systèmes (200-800 unités intérieures)

## Sources
- Haystack Project - VRF Equipment
- Brick Schema - VRF Classes
- BACnet Integration Guides
- ASHRAE Handbook - DX Systems
