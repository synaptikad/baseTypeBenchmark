# Car Operating Panel

## Identifiant
- **Code** : CAR_PANEL
- **Haystack** : elev + car + panel + equip
- **Brick** : brick:Car_Operating_Panel (subclass of brick:Interface_Panel)

## Description
Panneau de commande à l'intérieur de la cabine d'ascenseur permettant la sélection des étages de destination et l'accès aux fonctions spéciales. Interface principale entre passagers et système de contrôle.

## Fonction
Permettre aux passagers de sélectionner leur étage de destination, ouvrir/fermer les portes manuellement, déclencher l'alarme d'urgence, et communiquer avec l'extérieur. Interface utilisateur principal en cabine.

## Variantes Courantes
- **Panneau à boutons standards** : Boutons mécaniques classiques
- **Panneau tactile** : Écran tactile avec interface graphique
- **Panneau avec badge** : Lecteur de badge intégré
- **Panneau PMR** : Hauteur adaptée + braille + vocal
- **Panneau VIP** : Fonctions étage privé/express

## Caractéristiques Techniques Typiques
- Boutons illuminés pour chaque étage
- Afficheur position et direction
- Bouton ouverture/fermeture portes
- Bouton alarme et interphone
- Éclairage LED ou LCD
- Lecteur badge/NFC (optionnel)
- Braille et pictos tactiles (PMR)
- Communication : Bus série (RS-485, CAN)
- Matériaux résistants au vandalisme

## Localisation Typique
- Paroi latérale ou frontale de cabine
- Hauteur standard : 90-120 cm
- Panneau PMR additionnel : 80-100 cm
- À l'intérieur de chaque cabine d'ascenseur

## Relations avec Autres Équipements
- **Alimente** : N/A
- **Alimenté par** : Elevator Controller (basse tension)
- **Contrôlé par** : N/A (interface utilisateur)
- **Supervise par** : Elevator Controller
- **Interagit avec** : Emergency Communication Panel, Access Control Reader

## Quantité Typique par Bâtiment
- Petit (5 étages) : 1-2 panneaux (1 par cabine)
- Moyen (15 étages) : 4-8 panneaux (1 par cabine)
- Grand (30+ étages) : 12-32 panneaux (1 par cabine, certains 2 si PMR)

## Sources
- Haystack Project 4.0 - Interface equipment tagging
- Brick Schema - Interface panel classes
- EN 81-70:2018 - Accessibility for persons with disabilities
- ASME A17.1 - Car operating panel requirements
