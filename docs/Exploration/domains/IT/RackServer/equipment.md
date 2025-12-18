# Rack Server

## Identifiant
- **Code** : RACK-SRV
- **Haystack** : N/A
- **Brick** : N/A

## Description
Serveur informatique au format rack (1U à 4U typiquement) conçu pour être monté dans une baie standard 19 pouces. Équipement compute principal des datacenters, exécutant des charges de travail applicatives, bases de données, ou services d'infrastructure.

## Fonction
Fournit la puissance de calcul et la capacité mémoire nécessaires pour exécuter les applications et services IT. Intégré dans un écosystème de supervision via IPMI, SNMP, ou agents logiciels pour le monitoring de la santé matérielle (CPU, RAM, températures, ventilateurs, alimentation).

## Variantes Courantes
- **Serveur 1U** : Format ultra-compact, haute densité, performance modérée
- **Serveur 2U** : Format standard, équilibre densité/performance/extensibilité
- **Serveur 4U** : Format haute performance, capacités d'extension maximales (GPU, stockage)
- **Serveur de stockage** : Optimisé pour hébergement de disques (jusqu'à 60+ baies)
- **Serveur GPU** : Équipé de cartes graphiques pour calcul IA/HPC

## Caractéristiques Techniques Typiques
- Format rack 19 pouces (hauteur 1U à 4U)
- Processeurs multi-coeurs (8 à 128+ coeurs par serveur)
- Mémoire RAM : 64 GB à 2+ TB
- Alimentation redondante : 2 PSU (500W à 2000W par unité)
- BMC (Baseboard Management Controller) pour gestion hors-bande
- Interfaces réseau : 2 à 8 ports (1GbE à 100GbE)
- Consommation typique : 200W à 800W en charge normale

## Localisation Typique
- Salle serveur (Server Room)
- Datacenter
- Local technique informatique
- Salle blanche (Clean Room) pour équipements critiques

## Relations avec Autres Équipements
- **Alimente** : Charges applicatives, services réseau, machines virtuelles
- **Alimenté par** : PDU (Power Distribution Unit), UPS
- **Contrôlé par** : DCIM, système de monitoring (SNMP/IPMI/Redfish), orchestrateur (Kubernetes, VMware)
- **Connecté à** : Network Switch (ToR - Top of Rack), Storage (SAN/NAS), KVM Switch
- **Refroidi par** : CRAC/CRAH, In-Row Cooling, système de ventilation datacenter

## Quantité Typique par Bâtiment
- Petit (5 étages) : 5-20 serveurs (petite salle serveur)
- Moyen (15 étages) : 20-100 serveurs (datacenter d'entreprise)
- Grand (30+ étages) : 100-1000+ serveurs (datacenter principal ou multi-sites)

## Sources
- Standards DCIM (Data Center Infrastructure Management)
- IPMI specification (Intelligent Platform Management Interface)
- Redfish API standard (DMTF)
- SNMP MIBs for server monitoring
