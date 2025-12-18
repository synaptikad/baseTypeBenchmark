# Destination Entry Panel

## Identifiant
- **Code** : DEST_PANEL
- **Haystack** : destination + entry + panel + equip
- **Brick** : brick:Destination_Entry_Panel (subclass of brick:Interface_Panel)

## Description
Terminal interactif permettant aux passagers de saisir leur étage de destination avant d'embarquer. Partie visible du système de destination dispatch. Affiche la cabine assignée après validation.

## Fonction
Recueillir la destination finale des passagers, communiquer avec le système d'affectation intelligent, indiquer quelle cabine utiliser. Optimise le regroupement des passagers par destination.

## Variantes Courantes
- **Terminal à clavier numérique** : Saisie manuelle du numéro d'étage
- **Terminal tactile** : Écran tactile avec interface graphique
- **Terminal avec badge** : Reconnaissance automatique de la destination autorisée
- **Terminal vocal** : Commande vocale pour PMR
- **Terminal mobile** : Via application smartphone

## Caractéristiques Techniques Typiques
- Écran tactile 7-10 pouces ou clavier numérique
- Afficheur LED indication cabine assignée
- Lecteur badge NFC/RFID intégré
- Connexion réseau Ethernet
- Protocoles : TCP/IP, REST API
- Interface multilingue
- Hauteur PMR : 80-120 cm
- Matériaux anti-vandalisme

## Localisation Typique
- Halls d'ascenseurs au rez-de-chaussée
- Chaque palier (systèmes avancés)
- Lobbies et zones d'accès
- Entrées de parkings

## Relations avec Autres Équipements
- **Alimente** : N/A
- **Alimenté par** : PoE ou alimentation locale
- **Contrôlé par** : N/A (interface utilisateur)
- **Supervise par** : Destination Dispatch System
- **Interagit avec** : Access Control System, Group Controller, Mobile Applications

## Quantité Typique par Bâtiment
- Petit (5 étages) : 0 terminaux (système non installé)
- Moyen (15 étages) : 2-8 terminaux (si système installé)
- Grand (30+ étages) : 8-40 terminaux (lobby + étages clés)

## Sources
- Haystack Project 4.0 - Destination entry equipment
- Brick Schema - Interface panel subclasses
- CIBSE Guide D - Destination control systems
- Smart building user interface standards
