# Access Controller

## Identifiant
- **Code** : ACCESS_CTRL
- **Haystack** : access-controller
- **Brick** : brick:Access_Control_Panel

## Description
Unité de contrôle intelligent gérant l'authentification et l'autorisation d'accès pour une ou plusieurs portes. Stocke les bases de données d'utilisateurs et droits d'accès, valide les credentials, enregistre les événements et commande les dispositifs de verrouillage. Peut fonctionner en mode autonome ou connecté à un serveur central.

## Fonction
Validation des identifiants reçus des lecteurs de badges, application des politiques d'accès (horaires, zones), gestion des événements de sécurité, commande des serrures électriques et interface avec le système de gestion de sécurité central.

## Variantes Courantes
- **Contrôleur simple porte** : Gère 1 porte avec 1-2 lecteurs
- **Contrôleur multi-portes** : Gère 2-32 portes simultanément
- **Contrôleur de zone** : Gère un ensemble de portes dans une zone définie
- **Contrôleur intelligent (edge)** : Capacités de traitement avancées, IA locale
- **Contrôleur PoE** : Alimentation et communication via Ethernet

## Caractéristiques Techniques Typiques
- Capacité : 1 à 64 portes par contrôleur
- Stockage : 10 000 à 500 000 utilisateurs selon modèle
- Événements stockés : 50 000 à 1 000 000
- Communication : TCP/IP, RS-485, Wi-Fi
- Protocoles : OSDP, Wiegand (entrée), REST API, BACnet (intégration BMS)
- Alimentation : 12-24V DC, PoE+
- Mode autonome en cas de perte réseau
- Chiffrement des données (AES-128/256)
- Horloge temps réel avec backup batterie

## Localisation Typique
- Locaux techniques (armoires de communication)
- Proximité des portes contrôlées
- Salles serveurs sécurisées
- Faux-plafonds techniques
- Gaines techniques

## Relations avec Autres Équipements
- **Alimente** : Electric Lock, Magnetic Lock, Electric Strike
- **Alimenté par** : Power supply, PoE switch, UPS
- **Contrôlé par** : Access Control Server, Security Management System
- **Reçoit de** : Badge Reader, Biometric Reader, Request-to-Exit Sensor, Door Contact
- **Envoie à** : Alarm Panel, Video Management System (event triggering)

## Quantité Typique par Bâtiment
- Petit (5 étages) : 2-5 contrôleurs
- Moyen (15 étages) : 10-25 contrôleurs
- Grand (30+ étages) : 30-80 contrôleurs

## Sources
- SIA OSDP Specification
- BACnet Security Objects Specification
- Brick Schema - Access Control Panel
- ONVIF Physical Access Control Service Specification
