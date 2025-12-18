# Network Attached Storage (NAS)

## Identifiant
- **Code** : STOR-NAS
- **Haystack** : N/A
- **Brick** : N/A

## Description
Serveur de fichiers dédié connecté au réseau fournissant stockage partagé via protocoles NFS, SMB/CIFS ou AFP. Optimisé pour partage de fichiers, collaboration et archivage avec interface de gestion simplifiée.

## Fonction
Centralise le stockage de fichiers pour utilisateurs et applications avec accès réseau. Offre gestion simplifiée, protection des données (RAID, snapshots), et services de fichiers (quotas, ACL, versioning). Supervisable via SNMP, API REST et dashboard web.

## Variantes Courantes
- **NAS entreprise** : Haute capacité et performance pour grands déploiements
- **NAS PME** : Solution compacte et économique pour petites installations
- **NAS scale-out** : Architecture distribuée pour capacité massive
- **NAS backup** : Optimisé pour sauvegarde et archivage (déduplication)
- **NAS vidéo** : Spécialisé pour stockage surveillance et médias

## Caractéristiques Techniques Typiques
- Formats : boîtier compact (2-4 baies) à rack 2U-4U (12-24 baies)
- Capacité : 4 TB à 1+ PB
- Performance : 100 MB/s à 10+ GB/s
- Protocoles : NFS, SMB/CIFS, AFP, FTP, WebDAV
- RAID : 0, 1, 5, 6, 10 (protection données)
- Network : 1 GbE à 100 GbE, agrégation de liens
- Management : Web GUI, SSH, SNMP, REST API
- Consommation : 50W à 500W selon taille

## Localisation Typique
- Salle serveur
- Local technique informatique
- Datacenter (zone file services)
- Branch office (sites distants)

## Relations avec Autres Équipements
- **Alimente** : Stockage fichiers partagés, home directories, partages collaboration
- **Alimenté par** : PDU, UPS
- **Contrôlé par** : Monitoring centralisé, backup software, DCIM
- **Connecté à** : Network switches (LAN), serveurs de backup
- **Refroidi par** : Climatisation salle technique

## Quantité Typique par Bâtiment
- Petit (5 étages) : 1-2 NAS (primaire + backup)
- Moyen (15 étages) : 2-5 NAS (départements, backup, archivage)
- Grand (30+ étages) : 5-15 NAS (multi-sites, usages spécialisés)

## Sources
- NFS protocol specifications (RFC 1813, RFC 7530)
- SMB/CIFS protocol documentation
- NAS monitoring best practices
- SNMP MIBs for NAS appliances
