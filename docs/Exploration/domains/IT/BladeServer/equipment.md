# Blade Server

## Identifiant
- **Code** : BLADE-SRV
- **Haystack** : N/A
- **Brick** : N/A

## Description
Serveur modulaire compact inséré dans un châssis blade partagé. Architecture haute densité permettant de concentrer plusieurs serveurs dans un espace réduit avec infrastructure partagée (alimentation, refroidissement, réseau).

## Fonction
Fournit une solution de calcul ultra-dense pour datacenters nécessitant une optimisation maximale de l'espace et de la consommation énergétique. Chaque blade est un serveur complet partageant les ressources du châssis (power, cooling, management).

## Variantes Courantes
- **Blade compute standard** : Serveur applicatif traditionnel au format blade
- **Blade haute densité** : Format demi-largeur, jusqu'à 16 blades par châssis
- **Blade storage** : Optimisé pour stockage avec nombreux disques
- **Blade GPU/accelerator** : Intègre des accélérateurs pour HPC ou IA
- **Blade networking** : Module switch intégré au châssis

## Caractéristiques Techniques Typiques
- Châssis blade : 6U, 9U ou 10U en hauteur
- Capacité : 8 à 16 blades par châssis
- Alimentation partagée : 4 à 8 PSU redondants par châssis (2500W à 6000W chacun)
- Ventilation centralisée gérée au niveau châssis
- Management module intégré (CMC - Chassis Management Controller)
- Interconnexions réseau et stockage intégrées
- Consommation totale châssis : 5 kW à 30+ kW

## Localisation Typique
- Datacenter haute densité
- Salle serveur d'entreprise
- Installation HPC (High Performance Computing)
- Cloud provider infrastructure

## Relations avec Autres Équipements
- **Alimente** : Services applicatifs, virtualisation à haute densité
- **Alimenté par** : PDU haute capacité, UPS datacenter
- **Contrôlé par** : DCIM, CMC (Chassis Management Controller), monitoring centralisé
- **Connecté à** : Core network switches, SAN/Storage network, management network
- **Refroidi par** : CRAC/CRAH, Hot aisle containment, In-Row Cooling

## Quantité Typique par Bâtiment
- Petit (5 étages) : 0-1 châssis (rare dans petites installations)
- Moyen (15 étages) : 1-5 châssis (40-80 serveurs)
- Grand (30+ étages) : 5-50+ châssis (400-800+ serveurs)

## Sources
- Blade server architecture specifications
- DCIM best practices for blade infrastructure
- CMC management interfaces documentation
- High-density datacenter design guides
