# Leak Detector

## Identifiant
- **Code** : LEAK-DET
- **Haystack** : `water`, `leak`, `detector`, `sensor`, `equip`
- **Brick** : `brick:Leak_Sensor`

## Description
Capteur intelligent détectant la présence d'eau ou d'humidité anormale dans des zones non prévues à cet effet. Alerte précoce pour prévenir les dégâts des eaux et permet l'intervention rapide ou le déclenchement automatique de vannes de coupure.

## Fonction
Détecter les fuites d'eau ou infiltrations dans les zones sensibles, déclencher des alarmes immédiates vers le système de supervision, permettre la localisation précise des fuites, et activer des procédures d'urgence (coupure d'eau, alertes).

## Variantes Courantes
- **Détecteur ponctuel** : Capteur de présence d'eau au sol
- **Cable détecteur** : Cable sensible sur plusieurs mètres (longueur de gaine)
- **Détecteur acoustique** : Détection par analyse sonore des fuites dans canalisations
- **Détecteur de débit anormal** : Analyse consommation pour détection fuite cachée

## Caractéristiques Techniques Typiques
- Type de détection : Conductivité, capacitif, optique
- Alimentation : Batterie (3-5 ans) ou secteur
- Communication : Sans fil (ZigBee, LoRaWAN, Z-Wave), filaire (contact sec, Modbus)
- Sensibilité : Détection quelques gouttes à quelques mm d'eau
- Alarme : Locale (buzzer) et remontée supervision
- Degré de protection : IP67-68

## Localisation Typique
- Sous réservoirs et ballons
- Gaines techniques verticales
- Faux-plafonds
- Locaux serveurs et techniques sensibles
- Sous machines à laver et équipements hydrauliques
- Parkings et sous-sols

## Relations avec Autres Équipements
- **Alimente** : N/A (capteur)
- **Alimenté par** : N/A
- **Contrôlé par** : Système de supervision, alarme intrusion
- **Associé à** : Motorized Valve (coupure auto), Water Meter (corrélation), système d'alarme

## Quantité Typique par Bâtiment
- Petit (5 étages) : 5-15 détecteurs (zones critiques)
- Moyen (15 étages) : 20-50 détecteurs (multi-zones + locaux techniques)
- Grand (30+ étages) : 50-200 détecteurs (couverture extensive toutes zones à risque)

## Sources
- Haystack Project - Leak detection sensors
- Brick Schema - Leak_Sensor class
- Building insurance and risk management standards
- Smart building IoT sensor protocols
