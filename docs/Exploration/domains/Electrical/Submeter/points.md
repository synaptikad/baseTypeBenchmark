# Points BMS - Submeter (Sous-Compteur Électrique)

## Introduction

Les sous-compteurs électriques mesurent la consommation d'énergie électrique d'une zone, d'un locataire, d'un usage spécifique ou d'un étage. Ils sont essentiels pour la refacturation énergétique (tenant billing), l'allocation équitable des coûts et le monitoring détaillé de la consommation. Les modèles certifiés MID (directive européenne 2014/32/UE) sont légalement utilisables pour la facturation commerciale et présentent une précision classe B (±0.5%) ou classe 1 (±1%).

Les sous-compteurs sont généralement plus simples que les compteurs principaux et se concentrent sur les mesures essentielles : énergie active importée (kWh), puissances instantanées, tensions, courants et facteur de puissance. Ils sont montés en armoire électrique sur rail DIN (1 à 4 modules) et communiquent via des protocoles standards.

**Protocoles de communication typiques** :
- **Modbus RTU** (RS485) : Le plus répandu, 9600-19200 bauds, adresses 1-247
- **Modbus TCP/IP** : Pour réseaux Ethernet
- **M-Bus** (EN 13757) : Standard européen de télérelève, efficace en multi-drop
- **BACnet/IP** ou **BACnet MS/TP** : Intégration GTB native
- **Impulsions** : Sortie passive pour comptage simple (1 impulsion = X Wh)

## Points de Mesure

| Nom du Point | Description | Type | Unité | Fréquence | Plage Typique | Haystack Tags | Brick Class | BACnet | Modbus |
|-------------|-------------|------|-------|-----------|---------------|---------------|-------------|---------|---------|
| **Active_Energy_Import** | Énergie active importée cumulée (point principal pour refacturation) | AI / ACC | kWh | 60s | 0-999999 kWh | `sensor`, `elec`, `energy`, `active`, `import`, `ac`, `point` | `Active_Energy_Sensor` | ACC | 30001 |
| **Active_Energy_Export** | Énergie active exportée cumulée (si production locale) | AI / ACC | kWh | 60s | 0-999999 kWh | `sensor`, `elec`, `energy`, `active`, `export`, `ac`, `point` | `Active_Energy_Sensor` | ACC | 30003 |
| **Reactive_Energy_Import** | Énergie réactive importée cumulée (si disponible) | AI / ACC | kVArh | 60s | 0-999999 kVArh | `sensor`, `elec`, `energy`, `reactive`, `import`, `ac`, `point` | `Reactive_Energy_Sensor` | ACC | 30005 |
| **Reactive_Energy_Export** | Énergie réactive exportée cumulée | AI / ACC | kVArh | 60s | 0-999999 kVArh | `sensor`, `elec`, `energy`, `reactive`, `export`, `ac`, `point` | `Reactive_Energy_Sensor` | ACC | 30007 |
| **Active_Power_Total** | Puissance active totale instantanée (3 phases) | AI | kW | 5-15s | 0-1000 kW | `sensor`, `elec`, `power`, `active`, `total`, `ac`, `point` | `Active_Power_Sensor` | AI | 40001 |
| **Active_Power_L1** | Puissance active phase L1 | AI | kW | 5-15s | 0-350 kW | `sensor`, `elec`, `power`, `active`, `phase`, `L1`, `ac`, `point` | `Active_Power_Sensor` | AI | 40003 |
| **Active_Power_L2** | Puissance active phase L2 | AI | kW | 5-15s | 0-350 kW | `sensor`, `elec`, `power`, `active`, `phase`, `L2`, `ac`, `point` | `Active_Power_Sensor` | AI | 40005 |
| **Active_Power_L3** | Puissance active phase L3 | AI | kW | 5-15s | 0-350 kW | `sensor`, `elec`, `power`, `active`, `phase`, `L3`, `ac`, `point` | `Active_Power_Sensor` | AI | 40007 |
| **Reactive_Power_Total** | Puissance réactive totale instantanée | AI | kVAr | 10-30s | -500 - +500 kVAr | `sensor`, `elec`, `power`, `reactive`, `total`, `ac`, `point` | `Reactive_Power_Sensor` | AI | 40009 |
| **Apparent_Power_Total** | Puissance apparente totale instantanée | AI | kVA | 10-30s | 0-1000 kVA | `sensor`, `elec`, `power`, `apparent`, `total`, `ac`, `point` | `Apparent_Power_Sensor` | AI | 40011 |
| **Voltage_L1_N** | Tension phase L1 - neutre | AI | V | 10-30s | 200-250 V | `sensor`, `elec`, `volt`, `phase`, `L1`, `ac`, `point` | `Voltage_Sensor` | AI | 40021 |
| **Voltage_L2_N** | Tension phase L2 - neutre | AI | V | 10-30s | 200-250 V | `sensor`, `elec`, `volt`, `phase`, `L2`, `ac`, `point` | `Voltage_Sensor` | AI | 40023 |
| **Voltage_L3_N** | Tension phase L3 - neutre | AI | V | 10-30s | 200-250 V | `sensor`, `elec`, `volt`, `phase`, `L3`, `ac`, `point` | `Voltage_Sensor` | AI | 40025 |
| **Voltage_L1_L2** | Tension phase-phase L1-L2 | AI | V | 10-30s | 380-420 V | `sensor`, `elec`, `volt`, `phase`, `L1`, `L2`, `ac`, `point` | `Voltage_Sensor` | AI | 40027 |
| **Voltage_L2_L3** | Tension phase-phase L2-L3 | AI | V | 10-30s | 380-420 V | `sensor`, `elec`, `volt`, `phase`, `L2`, `L3`, `ac`, `point` | `Voltage_Sensor` | AI | 40029 |
| **Voltage_L3_L1** | Tension phase-phase L3-L1 | AI | V | 10-30s | 380-420 V | `sensor`, `elec`, `volt`, `phase`, `L3`, `L1`, `ac`, `point` | `Voltage_Sensor` | AI | 40031 |
| **Current_L1** | Courant phase L1 | AI | A | 5-15s | 0-100 A | `sensor`, `elec`, `current`, `phase`, `L1`, `ac`, `point` | `Current_Sensor` | AI | 40041 |
| **Current_L2** | Courant phase L2 | AI | A | 5-15s | 0-100 A | `sensor`, `elec`, `current`, `phase`, `L2`, `ac`, `point` | `Current_Sensor` | AI | 40043 |
| **Current_L3** | Courant phase L3 | AI | A | 5-15s | 0-100 A | `sensor`, `elec`, `current`, `phase`, `L3`, `ac`, `point` | `Current_Sensor` | AI | 40045 |
| **Current_Neutral** | Courant neutre | AI | A | 10-30s | 0-50 A | `sensor`, `elec`, `current`, `neutral`, `ac`, `point` | `Current_Sensor` | AI | 40047 |
| **Power_Factor_Total** | Facteur de puissance total (cos φ) | AI | - | 10-30s | -1.0 - +1.0 | `sensor`, `elec`, `pf`, `total`, `ac`, `point` | `Power_Factor_Sensor` | AI | 40051 |
| **Power_Factor_L1** | Facteur de puissance phase L1 | AI | - | 10-30s | -1.0 - +1.0 | `sensor`, `elec`, `pf`, `phase`, `L1`, `ac`, `point` | `Power_Factor_Sensor` | AI | 40053 |
| **Power_Factor_L2** | Facteur de puissance phase L2 | AI | - | 10-30s | -1.0 - +1.0 | `sensor`, `elec`, `pf`, `phase`, `L2`, `ac`, `point` | `Power_Factor_Sensor` | AI | 40055 |
| **Power_Factor_L3** | Facteur de puissance phase L3 | AI | - | 10-30s | -1.0 - +1.0 | `sensor`, `elec`, `pf`, `phase`, `L3`, `ac`, `point` | `Power_Factor_Sensor` | AI | 40057 |
| **Frequency** | Fréquence réseau | AI | Hz | 30-60s | 49.5-50.5 Hz | `sensor`, `elec`, `freq`, `ac`, `point` | `Frequency_Sensor` | AI | 40061 |
| **Demand_Peak_Current** | Demande maximale sur fenêtre glissante (15min typique) | AI | kW | 60s | 0-1000 kW | `sensor`, `elec`, `demand`, `peak`, `power`, `active`, `ac`, `point` | `Peak_Power_Demand_Sensor` | AI | 40071 |
| **Demand_Peak_Timestamp** | Horodatage de la demande maximale | AI | timestamp | On change | - | `sensor`, `elec`, `demand`, `peak`, `datetime`, `point` | `Sensor` | AI | 40073 |
| **THD_Voltage_L1** | Taux de distorsion harmonique tension L1 (si disponible) | AI | % | 60s | 0-20 % | `sensor`, `elec`, `volt`, `thd`, `phase`, `L1`, `ac`, `point` | `Voltage_Sensor` | AI | 40081 |
| **THD_Current_L1** | Taux de distorsion harmonique courant L1 (si disponible) | AI | % | 60s | 0-50 % | `sensor`, `elec`, `current`, `thd`, `phase`, `L1`, `ac`, `point` | `Current_Sensor` | AI | 40083 |

**Notes** :
- **Active_Energy_Import** est le point critique pour la refacturation aux locataires
- Énergies cumulées : Type BACnet **ACC** (Accumulator), lecture lente (60s) car valeur cumulative
- Puissances instantanées : Type BACnet **AI**, lecture rapide (5-15s) pour monitoring temps réel
- Les adresses Modbus indiquées sont des exemples typiques ; se référer au manuel du fabricant pour la cartographie exacte
- Pour compteurs monophasés : uniquement L1 et neutre
- THD (Total Harmonic Distortion) disponible sur modèles avancés uniquement

## Points de Commande

| Nom du Point | Description | Type | Valeurs | Haystack Tags | Brick Class | BACnet | Modbus |
|-------------|-------------|------|---------|---------------|-------------|---------|---------|
| **Reset_Demand_Peak** | Réinitialisation demande maximale (si autorisé par l'équipement) | BO | 0=Inactif, 1=Reset | `cmd`, `elec`, `demand`, `reset`, `point` | `Command` | BO | Coil 1 |
| **Sync_Clock** | Synchronisation horloge interne (pour tarifs horaires) | BO | 0=Inactif, 1=Sync | `cmd`, `datetime`, `sync`, `point` | `Command` | BO | Coil 3 |

**IMPORTANT - Restrictions compteurs MID** :
- Les compteurs certifiés **MID** (directive européenne 2014/32/UE) utilisés pour la facturation commerciale sont **scellés légalement**
- La réinitialisation de l'énergie active importée est **strictement interdite** et techniquement bloquée
- Seule la réinitialisation de la demande maximale peut être autorisée (selon modèle)
- Les compteurs non-MID (monitoring uniquement) peuvent offrir des commandes de reset étendu, mais ne sont **pas utilisables légalement pour la refacturation**

**Notes** :
- Très peu de commandes disponibles sur les sous-compteurs (équipement passif de mesure)
- Certains modèles n'offrent aucune commande en écriture (lecture seule)
- La synchronisation d'horloge permet l'application de tarifs heures pleines/heures creuses

## Points d'État

| Nom du Point | Description | Type | Valeurs | Fréquence | Haystack Tags | Brick Class | BACnet | Modbus |
|-------------|-------------|------|---------|-----------|---------------|-------------|---------|---------|
| **Communication_Status** | État communication Modbus/M-Bus | BI | 0=Défaut, 1=OK | 10-30s | `sensor`, `comm`, `status`, `point` | `Status` | BI | DI 1 |
| **Phase_Loss_L1** | Perte phase L1 détectée | BI | 0=OK, 1=Perte | 10s | `sensor`, `elec`, `fault`, `phase`, `L1`, `point` | `Fault_Status` | BI | DI 3 |
| **Phase_Loss_L2** | Perte phase L2 détectée | BI | 0=OK, 1=Perte | 10s | `sensor`, `elec`, `fault`, `phase`, `L2`, `point` | `Fault_Status` | BI | DI 4 |
| **Phase_Loss_L3** | Perte phase L3 détectée | BI | 0=OK, 1=Perte | 10s | `sensor`, `elec`, `fault`, `phase`, `L3`, `point` | `Fault_Status` | BI | DI 5 |
| **Overload_Alarm** | Alarme surcharge détectée (courant > seuil) | BI | 0=OK, 1=Surcharge | 10s | `sensor`, `elec`, `alarm`, `overload`, `point` | `Alarm` | BI | DI 7 |
| **Energy_Direction** | Sens du flux énergétique | MSV | 0=Import, 1=Export | 10-30s | `sensor`, `elec`, `energy`, `direction`, `point` | `Status` | MSV | DI 9 |
| **Tamper_Alarm** | Alarme ouverture boîtier (détection fraude) | BI | 0=OK, 1=Ouvert | 10s | `sensor`, `security`, `tamper`, `alarm`, `point` | `Alarm` | BI | DI 11 |
| **MID_Certification_Valid** | Certification MID valide (scellement intact) | BI | 0=Invalide, 1=Valide | 300s | `sensor`, `certification`, `mid`, `status`, `point` | `Status` | BI | DI 13 |
| **Pulse_Output_Active** | État sortie impulsion active | BI | 0=Inactif, 1=Actif | 5s | `sensor`, `pulse`, `output`, `status`, `point` | `Status` | BI | DI 15 |
| **Meter_Error** | Erreur interne compteur | BI | 0=OK, 1=Erreur | 10-30s | `sensor`, `fault`, `meter`, `point` | `Fault_Status` | BI | DI 17 |
| **Voltage_Unbalance_Alarm** | Alarme déséquilibre tensions phases | BI | 0=OK, 1=Déséquilibre | 30s | `sensor`, `elec`, `volt`, `alarm`, `unbalance`, `point` | `Alarm` | BI | DI 19 |
| **Current_Unbalance_Alarm** | Alarme déséquilibre courants phases | BI | 0=OK, 1=Déséquilibre | 30s | `sensor`, `elec`, `current`, `alarm`, `unbalance`, `point` | `Alarm` | BI | DI 21 |
| **Reverse_Phase_Sequence** | Alarme inversion séquence phases (L1-L2-L3 inversé) | BI | 0=OK, 1=Inversé | 60s | `sensor`, `elec`, `alarm`, `phase`, `sequence`, `point` | `Alarm` | BI | DI 23 |

**Notes** :
- Les états de phase (perte, déséquilibre) sont critiques pour maintenance préventive
- L'alarme tamper est essentielle pour les installations exposées à la fraude
- Le statut MID garantit la validité légale des mesures pour facturation
- La direction d'énergie distingue import (consommation) et export (production locale, panneaux solaires)
- Fréquence de polling adaptée à la criticité : alarmes phase 10s, états généraux 30s

## Points de Configuration

| Nom du Point | Description | Type | Valeurs | Accès | Haystack Tags | Brick Class | BACnet | Modbus |
|-------------|-------------|------|---------|-------|---------------|-------------|---------|---------|
| **CT_Primary_Rating** | Rapport TC primaire (si TCs utilisés) | AO | 50-5000 A | R/W | `config`, `elec`, `current`, `ct`, `primary`, `point` | `Parameter` | AO | HR 1001 |
| **CT_Secondary_Rating** | Rapport TC secondaire (typiquement 5A ou 1A) | AO | 1-5 A | R/W | `config`, `elec`, `current`, `ct`, `secondary`, `point` | `Parameter` | AO | HR 1003 |
| **Demand_Interval** | Fenêtre de calcul demande (typiquement 15min) | AO | 1-60 min | R/W | `config`, `elec`, `demand`, `interval`, `point` | `Parameter` | AO | HR 1005 |
| **Pulse_Constant** | Constante impulsion sortie (Wh/impulsion) | AO | 1-10000 Wh/imp | R/W | `config`, `pulse`, `constant`, `point` | `Parameter` | AO | HR 1007 |
| **Modbus_Address** | Adresse Modbus RTU (1-247) | AO | 1-247 | R/W | `config`, `comm`, `modbus`, `address`, `point` | `Parameter` | AO | HR 1009 |
| **Modbus_Baudrate** | Vitesse Modbus RTU | MSV | 9600/19200/38400 bps | R/W | `config`, `comm`, `modbus`, `baudrate`, `point` | `Parameter` | MSV | HR 1011 |
| **Display_Backlight_Timeout** | Délai extinction rétro-éclairage LCD | AO | 0-300 s | R/W | `config`, `display`, `backlight`, `timeout`, `point` | `Parameter` | AO | HR 1013 |
| **Overload_Threshold** | Seuil alarme surcharge (% nominal) | AO | 80-120 % | R/W | `config`, `elec`, `alarm`, `overload`, `threshold`, `point` | `Parameter` | AO | HR 1015 |
| **Voltage_Unbalance_Threshold** | Seuil alarme déséquilibre tensions (%) | AO | 1-10 % | R/W | `config`, `elec`, `volt`, `alarm`, `unbalance`, `threshold`, `point` | `Parameter` | AO | HR 1017 |

**Notes** :
- Les paramètres de configuration sont généralement protégés par mot de passe
- **CT_Primary_Rating** et **CT_Secondary_Rating** critiques pour précision si TCs externes utilisés (sinon mesure directe)
- **Demand_Interval** : 15 minutes est la norme internationale pour facturation électrique (normes ANSI/IEC)
- **Pulse_Constant** : Permet interfaçage avec systèmes legacy comptage impulsions
- Accès en écriture à limiter aux techniciens qualifiés (risque déréglage précision)
- Après modification paramètres, vérifier conformité certification MID si applicable

## Notes d'Implémentation

### Protocoles de Communication

#### Modbus RTU (RS485)
- **Usage** : Protocole le plus répandu pour sous-compteurs
- **Topologie** : Bus RS485 multi-drop, jusqu'à 32 équipements sans répéteur (250 avec)
- **Adressage** : Adresses 1-247, chaque compteur doit avoir une adresse unique
- **Vitesse** : 9600 bps (standard), 19200 bps (rapide), parfois 38400 bps
- **Distance** : Jusqu'à 1200m (qualité câble et vitesse dépendants)
- **Câblage** : Paire torsadée blindée, terminaisons 120Ω aux extrémités

#### Modbus TCP/IP
- **Usage** : Pour réseaux IP, compteurs avec interface Ethernet intégrée
- **Port** : TCP 502 (standard Modbus TCP)
- **Avantages** : Intégration simplifiée réseaux IT, diagnostics réseau standards
- **Topologie** : Ethernet commutée (switch), protocole TCP garantit fiabilité

#### M-Bus (EN 13757)
- **Usage** : Standard européen de télérelève, très efficace pour sous-comptage
- **Topologie** : Bus série 2 fils, jusqu'à 250 esclaves par maître
- **Vitesse** : 2400 bps (standard), 9600 bps ou 38400 bps (extended)
- **Avantages** :
  - Combine alimentation et communication sur 2 fils
  - Polarité indépendante (simplification installation)
  - Transmet la valeur réelle lue (pas de multiplication), évite erreurs
  - Format standardisé facilite interopérabilité multi-fabricants
- **Applications** : Idéal bâtiments multi-locataires, lecture automatique compteurs

#### BACnet/IP et BACnet MS/TP
- **Usage** : Intégration native dans systèmes GTB (Building Automation)
- **BACnet/IP** : Sur réseau Ethernet (UDP port 47808)
- **BACnet MS/TP** : Sur bus RS485 multi-drop (similaire Modbus RTU)
- **Avantages** : Mapping direct vers objets BACnet standards (AI, ACC, BI)
- **Certification** : Vérifier certification BTL (BACnet Testing Laboratories) pour interopérabilité

#### Impulsions (Pulse Output)
- **Usage** : Sortie passive simple pour comptage legacy
- **Principe** : 1 impulsion = X Wh (constante configurable, ex: 1000 Wh/imp)
- **Interface** : Contact sec (relais) ou transistor NPN/PNP
- **Limitation** : Pas de retour d'information détaillée (uniquement énergie cumulée)
- **Applications** : Interfaçage avec anciens systèmes ou totalisateurs autonomes

### Fréquences de Polling Recommandées

| Type de Point | Fréquence | Justification |
|--------------|-----------|---------------|
| Énergies cumulées (kWh, kVArh) | 60s | Valeurs cumulatives, variation lente, charge réseau réduite |
| Puissances instantanées (kW, kVAr, kVA) | 5-15s | Monitoring temps réel, détection pics consommation |
| Tensions et courants | 10-30s | Surveillance qualité réseau, pas critique en temps réel |
| Facteur de puissance | 10-30s | Optimisation PF, variation modérée |
| Demande maximale (peak demand) | 60s | Calculé sur fenêtre 15min, pas besoin polling rapide |
| États et alarmes phase | 10s | Critique maintenance, détection rapide défaut |
| États généraux | 30s | Surveillance standard |
| Configuration | On change | Lecture à la demande uniquement |

**Optimisation charge réseau** :
- Grouper lectures Modbus en transactions multi-registres (réduire overhead)
- Pour M-Bus : lecture cyclique tous les compteurs (protocole optimisé pour ça)
- Éviter polling synchrone de tous compteurs (étaler requêtes dans temps)

### Facturation et Conformité Réglementaire

#### Directive MID 2014/32/UE (Measuring Instruments Directive)
- **Champ d'application** : Compteurs utilisés pour **transactions commerciales** (refacturation locataires)
- **Marquage** : CE + M + année fabrication (ex: M23 pour 2023) + code organisme notifié (4 chiffres)
- **Classes de précision** :
  - **Classe A** : IEC 62053-21 Classe 2 (±2%) - usage résidentiel léger
  - **Classe B** : IEC 62053-21 Classe 1 (±1%) - standard commercial
  - **Classe C** : IEC 62053-21 Classe 0.5 (±0.5%) - haute précision industrielle
- **Scellement légal** :
  - Compteurs MID sont scellés par fabricant/organisme notifié
  - Toute ouverture boîtier invalide certification
  - Reset énergie active **strictement interdit** et bloqué techniquement
- **Modules d'évaluation conformité** : B+F (type + vérification), B+D (type + assurance qualité), H1 (conformité totale)
- **Standards applicables** : EN 50470-1 (exigences générales), EN 50470-3 (essais)

#### Compteurs Non-MID
- **Usage** : Monitoring énergétique, allocation interne coûts (non-commercial)
- **Avantages** : Moins chers, fonctionnalités étendues (reset, logs détaillés)
- **Limitation légale** : **Ne peuvent pas être utilisés pour facturation commerciale externe**

#### Implications pour Intégration BMS
- **Compteurs MID** :
  - Lecture seule énergie active importée (point critique)
  - Traçabilité horodatage lectures (preuves légales)
  - Sauvegarde régulière index vers plateforme refacturation sécurisée
- **Vérification périodique** : Vérifier état tamper alarm et MID certification status
- **Documentation** : Conserver certificats MID et registres lectures pour audits

### Intégration Refacturation Locataires

#### Architecture Typique
1. **Sous-compteurs MID** par locataire/zone → mesures kWh
2. **Système BMS/EMS** → collecte données via Modbus/M-Bus/BACnet
3. **Plateforme de refacturation** (Tenant Billing Software) → génération factures

#### Points Clés Intégration
- **Lecture index périodique** : Mensuelle (facturation) + quotidienne (monitoring)
- **Horodatage précis** : Synchronisation NTP des systèmes BMS critiques
- **Mapping locataires** : Association ID compteur ↔ locataire/zone dans base données
- **Tarification** :
  - Tarif unique (€/kWh fixe)
  - Tarifs heures pleines/creuses (nécessite horloge compteur synchronisée)
  - Tarifs saisonniers
  - Peak demand charges (pénalités dépassement puissance souscrite)
- **Export données** : CSV, XML, API REST vers logiciel facturation
- **Alertes consommation** : Seuils dépassement pour anticipation factures

#### Économies d'Énergie Démontrées
- **Réduction 15-45%** consommation globale bâtiment (sources multiples)
- **Responsabilisation locataires** : Paiement usage réel incite sobriété
- **Détection fuites/gaspillages** : Analyse granulaire par zone révèle anomalies

#### Réglementations Locales
- **France** : Décret tertiaire impose monitoring détaillé (sous-comptage recommandé)
- **UK** : Submetering obligatoire pour nouveaux bâtiments multi-locataires
- **Allemagne** : Heizkostenverordnung impose comptage individuel chauffage/ECS (électricité recommandé)

### Configuration Transformateurs de Courant (TC)

Pour compteurs avec mesure indirecte via TCs :
- **TC Standards** : 50/5A, 100/5A, 250/5A, 500/5A, 1000/5A, 2000/5A
- **Configuration compteur** : Saisir ratio TC exact (ex: 100/5 = 20)
- **Impact précision** : TC classe 0.5 minimum pour sous-comptage MID
- **Installation** :
  - TC sur chaque phase (3 TC pour triphasé)
  - Sens passage courant (P1→P2) respecté
  - Secondaire TC **jamais ouvert** sous tension (risque surtension mortelle)
  - Câblage secondaire court (<3m), section adéquate (2.5mm²)

### Dépannage Problèmes Courants

| Symptôme | Cause Probable | Solution |
|----------|----------------|----------|
| Pas de communication Modbus | Mauvais câblage RS485, polarité inversée, absence terminaisons | Vérifier A/B, ajouter terminaisons 120Ω, tester continuité |
| Valeurs énergie aberrantes | Mauvaise config ratio TC, inversion phases | Vérifier paramètre CT ratio, vérifier séquence phases L1-L2-L3 |
| Courants mesurés = 0 | TC mal positionné ou secondaire ouvert | Vérifier serrage TC sur conducteur, continuité câblage secondaire |
| Alarme phase loss intempestive | Déséquilibre charge monophasé sur réseau triphasé | Normal si charge réellement monophasée, ajuster seuils alarme |
| Compteur ne répond plus (Modbus timeout) | Conflit adresse Modbus, équipement HS | Vérifier unicité adresses, tester compteur isolé, redémarrer |
| Facteur puissance négatif | Charge capacitive ou inversion TC | Vérifier sens TC (P1→P2), normal si compensation PF installée |

## Sources

1. https://project-haystack.org/doc/docHaystack/Meters - Project Haystack official meters documentation
2. https://project-haystack.org/doc/lib-phIoT/elec-meter - Haystack elec-meter tag definition
3. https://docs.brickschema.org/modeling/meters.html - Brick Schema meters modeling guide
4. https://brickschema.org/ontology/1.1/classes/Electrical_Meter/ - Brick Electrical_Meter class
5. https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32014L0032 - MID Directive 2014/32/EU official text
6. https://m-bus.com/ - M-Bus official protocol specification and resources
7. https://www.accuenergy.com/application-solutions/tenant-submetering/ - Tenant submetering applications and benefits
8. https://www.gavazziautomation.com/fileadmin/images/PIM/OTHERSTUFF/COMPRO/EM330_EM340_ET330_ET340_CP.pdf - Carlo Gavazzi EM340 communication protocol
9. https://library.e.abb.com/public/ad27e8ef78054f40b1c6156711faa796/2CSG445010D0201%20-%20M2M%20Basic_EN.pdf - ABB M2M meter installation manual
10. https://www.socomec.us/en-us/news/tenant-submetering-how-automatically-read-meters-and-generate-bills - Socomec tenant submetering guide
11. https://www.wattsense.com/blog/communication-protocols/modbus/ - Modbus protocol for building management
12. https://learnmetering.com/pages/demand-meters/ - Demand metering fundamentals and calculation
13. https://www.eastrongroup.com/news/company-news/midcertification-standards-unpacked-a-deep-dive-into-en504701-3-vs-en504703-2022-and-their-impact-on-smart-metering.html - MID certification standards explained
14. https://www.setra.com/energy-management/tenant-submetering - Setra tenant submetering power meters
15. https://www.productinfo.schneider-electric.com/nadigest/5c51d645347bdf0001f1f280/Master/17704_MAIN%20(bookmap)_0000041932.xml/$/PowerandEnergyMeters-iEM3000CPT_0000085046 - Schneider iEM3000 series technical documentation
