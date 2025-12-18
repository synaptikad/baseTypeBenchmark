# Hall Call Station

## Identifiant
- **Code** : HALL_CALL
- **Haystack** : elev + hall + call + station + equip
- **Brick** : brick:Hall_Call_Station (subclass of brick:Interface_Panel)

## Description
Borne d'appel située à chaque palier permettant d'appeler un ascenseur. Équipement d'interface entre passagers et système de gestion des ascenseurs. Affiche la position et direction des cabines.

## Fonction
Permettre aux passagers d'appeler un ascenseur depuis un palier en indiquant leur direction souhaitée (montée ou descente). Afficher l'arrivée et la direction des cabines disponibles.

## Variantes Courantes
- **Borne simple montée/descente** : 2 boutons classiques
- **Borne avec afficheur digital** : Position et temps d'attente
- **Borne avec badge** : Contrôle d'accès intégré
- **Borne vocale PMR** : Annonce sonore pour malvoyants
- **Borne de destination** : Saisie étage (voir Destination Entry Panel)

## Caractéristiques Techniques Typiques
- Boutons montée/descente illuminés
- Afficheur LED ou LCD (position cabines)
- Gong d'arrivée
- Indicateur direction (flèches)
- Matériaux résistants (inox, laiton)
- Communication : Bus série (RS-485, CAN)
- Lecteur badge NFC/RFID (optionnel)
- Alimentation : 12-24V DC depuis contrôleur

## Localisation Typique
- Chaque palier devant les ascenseurs
- Mur face aux portes d'ascenseur
- Hauteur standard : 110-140 cm
- Espaces de circulation verticale

## Relations avec Autres Équipements
- **Alimente** : N/A
- **Alimenté par** : Elevator Controller ou Group Controller
- **Contrôlé par** : N/A (interface utilisateur)
- **Supervise par** : Elevator Controller, Group Controller
- **Interagit avec** : Access Control System, Destination Dispatch System

## Quantité Typique par Bâtiment
- Petit (5 étages) : 8-10 bornes (2 par étage x 1-2 ascenseurs)
- Moyen (15 étages) : 30-60 bornes (2 par étage x 4-8 ascenseurs)
- Grand (30+ étages) : 60-180 bornes (selon zones et nombre d'ascenseurs)

## Sources
- Haystack Project 4.0 - Hall call equipment tagging
- Brick Schema - Interface equipment classes
- EN 81-20:2020 - Landing call registration devices
- Elevator signaling and interface standards
