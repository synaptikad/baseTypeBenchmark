# Parking Guidance Controller

## Identifiant
- **Code** : GUIDANCE_CONTROLLER
- **Haystack** : N/A
- **Brick** : N/A

## Description
Contrôleur dédié au système de guidage parking. Collecte données de centaines de capteurs de places, agrège comptages par zone/étage, et pilote afficheurs de guidage et indicateurs individuels. Niveau intermédiaire entre capteurs et serveur central.

## Fonction
Agrégation et traitement local des données de capteurs de stationnement. Calcul comptages par zone en temps réel, commande des indicateurs lumineux et panneaux d'affichage, et remontée données vers Parking Management Server.

## Variantes Courantes
- **Contrôleur de zone** : Gère 50-200 capteurs d'une zone/étage
- **Contrôleur maître** : Agrège multiples contrôleurs de zone
- **Contrôleur intégré** : Edge computing dans afficheur principal
- **Version PoE** : Alimentation et communication Ethernet

## Caractéristiques Techniques Typiques
- Architecture : Microcontrôleur ou PC industriel embarqué
- Entrées : RS485 (capteurs), Ethernet (réseau)
- Sorties : RS485 (indicateurs), Ethernet (afficheurs, serveur)
- Capacité : 50-500 capteurs par contrôleur
- Protocoles : Modbus RTU/TCP, BACnet, MQTT, HTTP API
- Traitement : Agrégation comptages, filtrage données, détection anomalies
- Alimentation : 12-24V DC ou PoE
- Température opération : -20°C à +60°C
- Protection : IP40-IP54

## Localisation Typique
- Local technique parking (armoire électrique)
- Chaque zone/étage (contrôleurs distribués)
- Près des concentrateurs de capteurs
- Salle serveurs locale (version centralisée)

## Relations avec Autres Équipements
- **Alimente** : N/A
- **Alimenté par** : Distribution électrique 12-24V DC ou PoE
- **Contrôlé par** : Parking Management Server
- **Interagit avec** : Parking Sensor Ultrasonic/Magnetic (collecte données), Overhead Parking Indicator (commande LED), Parking Guidance Display (envoie comptages), Variable Message Sign (données disponibilités)

## Quantité Typique par Bâtiment
- Petit (parking 50 places) : 1 contrôleur (système centralisé)
- Moyen (parking 200 places) : 2-4 contrôleurs (par zone/étage)
- Grand (parking 1000+ places) : 5-15 contrôleurs (architecture distribuée)

## Sources
- Standards Modbus RTU/TCP
- Documentation systèmes guidage parking
- Protocoles BACnet, MQTT pour IoT
