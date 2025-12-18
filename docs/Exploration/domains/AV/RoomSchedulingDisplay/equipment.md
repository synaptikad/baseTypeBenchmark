# Room Scheduling Display

## Identifiant
- **Code** : ROOM_SCHED
- **Haystack** : N/A
- **Brick** : N/A

## Description
Écran tactile de gestion de réservation de salle installé à l'entrée des espaces de réunion. Équipement communicant via IP pour synchronisation avec calendriers et systèmes de réservation.

## Fonction
Affichage statut salle (libre/occupé), réservations courantes et à venir, réservation ad-hoc, check-in obligatoire, libération automatique. Synchronisation bidirectionnelle avec Exchange, Google Calendar, systèmes de booking corporate. Intégration possible avec contrôle AV.

## Variantes Courantes
- **Wall-Mount Scheduling Panel** : Panel fixe encastré, 7"-10"
- **E-Paper Scheduling Display** : E-ink ultra basse consommation
- **LED Status Light** : Indicateur lumineux simple rouge/vert
- **Multi-Room Display** : Panel affichant plusieurs salles adjacentes
- **Integrated Control Panel** : Scheduling + contrôle AV combinés

## Caractéristiques Techniques Typiques
- Taille écran : 7" à 13" typique
- Technologie : LCD tactile ou E-Paper
- Résolution : 800x600 à 1920x1080
- Connectivité : Ethernet PoE, WiFi
- Protocoles : EWS (Exchange Web Services), Google Calendar API, REST APIs
- Capteurs : Occupancy sensor (PIR, ultrasonic) optionnel
- LED indicators : Barre LED RGB pour statut visuel à distance
- Contrôle : HTTP API, MQTT, proprietary booking APIs
- Alimentation : PoE (802.3af/at), USB-C
- Sécurité : Privacy modes, authentication

## Localisation Typique
- Entrées de salles de réunion
- Entrées de salles de visioconférence
- Focus rooms et huddle rooms
- Salles de formation
- Espaces collaboration bookables

## Relations avec Autres Équipements
- **Intégré avec** : Calendar systems (Exchange, Google), Room booking platforms, Occupancy sensors
- **Contrôle** : AV Control Processor (certains modèles dual-function)
- **Alimente** : Lighting Controller, AV Control Processor (trigger meeting start)

## Quantité Typique par Bâtiment
- Petit (5 étages) : 10-25 displays
- Moyen (15 étages) : 40-100 displays
- Grand (30+ étages) : 120-300 displays

## Sources
- Room booking system integration standards
- Exchange Web Services (EWS) API documentation
- Workspace analytics and occupancy tracking
