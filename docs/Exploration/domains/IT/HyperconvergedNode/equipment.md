# Hyperconverged Node

## Identifiant
- **Code** : HCI-NODE
- **Haystack** : N/A
- **Brick** : N/A

## Description
Nœud d'infrastructure hyperconvergée intégrant calcul, stockage et virtualisation réseau dans une appliance unifiée. Forme un cluster distribué avec d'autres nœuds pour fournir une infrastructure software-defined complète.

## Fonction
Fournit une infrastructure IT complète (compute, storage, network) dans un modèle scale-out, éliminant la séparation traditionnelle entre serveurs et SAN. Chaque nœud contribue ses ressources à un pool partagé géré de manière distribuée.

## Variantes Courantes
- **Nœud all-flash** : Storage 100% SSD pour performances maximales
- **Nœud hybride** : Mix SSD (cache) et HDD (capacité) pour optimisation coût/performance
- **Nœud compute-heavy** : Ratio élevé CPU/RAM pour charges de calcul
- **Nœud storage-heavy** : Capacité stockage étendue pour données
- **Edge node** : Format compact pour déploiements edge/branch office

## Caractéristiques Techniques Typiques
- Format rack 1U ou 2U par nœud
- Configuration cluster : minimum 3 nœuds (haute disponibilité)
- Stockage local : 4 à 24 disques SSD/NVMe par nœud (10-100 TB brut)
- RAM : 256 GB à 1+ TB par nœud
- Network : 4 à 8 ports 10/25/100 GbE
- Gestion intégrée via API REST et interface web unifiée
- Consommation : 300W à 800W par nœud

## Localisation Typique
- Datacenter d'entreprise
- Salle serveur régionale
- Site edge/branch office (configurations compactes)
- Installation ROBO (Remote Office/Branch Office)

## Relations avec Autres Équipements
- **Alimente** : Machines virtuelles, containers, services applicatifs distribués
- **Alimenté par** : PDU, UPS
- **Contrôlé par** : Plateforme HCI (management cluster), DCIM, monitoring centralisé
- **Connecté à** : Network switches (data + management), autres nœuds du cluster
- **Refroidi par** : Système de climatisation datacenter, CRAC/CRAH

## Quantité Typique par Bâtiment
- Petit (5 étages) : 3-6 nœuds (cluster minimal)
- Moyen (15 étages) : 6-20 nœuds (infrastructure scale-out)
- Grand (30+ étages) : 20-100+ nœuds (multiple clusters ou large cluster)

## Sources
- Software-Defined Datacenter architecture
- HCI best practices documentation
- Distributed storage systems architecture
- DCIM integration for converged infrastructure
