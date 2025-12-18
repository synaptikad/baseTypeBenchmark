# Door Controller

## Identifiant
- **Code** : DOOR_CTRL
- **Haystack** : door-controller
- **Brick** : brick:Door_Controller

## Description
Module électronique dédié à la gestion et au monitoring d'une porte sécurisée. Gère la logique de contrôle de la serrure, surveille l'état de la porte (ouverte/fermée/forcée), gère les temporisations, et interface avec les capteurs associés (REX, contact de porte). Souvent intégré ou connecté à un contrôleur d'accès.

## Fonction
Gestion locale d'une porte : commande de serrure, monitoring d'état, détection d'anomalies (porte forcée, maintenue ouverte), gestion des demandes de sortie, application des temporisations d'ouverture.

## Variantes Courantes
- **Intégré au contrôleur d'accès** : Fonctions intégrées dans le contrôleur principal
- **Module autonome** : Boîtier séparé dédié à une porte
- **Interface relais simple** : Gestion basique sans intelligence
- **Contrôleur intelligent** : Avec logique avancée et diagnostics

## Caractéristiques Techniques Typiques
- Entrées : Door Contact, Request-to-Exit, Emergency Release
- Sorties : Lock Control (relais), Door Status LED
- Temporisations configurables : Door open time, Door held open alarm
- Détection : Door forced open, Door held open
- Communication : RS-485, Wiegand, TCP/IP
- Alimentation : 12-24V DC
- Modes : Normal, Locked, Unlocked, Card only, Office mode

## Localisation Typique
- Proximité immédiate de chaque porte contrôlée
- Intégré dans cadre de porte
- Boîtier mural adjacent à la porte
- Faux-plafond au-dessus de la porte

## Relations avec Autres Équipements
- **Alimente** : Electric Lock, Magnetic Lock, Electric Strike
- **Alimenté par** : Access Controller, Power supply
- **Contrôlé par** : Access Controller
- **Reçoit de** : Door Contact, Request-to-Exit Sensor, Emergency Break Glass
- **Envoie à** : Access Controller (status and events)

## Quantité Typique par Bâtiment
- Petit (5 étages) : 10-30 contrôleurs
- Moyen (15 étages) : 50-150 contrôleurs
- Grand (30+ étages) : 200-500 contrôleurs

## Sources
- OSDP Connection and Control Specifications
- Building Access Control Standards
- Brick Schema Door Controller Class
