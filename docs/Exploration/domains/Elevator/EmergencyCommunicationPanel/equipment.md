# Emergency Communication Panel

## Identifiant
- **Code** : EMERG_COM
- **Haystack** : emergency + communication + panel + equip
- **Brick** : brick:Emergency_Communication_Panel (subclass of brick:Safety_Equipment)

## Description
Système de communication d'urgence bidirectionnel intégré à la cabine d'ascenseur, permettant aux passagers bloqués de contacter les services de secours ou le personnel de sécurité. Équipement de sécurité obligatoire.

## Fonction
Permettre aux passagers en situation d'urgence (panne, blocage) de communiquer avec l'extérieur. Transmet automatiquement les informations de localisation. Assure la liaison avec PC sécurité ou services d'urgence.

## Variantes Courantes
- **Interphone simple** : Communication audio bidirectionnelle
- **Système vidéo** : Caméra + audio pour évaluation visuelle
- **Système automatique** : Appel automatique en cas de panne
- **Système GSM** : Backup par réseau mobile
- **Système intégré BMS** : Lien direct avec supervision

## Caractéristiques Techniques Typiques
- Bouton d'appel d'urgence visible et accessible
- Interphone mains-libres
- Haut-parleur et microphone haute sensibilité
- LED d'état de connexion
- Caméra (optionnel)
- Alimentation secours par batterie
- Protocoles : Analogique, VoIP, SIP
- Enregistrement des communications (RGPD)
- Conforme EN 81-28 (alarme et communication)

## Localisation Typique
- Intégré au Car Operating Panel
- Paroi de cabine (panneau dédié)
- À l'intérieur de toutes les cabines

## Relations avec Autres Équipements
- **Alimente** : N/A
- **Alimenté par** : Elevator Controller + Battery Backup
- **Contrôlé par** : N/A (activé par passager)
- **Supervise par** : Elevator Monitoring System, Security Control Center
- **Interagit avec** : Fire Alarm System, Security Phone System, CCTV

## Quantité Typique par Bâtiment
- Petit (5 étages) : 1-2 panneaux (1 par cabine, obligatoire)
- Moyen (15 étages) : 4-8 panneaux (1 par cabine)
- Grand (30+ étages) : 12-32 panneaux (1 par cabine)

## Sources
- EN 81-28:2018 - Remote alarm for passenger entrapment
- ASME A17.1 - Emergency communication requirements
- Haystack Project 4.0 - Safety equipment tagging
- Brick Schema - Emergency and safety equipment classes
