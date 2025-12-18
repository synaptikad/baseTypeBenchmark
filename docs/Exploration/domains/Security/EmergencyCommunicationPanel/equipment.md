# Emergency Communication Panel

## Identifiant
- **Code** : EMERGENCY_COMM
- **Haystack** : emergency-comm-panel
- **Brick** : brick:Emergency_Communication_Panel

## Description
Système de communication dédié aux situations d'urgence, installé dans ascenseurs, cages d'escaliers, parkings, zones isolées. Permet communication directe avec centre de sécurité ou services d'urgence. Souvent réglementaire dans certaines zones (ascenseurs, issues de secours). Peut inclure bouton d'appel, interphone, et signalisation visuelle.

## Fonction
Communication d'urgence bidirectionnelle, appel automatique vers centre de sécurité ou pompiers, signalisation visuelle d'état, enregistrement des communications, tests périodiques automatiques, alimentation secourue, conformité réglementaire.

## Variantes Courantes
- **Panel ascenseur** : Conforme EN 81-28, ligne téléphonique dédiée ou IP
- **Panel escalier de secours** : Communication pompiers
- **Panel parking** : Bornes d'appel d'urgence
- **Panel zone isolée** : Communication site isolé
- **Panel avec vidéo** : Caméra pour identification visuelle
- **Panel IP** : Communication VoIP/SIP

## Caractéristiques Techniques Typiques
- Audio : Mains-libres, full-duplex, haute intelligibilité
- Bouton d'appel : Résistant vandalisme, éclairé
- Signalisation : LED état (veille, appel, communication)
- Alimentation : Primaire + batterie backup 24-72h
- Communication : Ligne téléphonique, IP (SIP), GSM backup
- Test automatique : Périodique avec rapport
- Enregistrement : Logging des appels
- Protection : IP65, IK10
- Normes : EN 81-28 (ascenseurs), EN 81-70
- Matériau : Acier inox, polycarbonate
- Températures : -20°C à +70°C

## Localisation Typique
- Cabines d'ascenseurs (obligatoire)
- Cages d'escaliers de secours
- Parkings souterrains
- Zones isolées ou dangereuses
- Quais de chargement
- Toitures-terrasses accessibles
- Locaux techniques isolés
- Tunnels et galeries

## Relations avec Autres Équipements
- **Alimente** : N/A
- **Alimenté par** : Battery backup, UPS, PoE
- **Contrôlé par** : Emergency Management System, Security Center
- **Envoie vers** : Security Desk, Fire Brigade, Emergency Services, Elevator Monitoring
- **Interagit avec** : Fire Alarm System, Elevator Controller, CCTV (vérification)
- **Supervise** : Elevator Phone Monitoring Service

## Quantité Typique par Bâtiment
- Petit (5 étages) : 3-8 panels (ascenseurs + escaliers)
- Moyen (15 étages) : 10-25 panels
- Grand (30+ étages) : 30-80 panels

## Sources
- EN 81-28 - Alarm Devices and Rules for Trapped Passengers
- EN 81-70 - Accessibility Requirements for Elevators
- Emergency Communication Systems Standards
- Brick Schema - Emergency Communication Equipment
