# Digital Video Recorder (DVR)

## Identifiant
- **Code** : DVR
- **Haystack** : dvr
- **Brick** : brick:Video_Server

## Description
Enregistreur vidéo numérique conçu pour recevoir et encoder des signaux vidéo analogiques (BNC) provenant de caméras analogiques traditionnelles. Convertit les signaux en format numérique pour stockage. Moins courant dans les nouvelles installations mais encore présent dans les systèmes legacy ou hybrides.

## Fonction
Réception de signaux vidéo analogiques, numérisation et compression, enregistrement sur disques, lecture et export de vidéos, détection de mouvement, gestion d'événements.

## Variantes Courantes
- **DVR standalone** : 4-16 canaux, boîtier autonome
- **Hybrid DVR (HDVR)** : Supporte analogique + IP
- **Tribrid DVR** : Analogique + HD-TVI/AHD/CVI + IP
- **DVR haute définition** : Supporte caméras analogiques HD (1080p)

## Caractéristiques Techniques Typiques
- Canaux : 4 à 64 entrées BNC
- Résolution : D1, 720p, 1080p (selon technologie)
- Compression : H.264, H.265
- Stockage : 1TB à 20TB (RAID optionnel)
- Entrées : BNC vidéo, audio, alarme
- Sorties : HDMI, VGA, BNC (loop-through)
- Réseau : Ethernet pour accès distant
- Frame rate : 25/30 fps PAL/NTSC
- Alimentation : 100-240V AC

## Localisation Typique
- Locaux de sécurité
- Salles techniques
- Locaux de maintenance (systèmes existants)

## Relations avec Autres Équipements
- **Alimente** : N/A
- **Alimenté par** : UPS, Power supply
- **Contrôlé par** : Video Management System (si intégration)
- **Reçoit de** : Analog Camera, Coaxial transmission
- **Envoie à** : Monitors, Client PCs (via réseau)
- **Interagit avec** : Alarm Panel (entrées/sorties alarme)

## Quantité Typique par Bâtiment
- Petit (5 étages) : 0-2 DVR (legacy)
- Moyen (15 étages) : 0-3 DVR (legacy)
- Grand (30+ étages) : 0-5 DVR (migration en cours vers IP)

## Sources
- DVR Technology Standards
- Brick Schema - Video Server Class
