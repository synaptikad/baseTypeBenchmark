# Biometric Reader

## Identifiant
- **Code** : BIO_READER
- **Haystack** : biometric-reader
- **Brick** : brick:Biometric_Reader

## Description
Dispositif de lecture et vérification biométrique pour authentification forte basée sur les caractéristiques physiques uniques des individus. Peut utiliser empreintes digitales, reconnaissance faciale, iris, géométrie de la main, ou veines palmaires. Utilisé seul ou en complément d'un badge pour authentification multi-facteurs.

## Fonction
Capture et analyse des données biométriques, comparaison avec modèles enregistrés, validation d'identité, transmission du résultat d'authentification au contrôleur d'accès. Peut fonctionner en mode 1:1 (vérification) ou 1:N (identification).

## Variantes Courantes
- **Lecteur d'empreintes digitales** : Technologie la plus répandue, optique ou capacitif
- **Reconnaissance faciale** : Caméra 2D ou 3D, avec ou sans liveness detection
- **Lecteur d'iris** : Haute sécurité, précision très élevée
- **Lecteur de veines palmaires** : Non-contact, très sécurisé
- **Lecteur géométrie de la main** : Pour environnements industriels
- **Multi-modal** : Combine plusieurs biométries (visage + empreinte)

## Caractéristiques Techniques Typiques
- Temps de vérification : 0.3-2 secondes
- Taux de faux rejet (FRR) : 0.01-1%
- Taux de fausse acceptation (FAR) : 0.001-0.1%
- Capacité modèles : 1 000 à 100 000 utilisateurs
- Communication : TCP/IP, Wiegand, OSDP, RS-485
- Alimentation : 12-24V DC, PoE
- Stockage local ou déporté des templates
- Chiffrement des données biométriques
- Protection anti-spoofing (liveness detection)
- Écran tactile pour interface utilisateur

## Localisation Typique
- Entrées de zones haute sécurité
- Salles serveurs et datacenters
- Laboratoires sensibles
- Coffres et zones réglementées
- Salles de contrôle
- Zones ATEX ou cleanroom (modèles spéciaux)

## Relations avec Autres Équipements
- **Alimente** : N/A
- **Alimenté par** : Power supply, PoE switch
- **Contrôlé par** : Access Controller, Biometric Server
- **Interagit avec** : Badge Reader (authentification 2 facteurs), Electric Lock, Door Controller
- **Synchronisé avec** : Biometric Enrollment Station

## Quantité Typique par Bâtiment
- Petit (5 étages) : 2-10 lecteurs
- Moyen (15 étages) : 10-30 lecteurs
- Grand (30+ étages) : 30-100 lecteurs

## Sources
- ISO/IEC 19794 - Biometric Data Interchange Formats
- NIST Biometric Standards
- OSDP Biometric Profile
- Brick Schema - Biometric Reader Class
