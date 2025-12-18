# Load Balancer

## Identifiant
- **Code** : NET-LB
- **Haystack** : N/A
- **Brick** : N/A

## Description
Équipement réseau distribuant intelligemment le trafic applicatif entre plusieurs serveurs backend pour optimiser la disponibilité, performance et scalabilité. Opère aux niveaux Layer 4 (TCP/UDP) et Layer 7 (HTTP/HTTPS).

## Fonction
Répartit les requêtes entrantes sur un pool de serveurs selon des algorithmes (round-robin, least connections, weighted) et des health checks. Assure la haute disponibilité des applications, l'affinité de session et le SSL offloading. Supervisable via SNMP, API REST et collecte de métriques détaillées.

## Variantes Courantes
- **Hardware Load Balancer (ADC)** : Appliance physique dédiée haute performance
- **Software Load Balancer** : Solution virtualisée ou conteneurisée
- **Global Server Load Balancer (GSLB)** : Répartition entre datacenters géographiques
- **Application Delivery Controller (ADC)** : Load balancer avancé avec optimisation applicative
- **Reverse Proxy Load Balancer** : Combinaison proxy inverse + load balancing

## Caractéristiques Techniques Typiques
- Formats : 1U à 2U (hardware), virtuel (software)
- Débit : 1 Gbps à 100+ Gbps
- Connexions simultanées : 1M à 100M+ sessions
- Layer 4 (transport) et Layer 7 (application) load balancing
- SSL/TLS termination et offloading
- Health monitoring actif des backends
- Management : Web GUI, CLI, REST API, SNMP
- Consommation : 150W à 800W (hardware)

## Localisation Typique
- Datacenter (devant fermes de serveurs web/applicatifs)
- DMZ pour applications publiques
- Salle réseau principale
- Zones de services critiques

## Relations avec Autres Équipements
- **Alimente** : Distribution de charge applicative, haute disponibilité services
- **Alimenté par** : PDU, UPS critique
- **Contrôlé par** : Monitoring APM (Application Performance Monitoring), NMS, orchestration
- **Connecté à** : Core switches, serveurs applicatifs/web, firewalls (upstream)
- **Refroidi par** : Climatisation datacenter

## Quantité Typique par Bâtiment
- Petit (5 étages) : 0-2 load balancers (petite infrastructure web)
- Moyen (15 étages) : 2-6 load balancers (redondance, multiple applications)
- Grand (30+ étages) : 6-20+ load balancers (multi-sites, nombreuses applications)

## Sources
- Application Delivery Controller architecture
- Layer 4 vs Layer 7 load balancing
- Health check mechanisms documentation
- SNMP monitoring for load balancers
