# Sprinkler System

## Identifiant
- **Code** : SPRINKLER
- **Haystack** : sprinkler
- **Brick** : brick:Sprinkler

## Description
Système automatique d'extinction incendie par eau, composé de têtes sprinkler (sprinklers) réparties au plafond qui s'activent individuellement lorsque la température dépasse un seuil. Chaque tête libère un jet d'eau pulvérisée pour contrôler ou éteindre le feu.

## Fonction
Détecte et combat automatiquement un incendie en déversant de l'eau directement sur le foyer. Activation locale par fusion d'ampoule ou élément fusible. Système le plus efficace pour la protection des biens et des personnes dans les bâtiments.

## Variantes Courantes
- **Réseau humide** : Canalisations remplies d'eau en permanence
- **Réseau sec** : Canalisations remplies d'air comprimé (zones hors gel)
- **Déluge** : Activation simultanée de toutes les têtes d'une zone
- **Pré-action** : Double détection avant mise en eau
- **ESFR (Early Suppression Fast Response)** : Gouttes grosses, réponse rapide
- **Sprinkler résidentiel** : Spécifique logements, débits adaptés
- **Têtes pendantes, montantes, latérales** : Selon configuration plafond

## Caractéristiques Techniques Typiques
- Température d'activation : 57°C, 68°C, 79°C, 93°C, 141°C selon classe
- Débit par tête : 80-300 L/min selon type
- Pression réseau : 1-12 bar
- Couverture par tête : 9-20 m² selon configuration
- Coefficient K : K80, K115, K160, K200, K240 selon débit
- Temps de réponse : RTI (Response Time Index) 50-350
- Couleur ampoule : Code température (orange=57°C, rouge=68°C, jaune=79°C)
- Certification : EN 12845, FM, UL 199

## Localisation Typique
- Bureaux et espaces tertiaires
- Entrepôts et zones de stockage
- Centres commerciaux
- Hôtels et résidences
- Parkings couverts
- Data centers
- Industries
- Locaux techniques

## Relations avec Autres Équipements
- **Alimente** : N/A (têtes passives activées par température)
- **Alimenté par** : Fire Pump, Water Tank, réseau ville
- **Contrôlé par** : Fire Alarm Panel (via flow switch et pressure switch)
- **Surveillé par** : Sprinkler Flow Switch, Pressure Switch, Tamper Switch
- **Déclenche** : Alarme sprinkler, arrêt ventilation, évacuation
- **Communique avec** : Building Management System (BMS) via supervision réseau

## Quantité Typique par Bâtiment
- Petit (5 étages, 2500 m²) : 150-300 têtes
- Moyen (15 étages, 15000 m²) : 800-1500 têtes
- Grand (30+ étages, 50000 m²) : 2500-5000 têtes

## Sources
- EN 12845: Fixed firefighting systems - Automatic sprinkler systems
- NFPA 13: Standard for the Installation of Sprinkler Systems
- Brick Schema: https://brickschema.org/
- Project Haystack: https://project-haystack.org/
- Règle APSAD R1: Extinction automatique à eau type sprinkler
