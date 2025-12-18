# Lighting Scene Controller

## Identifiant
- **Code** : SCENE_CTRL
- **Haystack** : scene, controller, lighting
- **Brick** : brick:Scene_Controller, brick:Lighting_Scene_Controller

## Description
Dispositif permettant la mémorisation et le rappel de configurations d'éclairage prédéfinies (scènes). Une scène définit un ensemble de niveaux d'intensité, de couleurs, et d'états pour plusieurs luminaires, permettant de créer différentes ambiances lumineuses et de les activer instantanément par simple pression d'un bouton.

## Fonction
Stocker et exécuter des scénarios d'éclairage complexes impliquant plusieurs circuits, zones, et luminaires avec des niveaux de gradation différents. Permet la transition fluide entre différentes ambiances (présentation, réunion, pause, nettoyage, etc.) sans intervention manuelle individuelle sur chaque luminaire.

## Variantes Courantes
- **Wall-Mounted Scene Controller** : Panneau mural avec boutons de scène (4 à 8 scènes typiques)
- **Keypad Scene Controller** : Clavier programmable avec affichage LCD
- **Touchscreen Scene Controller** : Interface tactile graphique
- **Wireless Scene Controller** : Sans fil (Zigbee, Bluetooth, EnOcean)
- **Architectural Scene Controller** : Design haut de gamme pour espaces premium
- **Master Scene Controller** : Gestion multi-zones et scènes complexes
- **Preset Scene Controller** : Scènes préenregistrées non modifiables
- **Programmable Scene Controller** : Scènes configurables par l'utilisateur
- **Remote Scene Controller** : Télécommande portable pour activation des scènes

## Caractéristiques Techniques Typiques
- Nombre de scènes: 4 à 100+ selon modèle
- Zones contrôlées: 1 à 50+ zones
- Canaux par scène: 4 à 500+ canaux
- Résolution gradation: 8-bit (256 niveaux) à 16-bit
- Temps de transition: 0 à 60 secondes configurables
- Type de boutons: Tactile capacitif, mécanique, ou écran tactile
- Rétroéclairage: LED, configurable jour/nuit
- Gravure boutons: Personnalisable ou écran dynamique
- Alimentation: 12-24V DC, PoE, ou secteur
- Communication: DALI, DMX512, KNX, BACnet, Modbus, Zigbee, Bluetooth
- Feedback visuel: LED d'état par bouton, écran
- Montage: Boîtier encastré standard, surface, ou DIN rail
- Interface utilisateur: Boutons, rotary encoder, tactile
- Programmation: Logiciel PC, application mobile, ou interface web

## Localisation Typique
- Salles de réunion et conférence
- Auditoriums et salles de spectacle
- Espaces de restauration
- Halls de réception et lobbies
- Salles de classe et formation
- Showrooms et espaces commerciaux
- Espaces événementiels
- Salles de conseil et direction
- Entrées de zones multi-usages
- Postes de contrôle et régie

## Relations avec Autres Équipements
- **Alimente** : N/A
- **Alimenté par** : Electrical Panel, PoE Switch, Power Supply
- **Contrôlé par** : Building Automation System (programmation et supervision)
- **Contrôle** : LED Luminaire, Dimmer, Lighting Relay, Lighting Controller, parfois aussi Blind/Shade Controller
- **Communique avec** : DALI Gateway, DMX Controller, Lighting Controller

## Quantité Typique par Bâtiment
- Petit (5 étages) : 10-50
- Moyen (15 étages) : 50-200
- Grand (30+ étages) : 200-1,000

## Sources
- Haystack Project - Scene controller definitions
- Brick Schema - Scene Controller class
- IEC 62386 - DALI scene control (Part 102, 103)
- ANSI E1.20 - RDM (Remote Device Management) for DMX
- Building automation best practices
- Commercial lighting control system specifications
