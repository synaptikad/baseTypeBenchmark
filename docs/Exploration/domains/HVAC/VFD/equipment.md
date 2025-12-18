# VFD - Variable Frequency Drive (Variateur de fréquence)

## Identifiant
- **Code** : VFD / VSD / AFD
- **Haystack** : `vfd-equip`
- **Brick** : `brick:Variable_Frequency_Drive`

## Description
Dispositif électronique de puissance qui contrôle la vitesse d'un moteur électrique en faisant varier la fréquence et la tension d'alimentation. Permet l'adaptation du débit des pompes et ventilateurs aux besoins réels avec économies d'énergie significatives.

## Fonction
Moduler la vitesse de rotation des moteurs de pompes, ventilateurs ou compresseurs pour adapter leur débit ou pression aux besoins instantanés. Réduire la consommation électrique (loi du cube : P ∝ n³ pour les charges centrifuges).

## Variantes Courantes
- **VFD standard** : Applications générales
- **VFD pompes** : Fonctions dédiées (PID, anti-pompage)
- **VFD ventilateurs** : Fonctions spécifiques (rampes douces)
- **VFD HVAC** : Intégration BMS native
- **VFD régénératif** : Récupération d'énergie au freinage
- **VFD multi-moteurs** : Pilotage de plusieurs moteurs

## Caractéristiques Techniques Typiques
- Puissance : 0.75 kW - 500 kW
- Plage de fréquence : 0-120 Hz (typiquement 0-60 Hz)
- Tension : 230V mono, 400V tri
- Rendement : 95-98%
- Protocoles : BACnet, Modbus, Profibus, Ethernet/IP
- Points de supervision : fréquence, courant, puissance, vitesse, alarmes

## Localisation Typique
- Local technique CVC
- Armoire électrique
- À proximité du moteur piloté
- Chaufferie/Sous-station

## Relations avec Autres Équipements
- **Pilote** : Pompes, Ventilateurs AHU, Compresseurs, Tours de refroidissement
- **Alimenté par** : Tableau électrique
- **Contrôlé par** : BMS, Automate, Régulateur PID
- **Interagit avec** : Capteurs de pression, Capteurs de débit, Sondes de température

## Quantité Typique par Bâtiment
- Petit (5 étages) : 5-15 unités
- Moyen (15 étages) : 15-50 unités
- Grand (30+ étages) : 50-200 unités

## Sources
- ASHRAE Handbook - HVAC Applications
- IEC 61800 - Adjustable Speed Electrical Power Drive Systems
- Project Haystack - VFD Equipment
- Brick Schema - Variable_Frequency_Drive Class
- ABB / Danfoss / Siemens - VFD Application Guides
