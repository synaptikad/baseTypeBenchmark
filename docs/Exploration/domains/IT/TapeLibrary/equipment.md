# Tape Library

## Identifiant
- **Code** : STOR-TAPE
- **Haystack** : N/A
- **Brick** : N/A

## Description
Système automatisé de stockage sur bandes magnétiques avec robotique pour manipulation des cartouches. Solution d'archivage long terme et backup économique pour grandes capacités de données.

## Fonction
Fournit stockage offline ou nearline économique pour archivage légal, disaster recovery et conservation long terme. Robot automatise chargement/déchargement des bandes, lecture/écriture via drives LTO ou autres formats. Monitoring via SNMP et interfaces propriétaires.

## Variantes Courantes
- **Entry-level library** : 1-2 drives, 20-40 slots (petites capacités)
- **Midrange library** : 2-8 drives, 100-500 slots
- **Enterprise library** : 8-32+ drives, 1000-10000+ slots, capacité PB
- **Virtual Tape Library (VTL)** : Émulation bande sur disque
- **Scalable library** : Architecture modulaire extensible

## Caractéristiques Techniques Typiques
- Formats : rack-mount (6U-42U) ou cabinet standalone
- Capacité : 50 TB à 100+ PB (avec compression)
- Technologie : LTO-7/8/9 (6-18 TB par cartouche native)
- Drives : 1 à 32+ lecteurs simultanés
- Robotique : bras mécanique ou rail pour manipulation cartouches
- Interface : FC, SAS, iSCSI pour connexion drives
- Management : Web GUI, SNMP, RSM (Removable Storage Manager)
- Consommation : 200W à 2000W+ selon taille

## Localisation Typique
- Datacenter (zone backup/archivage)
- Salle serveur principale
- Site de disaster recovery
- Coffre-fort numérique (air-gapped backup)

## Relations avec Autres Équipements
- **Alimente** : Backup long terme, archivage compliance, disaster recovery
- **Alimenté par** : PDU, UPS
- **Contrôlé par** : Backup software, media management, monitoring centralisé
- **Connecté à** : Backup servers, SAN fabric (FC), LAN (iSCSI)
- **Refroidi par** : Climatisation salle technique

## Quantité Typique par Bâtiment
- Petit (5 étages) : 0-1 library (souvent remplacé par disk backup)
- Moyen (15 étages) : 1-2 libraries (production + DR)
- Grand (30+ étages) : 2-5 libraries (multi-sites, archivage massif)

## Sources
- LTO Ultrium technology specifications
- Tape library automation documentation
- SNMP monitoring for tape systems
- Long-term data retention best practices
