# Recording Server

## Identifiant
- **Code** : REC_SRV
- **Haystack** : N/A
- **Brick** : N/A

## Description
Serveur d'enregistrement vidéo pour capture et archivage de réunions, présentations et événements. Équipement communicant via API pour déclenchement enregistrement, gestion stockage et intégration calendriers.

## Fonction
Capture automatique ou manuelle de réunions et présentations avec indexation, transcription, archivage. Intégration avec calendriers pour enregistrement automatique basé sur métadonnées meeting. Post-processing (chapitrage, transcription AI, recherche). Distribution de replays via portail vidéo.

## Variantes Courantes
- **Appliance Recording Server** : Hardware dédié avec stockage local
- **Software Recording Solution** : VM ou container-based
- **Cloud Recording Service** : Intégré aux plateformes visio cloud (Zoom, Teams)
- **Lecture Capture System** : Spécialisé pour formation avec multi-stream sync
- **Meeting Intelligence Platform** : Recording + transcription + AI insights

## Caractéristiques Techniques Typiques
- Canaux simultanés : 4 à 64+ enregistrements parallèles
- Codecs : H.264, H.265 pour vidéo, AAC pour audio
- Résolution : 720p à 4K
- Sources : HDMI capture, IP streams (RTSP), screen capture, codec integration
- Storage : Local SSD/HDD, NAS, SAN, cloud storage (S3, Azure)
- Contrôle : REST API, calendar integration (Exchange, Google)
- Automation : Auto-start/stop via calendar, occupancy sensors
- Post-processing : Transcription (speech-to-text), chapitrage automatique
- Search : Full-text search dans transcriptions
- Sécurité : Encryption at-rest et in-transit, access control
- Distribution : Streaming portal, LMS integration

## Localisation Typique
- Data center interne
- Salle serveurs IT
- Locaux techniques AV (pour appliances)

## Relations avec Autres Équipements
- **Alimenté par** : Video Conference Codec, PTZ Camera, DSP, AV Matrix Switcher, Video Encoder
- **Contrôlé par** : AV Control Processor, Calendar systems, Touch Panel Controller
- **Intégré avec** : Streaming Server, Learning Management Systems, Content portals

## Quantité Typique par Bâtiment
- Petit (5 étages) : 1-2 servers
- Moyen (15 étages) : 2-5 servers
- Grand (30+ étages) : 5-12 servers (ou cloud-based)

## Sources
- Lecture capture system specifications
- Video recording and archiving standards
- Enterprise content management integration
