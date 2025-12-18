# Storage Array

## Identifiant
- **Code** : STOR-ARRAY
- **Haystack** : N/A
- **Brick** : N/A

## Description
Système de stockage centralisé composé de multiples disques et contrôleurs fournissant capacité et performance de stockage pour serveurs. Offre fonctions avancées (RAID, snapshots, réplication, thin provisioning) avec supervision exhaustive.

## Fonction
Fournit stockage partagé de haute disponibilité pour applications critiques, bases de données et virtualisation. Centralise la gestion des données avec redondance, protection et performances optimisées. Monitoring via API propriétaires, SNMP et SMI-S pour health, performance et capacité.

## Variantes Courantes
- **All-Flash Array (AFA)** : 100% SSD/NVMe pour performances maximales
- **Hybrid Array** : Mix SSD (cache/tier 1) et HDD (capacité/tier 2-3)
- **Unified Storage** : Support simultané block (SAN) et file (NAS)
- **Object Storage Array** : Stockage scale-out pour données non structurées
- **Midrange Array** : Solution équilibrée coût/performance pour entreprises

## Caractéristiques Techniques Typiques
- Formats : 2U à 42U (châssis + shelves d'extension)
- Capacité : 10 TB à plusieurs PB (raw)
- Performance : 100K à 10M+ IOPS
- Protocoles : FC, iSCSI, NFS, SMB, S3
- Contrôleurs : dual controllers actif/actif pour haute disponibilité
- Management : GUI web, CLI, REST API, SMI-S, SNMP
- Consommation : 500W à 5000W+ selon capacité

## Localisation Typique
- Datacenter (zone storage dédiée)
- Salle serveur principale
- SAN room (Storage Area Network)
- Backbone storage infrastructure

## Relations avec Autres Équipements
- **Alimente** : Stockage pour serveurs, VMs, bases de données, applications
- **Alimenté par** : PDU haute capacité, UPS critique
- **Contrôlé par** : Storage management software, DCIM, monitoring centralisé
- **Connecté à** : FC switches (SAN), Ethernet switches (iSCSI/NFS), serveurs (direct-attach)
- **Refroidi par** : CRAC/CRAH, climatisation précision datacenter

## Quantité Typique par Bâtiment
- Petit (5 étages) : 1-2 arrays (capacité limitée + backup)
- Moyen (15 étages) : 2-4 arrays (production + DR, tiers de performance)
- Grand (30+ étages) : 4-10+ arrays (multi-sites, multiple tiers)

## Sources
- SNIA (Storage Networking Industry Association) standards
- SMI-S specification for storage monitoring
- SAN architecture best practices
- Storage performance metrics and monitoring
