# Dedicated Outdoor Air System (DOAS)

## Identifiant
- **Code** : DOAS
- **Haystack** : `doas-equip`
- **Brick** : `brick:DOAS`

## Description
Système dédié au traitement de l'air neuf extérieur (100% air neuf) avec déshumidification et récupération d'énergie. Fournit l'air neuf hygiénique aux zones tout en découplant la charge latente de la charge sensible traitée par les terminaux.

## Fonction
Traiter et fournir l'air neuf de ventilation avec un contrôle précis de l'humidité. Permet de découpler le traitement de l'air neuf (charge latente) du traitement de zone (charge sensible), optimisant l'efficacité globale.

## Variantes Courantes
- **DOAS avec ERV** : Récupération enthalpique sur air extrait
- **DOAS avec roue déshydratante** : Déshumidification par adsorption
- **DOAS avec batterie froide** : Déshumidification par refroidissement
- **DOAS avec réchauffage** : Réchauffe l'air après déshumidification
- **DOAS pour chilled beams** : Fournit air primaire aux poutres froides

## Caractéristiques Techniques Typiques
- Débit d'air : 1,000 - 50,000 m³/h (100% air neuf)
- Déshumidification : Point de rosée cible 10-12°C
- Récupération énergie : 50-80% efficacité
- Température soufflage : 14-18°C (neutre ou légèrement refroidi)
- Protocoles : BACnet, Modbus, LON
- Points de supervision : températures, HR, débits, positions registres

## Localisation Typique
- Toiture
- Local technique
- Proximité des terminaux alimentés

## Relations avec Autres Équipements
- **Alimente** : Chilled Beams, VAV (air primaire), Zones (air neuf)
- **Alimenté par** : Chiller (eau glacée), Boiler (eau chaude), ERV/HRV
- **Contrôlé par** : DDC Controller, BMS
- **Interagit avec** : Terminaux de zone, Systèmes d'extraction

## Quantité Typique par Bâtiment
- Petit (5 étages) : 1-2 unités
- Moyen (15 étages) : 2-5 unités
- Grand (30+ étages) : 5-15 unités

## Sources
- ASHRAE DOAS Design Guide
- Greenheck DOAS Documentation
- Project Haystack - DOAS Equipment
- ASHRAE Standard 62.1 - Ventilation
