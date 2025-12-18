# Evaporative Cooler (Rafraîchisseur évaporatif)

## Identifiant
- **Code** : EVAP
- **Haystack** : `evaporativeCooler-equip`
- **Brick** : `brick:Evaporative_Cooler`

## Description
Système de refroidissement qui utilise l'évaporation de l'eau pour abaisser la température de l'air. Efficace dans les climats secs, consomme peu d'énergie mais augmente l'humidité de l'air traité.

## Fonction
Refroidir l'air par évaporation d'eau sur un média humide. Alternative économique à la climatisation mécanique dans les régions à faible humidité. Utilisé pour le confort ou le pré-refroidissement de l'air neuf.

## Variantes Courantes
- **Direct evaporative cooler** : L'air passe directement sur le média humide
- **Indirect evaporative cooler** : Échangeur à plaques, air primaire non humidifié
- **Indirect-direct (2-stage)** : Combinaison des deux méthodes
- **Roof-mounted evaporative cooler** : Installation en toiture
- **Portable evaporative cooler** : Unité mobile

## Caractéristiques Techniques Typiques
- Débit d'air : 1,000 - 50,000 m³/h
- Efficacité évaporative : 70-90% (direct), 50-70% (indirect)
- Consommation électrique : 0.1-0.3 kW/1000 m³/h
- Consommation eau : 5-15 l/h par 1000 m³/h
- Protocoles : BACnet, Modbus, relais
- Points de supervision : températures, humidités, niveau eau, état pompe

## Localisation Typique
- Toiture
- Mur extérieur
- Zone de production industrielle
- Entrepôts

## Relations avec Autres Équipements
- **Alimente** : Zone (air rafraîchi)
- **Alimenté par** : Air extérieur, Réseau d'eau
- **Contrôlé par** : Thermostat, BMS
- **Interagit avec** : Ventilation, Extraction (apport air neuf important)

## Quantité Typique par Bâtiment
- Petit (5 étages) : 0-2 unités (selon climat)
- Moyen (15 étages) : 2-10 unités
- Grand (30+ étages) : 10-30 unités (zones industrielles)

## Sources
- ASHRAE Handbook - HVAC Systems
- Project Haystack - Evaporative Cooler Equipment
- Brick Schema - Evaporative Cooler Class
- Munters / Seeley - Evaporative Cooling Documentation
