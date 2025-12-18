# Groupe Électrogène (Emergency Generator / Genset)

## Identifiant
- **Code** : GE
- **Haystack** : generator, elec-output
- **Brick** : Generator

## Description
Source d'énergie électrique de secours autonome fonctionnant généralement au diesel ou au gaz. Il assure la continuité d'alimentation des circuits critiques en cas de défaillance du réseau principal. Équipé de modules de supervision et de démarrage automatique.

## Fonction
Produire de l'électricité en mode secours lors d'une coupure du réseau principal. Maintient l'alimentation des charges critiques (éclairage de sécurité, ascenseurs pompiers, systèmes de sécurité, serveurs) jusqu'au retour du réseau ou durant une durée déterminée.

## Variantes Courantes
- **Groupe diesel** : Moteur diesel avec alternateur
- **Groupe gaz** : Fonctionnement au gaz naturel ou GPL
- **Groupe bi-énergie** : Diesel/gaz avec commutation automatique
- **Groupe conteneurisé** : Installation extérieure en conteneur insonorisé

## Caractéristiques Techniques Typiques
- Puissance : 50 kVA à 2000 kVA (bâtiments tertiaires)
- Tension de sortie : 230V/400V triphasé 50Hz
- Temps de démarrage : 10-15 secondes
- Autonomie : 6-72 heures selon capacité réservoir
- Communication : Modbus RTU/TCP, CANbus, BACnet
- Supervision : température moteur, pression huile, niveau carburant, heures de fonctionnement
- Démarrage automatique sur défaut réseau

## Localisation Typique
- Extérieur sur dalle technique (groupe conteneurisé)
- Local technique ventilé avec extraction fumées
- Toiture terrasse avec isolation acoustique
- Zone accessible pour maintenance et livraison carburant

## Relations avec Autres Équipements
- **Alimente** : TGBT secours via Automatic Transfer Switch (ATS)
- **Alimenté par** : Réservoir carburant (diesel/gaz)
- **Contrôlé par** : Automate de démarrage, système GTB, ATS
- **Associé à** : Préchauffeur moteur, chargeur batteries, coffret ATS

## Quantité Typique par Bâtiment
- Petit (5 étages) : 0-1
- Moyen (15 étages) : 1
- Grand (30+ étages) : 1-2

## Sources
- Brick Schema (Generator class)
- Haystack v4 (generator, elec tags)
- Standards BACnet pour générateurs
- Normes NF S 61-940 (éclairage de sécurité)
