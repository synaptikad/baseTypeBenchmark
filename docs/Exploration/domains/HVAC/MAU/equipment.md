# Makeup Air Unit (MAU)

## Identifiant
- **Code** : MAU
- **Haystack** : `mau-equip`
- **Brick** : `brick:Makeup_Air_Unit`

## Description
Unité de traitement d'air dédiée exclusivement à l'apport d'air neuf extérieur (100% air neuf, 0% recyclage). Compense l'air extrait par les systèmes d'extraction (cuisines, laboratoires, salles blanches) et maintient la pression du bâtiment.

## Fonction
Fournir l'air neuf hygiénique nécessaire au bâtiment en traitant uniquement l'air extérieur. Maintenir l'équilibre des débits d'air et la pressurisation du bâtiment. Souvent utilisé avec systèmes à forte extraction.

## Variantes Courantes
- **MAU avec chauffage seul** : Préchauffe l'air neuf (hiver)
- **MAU avec chauffage et refroidissement** : Traitement complet
- **MAU avec récupération d'énergie** : ERV/HRV intégré
- **MAU tempéré** : Traitement minimal (température neutre)
- **MAU pour cuisines** : Compense extraction hottes

## Caractéristiques Techniques Typiques
- Débit d'air : 2,000 - 50,000 m³/h (100% air neuf)
- Traitement : Filtration, chauffage, refroidissement (optionnel), humidification (optionnel)
- Récupération énergie : ERV/HRV souvent intégré
- Protocoles : BACnet, Modbus, LON
- Points de supervision : débit air neuf, températures, pressions, positions registres

## Localisation Typique
- Toiture
- Sous-sol technique
- Local technique dédié

## Relations avec Autres Équipements
- **Alimente** : Réseau de distribution d'air neuf, AHU (complément), Zones du bâtiment
- **Alimenté par** : Chiller (si refroidissement), Boiler/Heat Pump (chauffage), ERV/HRV (récupération)
- **Contrôlé par** : DDC Controller, BMS
- **Interagit avec** : Exhaust Fans (équilibrage), Dampers, Capteurs CO2/qualité air

## Quantité Typique par Bâtiment
- Petit (5 étages) : 1-2 unités
- Moyen (15 étages) : 2-5 unités
- Grand (30+ étages) : 5-15 unités

## Sources
- Haystack Project - MAU Equipment
- Brick Schema - Makeup Air Unit
- BACnet Standard - Air Handling
- ASHRAE Standard 62.1 - Ventilation Requirements
