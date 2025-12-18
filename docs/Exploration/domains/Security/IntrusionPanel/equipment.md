# Intrusion Panel (Intrusion Alarm Panel)

## Identifiant
- **Code** : INTRUSION_PANEL
- **Haystack** : intrusion-panel
- **Brick** : brick:Intrusion_Alarm_Panel

## Description
Centrale d'alarme anti-intrusion gérant un ensemble de détecteurs (PIR, contacts, bris de vitre, etc.), de claviers d'armement et de sirènes. Supervise les zones, gère les modes d'armement (total, partiel, désarmé), traite les événements, déclenche les alarmes et notifie les services de télésurveillance.

## Fonction
Centralisation et traitement des événements intrusion, gestion des zones et partitions, armement/désarmement par code ou badge, génération d'alarmes locales et distantes, journal d'événements, télésurveillance, intégration avec contrôle d'accès et vidéo.

## Variantes Courantes
- **Centrale filaire** : 8-64 zones, détecteurs câblés
- **Centrale hybride** : Zones filaires + sans fil (868MHz)
- **Centrale IP** : Communication TCP/IP, supervision cloud
- **Centrale intégrée** : Combinée avec contrôle d'accès
- **Centrale distribuée** : Modules déportés, grandes installations

## Caractéristiques Techniques Typiques
- Zones : 8 à 512+ selon modèle
- Partitions : 1-32 zones logiques
- Sorties : 2-16 (sirènes, flashs, relais)
- Utilisateurs : 50-10000 codes/badges
- Communication : GSM, IP, PSTN, radio
- Protocoles : Contact ID, SIA, propriétaires
- Alimentation : 230V AC + batterie backup 7-18Ah
- Conformité : EN 50131 Grade 2/3
- Interface : Clavier LCD, écran tactile, app mobile

## Localisation Typique
- Locaux techniques sécurisés
- Armoires électriques protégées
- Salles de sécurité
- Zones non-publiques

## Relations avec Autres Équipements
- **Alimente** : Détecteurs intrusion, Sirènes, Claviers
- **Alimenté par** : Secteur + Batterie backup
- **Contrôle** : PIR, Door Contact, Glass Break, Sirens, Keypads
- **Envoie à** : Télésurveillance (ARC), VMS, BMS
- **Intègre avec** : Access Control, Video, Fire Alarm

## Quantité Typique par Bâtiment
- Petit (5 étages) : 1 centrale
- Moyen (15 étages) : 1-3 centrales
- Grand (30+ étages) : 3-10 centrales (distribuées)

## Sources
- EN 50131 - Alarm Systems Standard
- SIA DC-09 - Control Panel Standard
- Brick Schema - Intrusion Alarm Panel Class
