# Video Analytics Server

## Identifiant
- **Code** : VIDEO_ANALYTICS
- **Haystack** : video-analytics-server
- **Brick** : brick:Video_Analytics_Server

## Description
Serveur dédié au traitement et à l'analyse automatisée des flux vidéo en temps réel ou en post-traitement. Utilise l'intelligence artificielle et le machine learning pour détecter, classifier et analyser des événements, objets, comportements dans les images vidéo. Décharge les caméras et VMS des traitements intensifs.

## Fonction
Analyse vidéo avancée (deep learning), détection d'objets, reconnaissance faciale, comptage de personnes, analyse comportementale, détection d'anomalies, génération d'alertes intelligentes, métadonnées vidéo, intégration avec VMS et systèmes tiers.

## Variantes Courantes
- **Analytics générique** : Multi-applications (détection, comptage, classification)
- **Reconnaissance faciale** : Spécialisé identification/vérification faciale
- **ANPR/LPR** : Lecture automatique de plaques d'immatriculation
- **People counting** : Comptage et analyse de flux de personnes
- **Behavior analytics** : Détection comportements suspects, loitering, crowd detection
- **Perimeter protection** : Intrusion, line crossing, zone protection
- **GPU-accelerated** : Serveurs avec cartes graphiques pour IA

## Caractéristiques Techniques Typiques
- Capacité : 10 à 500+ flux simultanés
- Processeur : CPU multi-core + GPU (NVIDIA Tesla, RTX)
- Algorithmes : CNN, Deep Learning, Computer Vision
- Précision : 90-99% selon application et conditions
- Latence : 50ms-2s selon complexité
- Métadonnées : JSON, XML export
- Protocoles : ONVIF Analytics, RTSP, HTTP
- API : REST, gRPC, WebSocket
- Base de données : Pour stockage métadonnées et événements
- Intégration : VMS, Access Control, BMS

## Localisation Typique
- Salle serveurs
- Data center
- Edge servers (proximité caméras)
- Cloud (analytics déporté)

## Relations avec Autres Équipements
- **Alimente** : N/A
- **Alimenté par** : Server infrastructure, UPS
- **Contrôlé par** : Video Management System
- **Reçoit de** : IP Camera, NVR, Video Management System
- **Envoie à** : VMS, Alarm Panel, Access Controller, BMS, PSIM
- **Interagit avec** : Database Server, Access Control Database

## Quantité Typique par Bâtiment
- Petit (5 étages) : 0-1 serveur (analytics souvent intégré VMS/caméras)
- Moyen (15 étages) : 1-2 serveurs analytics
- Grand (30+ étages) : 2-5 serveurs analytics (ou cluster)

## Sources
- ONVIF Analytics Service Specification
- Deep Learning for Video Surveillance Standards
- Brick Schema - Video Analytics Server
