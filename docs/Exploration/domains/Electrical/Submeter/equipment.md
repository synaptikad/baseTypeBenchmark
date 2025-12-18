# Sous-Compteur (Submeter / Divisional Meter)

## Identifiant
- **Code** : SUBMETER
- **Haystack** : elec-meter, submeter
- **Brick** : Electrical_Meter

## Description
Compteur d'énergie électrique installé en aval du compteur principal pour mesurer la consommation d'une zone spécifique, d'un locataire, d'un usage particulier ou d'un étage. Élément clé de la refacturation énergétique et du suivi détaillé par poste de consommation.

## Fonction
Mesurer la consommation électrique par zone, locataire ou usage spécifique. Permet la refacturation aux locataires, l'allocation des coûts énergétiques et l'identification des gisements d'économies. Essentiel pour les bâtiments multi-locataires et le monitoring énergétique détaillé.

## Variantes Courantes
- **Sous-compteur par locataire** : Refacturation individuelle
- **Sous-compteur par usage** : CVC, éclairage, prises, serveurs
- **Sous-compteur par étage** : Suivi vertical du bâtiment
- **Sous-compteur par aile** : Découpage horizontal
- **Sous-compteur MID** : Certifié pour facturation (directive européenne)

## Caractéristiques Techniques Typiques
- Précision : Classe 1 à B (IEC 62053), MID pour refacturation
- Mesures : Énergie active (kWh), parfois réactive (kVArh)
- Courant : 5A à 100A direct, ou via TC
- Communication : Modbus RTU/TCP, M-Bus, impulsions, BACnet
- Montage : Rail DIN compact (1 à 4 modules)
- Afficheur : LCD ou sans afficheur (lecture distante)

## Localisation Typique
- Tableaux divisionnaires par étage
- Coffrets par locataire/zone
- Armoires électriques dédiées
- En aval immédiat des départs TGBT

## Relations avec Autres Équipements
- **Mesure** : Consommation d'un sous-ensemble du bâtiment
- **Alimenté par** : TGBT ou tableau divisionnaire amont
- **En cascade de** : Compteur principal
- **Supervisé par** : Système EMS, GTB, plateforme de refacturation

## Quantité Typique par Bâtiment
- Petit (5 étages) : 5-20
- Moyen (15 étages) : 30-100
- Grand (30+ étages) : 100-300

## Sources
- Haystack v4 (submeter, elec-meter tags)
- Brick Schema (Electrical_Meter class)
- Directive MID 2014/32/UE (comptage facturation)
- Standards M-Bus et Modbus pour sous-comptage
