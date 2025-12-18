# Video Wall Controller

## Identifiant
- **Code** : VIDEOWALL_CTRL
- **Haystack** : N/A
- **Brick** : N/A

## Description
Processeur vidéo spécialisé pour gestion de murs d'images (video walls) multi-écrans. Équipement communicant via IP pour contrôle de layouts, sources et configuration.

## Fonction
Orchestration de multiples displays en configuration mur d'images : gestion du bezel compensation, layouts dynamiques, répartition d'image unique sur multiple écrans, fenêtrage multi-sources. Contrôle centralisé et présets de configurations. Utilisé pour command centers, lobbies, salles immersives.

## Variantes Courantes
- **Hardware Video Wall Processor** : Appliance dédiée avec multiples sorties HDMI/DisplayPort
- **Software Video Wall** : Solution logicielle sur serveur GPU
- **LED Video Wall Controller** : Spécialisé pour LED tiles, support résolutions custom
- **4K/8K Video Wall Controller** : Support entrées/sorties ultra-haute résolution
- **Modular Video Wall System** : Châssis avec cartes I/O expansibles

## Caractéristiques Techniques Typiques
- Sorties : 4 à 64 outputs HDMI/DisplayPort
- Entrées : 4 à 32 sources (HDMI, SDI, IP streams)
- Résolution max : 4K60 par output, total canvas jusqu'à 32K
- Configuration : 2x2 à 16x16 displays (ou plus)
- Bezel compensation : Automatic ou manuel
- Layouts : Preset et custom, PIP/POP, zones multiples
- Contrôle : HTTP API, Telnet, RS-232, proprietary software
- Scaling : Per-window scaling, rotation
- Latency : <50ms
- Genlock : Frame synchronization entre displays

## Localisation Typique
- Centres de contrôle et NOC (Network Operations Center)
- Lobbies et halls d'entrée
- Salles de crise
- Salles de trading
- Show rooms et espaces événementiels

## Relations avec Autres Équipements
- **Alimente** : Display (video wall), LED Video Wall Panel
- **Alimenté par** : AV Matrix Switcher, Video Encoder, Media Server, IP cameras, Streaming Server
- **Contrôlé par** : AV Control Processor, Touch Panel Controller
- **Connecté via** : Video Distribution Amplifier

## Quantité Typique par Bâtiment
- Petit (5 étages) : 0-2 controllers
- Moyen (15 étages) : 2-5 controllers
- Grand (30+ étages) : 5-15 controllers

## Sources
- Video wall technology documentation
- Display synchronization and bezel compensation
- Command center video wall design standards
