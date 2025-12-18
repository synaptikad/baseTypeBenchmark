# Onduleur (UPS - Uninterruptible Power Supply)

## Identifiant
- **Code** : UPS
- **Haystack** : ups, elec-output
- **Brick** : UPS

## Description
Système d'alimentation électrique de secours sans interruption utilisant des batteries pour fournir une continuité électrique immédiate (0ms) lors de micro-coupures ou défaillances réseau. Assure également le conditionnement et la protection de l'énergie électrique (filtrage, régulation).

## Fonction
Garantir une alimentation électrique stable et continue pour les équipements sensibles (serveurs, équipements médicaux, systèmes de sécurité). Protège contre les coupures, surtensions, sous-tensions, harmoniques et perturbations du réseau.

## Variantes Courantes
- **UPS Off-line (VFD)** : Basculement sur batterie lors de coupure
- **UPS Line-interactive** : Régulation tension + batterie
- **UPS On-line (VFI)** : Double conversion permanente (haute qualité)
- **UPS modulaire** : Architecture N+1 redondante avec modules hot-swap
- **UPS rotatif** : Volant d'inertie + générateur (datacenters)

## Caractéristiques Techniques Typiques
- Puissance : 1 kVA à 1000 kVA
- Autonomie : 5-30 minutes (batteries standard)
- Rendement : 92-98% (mode on-line)
- Tension d'entrée/sortie : 230V/400V
- Communication : SNMP, Modbus TCP, BACnet IP, USB
- Supervision : charge batterie, autonomie restante, état bypass, température
- Bypass maintenance intégré

## Localisation Typique
- Salle serveurs / datacenter
- Local technique informatique
- Armoires télécoms
- Locaux techniques critiques (sécurité incendie)
- Salles de contrôle GTB/GTC

## Relations avec Autres Équipements
- **Alimente** : Serveurs, équipements réseau, systèmes de sécurité, automates
- **Alimenté par** : TGBT ou tableau divisionnaire
- **Contrôlé par** : Système de monitoring DCIM, GTB, SNMP manager
- **Associé à** : Armoires batteries externes, PDU, climatisation salle serveurs

## Quantité Typique par Bâtiment
- Petit (5 étages) : 1-2
- Moyen (15 étages) : 2-5
- Grand (30+ étages) : 5-15

## Sources
- Brick Schema (UPS class)
- Haystack v4 (ups, elec tags)
- Standards BACnet pour UPS
- RFC 1628 (UPS MIB SNMP)
