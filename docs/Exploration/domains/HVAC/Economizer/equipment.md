# Economizer (Économiseur d'énergie)

## Identifiant
- **Code** : ECON
- **Haystack** : `economizer-equip`
- **Brick** : `brick:Economizer`

## Description
Système de contrôle intégré à l'AHU qui maximise l'utilisation de l'air extérieur pour le refroidissement gratuit (free-cooling) lorsque les conditions extérieures sont favorables. Module automatiquement les registres d'air neuf, recyclé et extrait pour optimiser l'énergie.

## Fonction
Réduire la consommation énergétique du refroidissement mécanique en utilisant l'air extérieur frais pour refroidir le bâtiment lorsque sa température et/ou enthalpie sont favorables. Économie significative en intersaison et hiver.

## Variantes Courantes
- **Économiseur à air (airside)** : Modulation registres air neuf/recyclé
- **Économiseur à eau (waterside)** : Refroidissement direct eau via tour de refroidissement
- **Économiseur température sèche** : Décision basée sur température extérieure
- **Économiseur enthalpique** : Décision basée sur enthalpie (température + humidité)
- **Économiseur différentiel** : Compare enthalpie extérieure et de reprise
- **Économiseur intégré** : Combiné avec refroidissement mécanique (partiel/total)

## Caractéristiques Techniques Typiques
- Type contrôle : Température sèche ou enthalpie
- Plage activation : Text < 15-18°C (température) ou Hext < Hreturn (enthalpie)
- Composants : Registres motorisés (air neuf, recyclé, extrait), capteurs (T°, HR)
- Économie énergie : 20-50% sur facture refroidissement annuel
- Protocoles : BACnet, Modbus (via contrôleur AHU)
- Points de supervision : mode économiseur (actif/inactif), positions registres, T° ext/reprise

## Localisation Typique
- Intégré dans AHU (logique de contrôle + registres)
- Systèmes de gestion centralisés (waterside economizer)

## Relations avec Autres Équipements
- **Alimente** : N/A (optimise le fonctionnement AHU)
- **Alimenté par** : N/A (stratégie de contrôle)
- **Contrôlé par** : DDC Controller AHU, BMS
- **Interagit avec** : Dampers (air neuf/recyclé/extrait), Chiller, Capteurs météo

## Quantité Typique par Bâtiment
- Petit (5 étages) : 1-3 économiseurs (sur AHU principaux)
- Moyen (15 étages) : 5-15 économiseurs
- Grand (30+ étages) : 15-50 économiseurs

## Sources
- Haystack Project - Economizer Equipment
- Brick Schema - Economizer Classes
- BACnet Standard - Economizer Control Sequences
- ASHRAE Standard 90.1 - Air Economizers
