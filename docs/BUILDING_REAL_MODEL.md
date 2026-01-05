# Modèle Réel d'un Bâtiment Tertiaire

> Document de référence basé sur la réalité terrain pour aligner générateur et queries

---

## 1. ELECTRICAL (Distribution Électrique)

### Hiérarchie physique

```
[Arrivée HTA]
    |
[Transformateur HTA/BT] ──── Location: Local technique sous-sol (basement)
    |
[TGBT] ──────────────────── Location: Local technique sous-sol
    |
    ├── [TD Étage 1] ────── Location: Gaine technique Floor 1
    │       ├── Circuit Éclairage
    │       ├── Circuit Prises
    │       └── Circuit CVC (FCU, VAV)
    │
    ├── [TD Étage 2] ────── Location: Gaine technique Floor 2
    │       └── ...
    │
    ├── [TD Parking] ────── Location: Parking
    │       ├── Éclairage parking
    │       └── Bornes EV
    │
    ├── [UPS] ────────────── Location: Local IT / Datacenter
    │       └── Alim secourue IT
    │
    └── [Groupe Électrogène] ── Location: Local technique (backup)
```

### Relations

| Relation | Source | Destination | Exemple |
|----------|--------|-------------|---------|
| **FEEDS** | TGBT | TD_Étage | TGBT alimente TD |
| **FEEDS** | TD | Equipment | TD alimente FCU, Luminaires |
| **FEEDS** | UPS | IT Equipment | UPS alimente Serveurs |
| **LOCATED_IN** | TGBT | Space (local tech) | TGBT dans local technique |
| **LOCATED_IN** | TD | Space (gaine) | TD dans gaine technique étage |

### Points de mesure (Comptage)

| Équipement | Points | Grandeur (quantity) |
|------------|--------|---------------------|
| TGBT | active_energy, active_power, voltage, current, power_factor | energy, power, voltage, current |
| TD | active_energy, active_power | energy, power |
| UPS | input_power, output_power, battery_level, autonomy | power, percentage, duration |

### Logique FEEDS pour les queries

**Q1 (Chaîne énergétique)** : Partir d'un compteur (TGBT ou TD) et suivre FEEDS vers l'aval
```
TGBT -[FEEDS]-> TD_Étage1 -[FEEDS]-> FCU_Bureau101
```

**Q8/Q9 (Énergie tenant)** : Modèle 3 axes avec compteurs dédiés par tenant
```
Tenant <-[METERS_TENANT]- SubMeter_Tenant -[HAS_POINT]-> Point(energy)
```
✅ **Résolu** : Le générateur crée des SubMeter_Tenant avec relation METERS_TENANT directe (2 hops)

---

## 2. HVAC (Chauffage, Ventilation, Climatisation)

### Hiérarchie physique - Grand bâtiment

```
[Production Centralisée] ──── Location: Rooftop ou Sous-sol technique
    │
    ├── [Chiller] ────────── Produit eau glacée (6-12°C)
    │       └── Points: supply_temp, return_temp, power, COP
    │
    ├── [Boiler] ─────────── Produit eau chaude (40-80°C)
    │       └── Points: supply_temp, return_temp, gas_consumption
    │
    └── [Cooling Tower] ──── Rejette chaleur
            └── Points: fan_speed, water_temp

[Distribution Primaire]
    │
    ├── [Primary Pump] ───── Circulation eau glacée/chaude
    │
    └── [Heat Exchanger] ─── Échange entre circuits

[CTA / AHU] ─────────────── Location: Rooftop ou Local technique étage
    │                       Air neuf + traitement (chauffage/refroidissement)
    │                       Points: supply_air_temp, return_air_temp,
    │                               outdoor_air_temp, filter_dp, fan_speed
    │
    ├── [VAV Box] ────────── Location: Faux plafond, 1 par zone
    │       │                Points: airflow, damper_position
    │       │
    │       └── SERVES ───── Zone (plusieurs Spaces)
    │
    └── [FCU] ─────────────── Location: Dans le Space (plafond/mural)
            │                 Points: supply_air_temp, fan_speed, valve_position
            │
            └── SERVES ───── Space (1 ou plusieurs)

[Terminal] ───────────────── Location: Dans le Space
    │
    ├── [Thermostat] ─────── Points: zone_temp, setpoint_temp, mode
    │       └── CONTROLS ─── FCU ou VAV
    │
    └── [Diffuseur] ──────── Bouche de soufflage (passif, pas de points)
```

### Hiérarchie physique - Petit bâtiment

```
[Rooftop Unit / Split] ──── Location: Toiture ou Local
    │                       Tout-en-un : production + distribution
    │
    └── SERVES ──────────── Plusieurs Spaces directement
```

### Relations HVAC

| Relation | Source | Destination | Sémantique |
|----------|--------|-------------|------------|
| **FEEDS** | Chiller | AHU | Eau glacée alimente la batterie froid AHU |
| **FEEDS** | Boiler | AHU | Eau chaude alimente la batterie chaud AHU |
| **FEEDS** | AHU | VAV | Air traité distribué aux VAV |
| **FEEDS** | AHU | FCU | Eau (pas air) si FCU 4 tubes |
| **SERVES** | AHU | Building | L'AHU dessert le bâtiment (ou partie) |
| **SERVES** | VAV | Zone | Le VAV dessert une zone thermique |
| **SERVES** | FCU | Space | Le FCU dessert un ou plusieurs spaces |
| **CONTROLS** | Thermostat | FCU/VAV | Le thermostat pilote le terminal |
| **LOCATED_IN** | FCU | Space | Le FCU est physiquement dans l'espace |
| **LOCATED_IN** | VAV | Floor | Le VAV est dans le faux plafond de l'étage |

### Logique SERVES pour les queries

**Q4 (Inventaire température étage)** :
```
Floor -[CONTAINS]-> Space <-[SERVES]- FCU -[HAS_POINT]-> Point(temperature)
                         <-[LOCATED_IN]- Thermostat -[HAS_POINT]-> Point(temperature)
```

**Q11 (Confort thermique)** :
```
Space <-[SERVES]- FCU -[HAS_POINT]-> Point(temperature)
      <-[LOCATED_IN]- Thermostat -[HAS_POINT]-> Point(setpoint)
```

---

## 3. LIGHTING (Éclairage)

### Hiérarchie physique

```
[TD Étage] ─────────────── Location: Gaine technique
    │
    ├── [Circuit Éclairage]
    │       │
    │       ├── [DALI Gateway] ── Location: Faux plafond ou armoire
    │       │       │
    │       │       └── [Luminaire] ── Location: Space (plafond)
    │       │               Points: dim_level, power, status
    │       │
    │       └── [Luminaire direct] ── Sans DALI, on/off simple
    │
    └── [Détecteur présence] ── Location: Space
            Points: occupancy_status
            CONTROLS -> Luminaires de la zone
```

### Relations Lighting

| Relation | Source | Destination |
|----------|--------|-------------|
| **FEEDS** | TD | DALI Gateway |
| **FEEDS** | DALI Gateway | Luminaire |
| **CONTROLS** | Presence Detector | Luminaire |
| **LOCATED_IN** | Luminaire | Space |
| **SERVES** | Luminaire | Space |

---

## 4. PLUMBING (Plomberie / Fluides)

### Hiérarchie physique

```
[Arrivée Eau Ville] ───── Location: Local technique sous-sol
    │
    ├── [Compteur Général Eau]
    │       Points: volume, flow_rate
    │
    ├── [Surpresseur] ───── Si immeuble haut
    │       Points: pressure, status
    │
    ├── [Ballon ECS] ────── Eau Chaude Sanitaire
    │       Points: water_temp, heating_status
    │
    └── [Distribution] ──── Vers sanitaires par étage

[Arrivée Gaz] ──────────── Location: Local technique
    │
    ├── [Compteur Gaz]
    │       Points: volume, flow_rate
    │
    └── [Détendeur] ─────── Régulation pression
```

### Relations Plumbing

| Relation | Source | Destination |
|----------|--------|-------------|
| **FEEDS** | Compteur Eau | Building |
| **FEEDS** | Surpresseur | Floors (étages hauts) |
| **SERVES** | Ballon ECS | Building |

---

## 5. ELEVATOR (Ascenseurs / Escalators)

### Hiérarchie physique

```
[Ascenseur] ──────────── Location: Gaine ascenseur (traverse tous les floors)
    │
    ├── [Moteur] ────────── Location: Local machinerie (rooftop ou sous-sol)
    │       Points: power, status, fault
    │
    ├── [Cabine] ───────────
    │       Points: position (floor), load, door_status
    │
    └── [Contrôleur] ───────
            Points: call_count, trip_count, mode

[Escalator] ─────────────── Location: Entre 2 floors
    Points: speed, status, fault, direction
```

### Relations Elevator

| Relation | Source | Destination |
|----------|--------|-------------|
| **SERVES** | Elevator | Floor (tous les étages desservis) |
| **LOCATED_IN** | Elevator | Building |
| **FEEDS** | TD | Elevator Motor |

---

## 6. PARKING

### Hiérarchie physique

```
[Parking] ────────────────── Location: Basement levels
    │
    ├── [Barrière Entrée/Sortie]
    │       Points: status, vehicle_count
    │
    ├── [Capteur Place] ──── 1 par place
    │       Points: occupancy_status
    │       LOCATED_IN -> Parking Space
    │
    ├── [Borne EV] ────────── Charge véhicule électrique
    │       Points: power, energy, status, connector_status
    │       LOCATED_IN -> Parking Space
    │
    ├── [Ventilation Parking]
    │       Points: CO_level, fan_speed, status
    │       MONITORS -> CO level
    │
    └── [Éclairage Parking]
            LOCATED_IN -> Parking Zone
```

### Relations Parking

| Relation | Source | Destination |
|----------|--------|-------------|
| **LOCATED_IN** | Capteur Place | Parking Space |
| **LOCATED_IN** | Borne EV | Parking Space |
| **SERVES** | Ventilation | Parking Zone |
| **MONITORS** | CO Sensor | Parking Zone |

---

## 7. FIRE SAFETY (Sécurité Incendie)

### Hiérarchie physique

```
[Centrale Incendie SSI] ─── Location: Local sécurité (RDC ou PC sécu)
    │
    ├── [Détecteur Fumée] ── Location: Chaque Space
    │       Points: alarm, fault, status
    │
    ├── [Détecteur Chaleur] ─ Location: Cuisines, parkings
    │       Points: alarm, temperature
    │
    ├── [Déclencheur Manuel] ── Location: Circulations, issues
    │       Points: alarm, status
    │
    ├── [Sprinkler] ───────── Location: Chaque Space (faux plafond)
    │       Points: flow_alarm (sur vanne de zone)
    │
    ├── [Désenfumage] ─────── Volets + Extracteurs
    │       Points: damper_position, fan_status
    │       SERVES -> Zone de désenfumage
    │
    └── [Éclairage Sécurité] ── BAES
            Points: status, battery_level
            LOCATED_IN -> Circulations
```

### Relations Fire Safety

| Relation | Source | Destination |
|----------|--------|-------------|
| **MONITORS** | Smoke Detector | Space |
| **LOCATED_IN** | Smoke Detector | Space |
| **CONTROLS** | SSI Centrale | Désenfumage, Portes coupe-feu |
| **SERVES** | Désenfumage | Zone |

---

## 8. SECURITY (Sûreté)

### Hiérarchie physique

```
[Centrale Sûreté] ──────── Location: PC Sécurité
    │
    ├── [Contrôle Accès]
    │       ├── [Lecteur Badge] ── Location: Entrées, portes sécurisées
    │       │       Points: access_granted, access_denied, badge_id
    │       │
    │       └── [Gâche/Ventouse] ── Verrouillage porte
    │               Points: lock_status
    │
    ├── [Vidéosurveillance]
    │       ├── [Caméra] ────────── Location: Entrées, parkings, halls
    │       │       Points: status, recording
    │       │
    │       └── [NVR/Enregistreur]
    │               Points: storage_used, status
    │
    └── [Intrusion]
            ├── [Détecteur mouvement] ── Location: Zones sensibles
            │       Points: alarm, status
            │
            └── [Contact porte/fenêtre]
                    Points: open, closed, tamper
```

### Relations Security

| Relation | Source | Destination |
|----------|--------|-------------|
| **MONITORS** | Camera | Space/Zone |
| **LOCATED_IN** | Badge Reader | Space (entrée) |
| **CONTROLS** | Badge Reader | Door Lock |

---

## 9. AV (Audio-Visuel)

### Hiérarchie physique

```
[Salle de réunion / Conférence]
    │
    ├── [Écran/Vidéoprojecteur]
    │       Points: power_status, input_source
    │
    ├── [Système Visio]
    │       Points: call_status, mute
    │
    ├── [Microphone]
    │       Points: mute, level
    │
    └── [Contrôleur AV] ──── Crestron, Extron, etc.
            CONTROLS -> Tous les équipements AV de la salle
```

### Relations AV

| Relation | Source | Destination |
|----------|--------|-------------|
| **LOCATED_IN** | AV Equipment | Space (salle) |
| **SERVES** | AV System | Space |
| **CONTROLS** | AV Controller | Screen, Projector, etc. |

---

## 10. IT (Infrastructure Informatique)

### Hiérarchie physique

```
[Datacenter / Local IT] ─── Location: Dédié ou mutualisé
    │
    ├── [Rack Serveur]
    │       ├── [Serveur]
    │       │       Points: cpu_usage, memory_usage, power
    │       │
    │       └── [Switch Réseau]
    │               Points: port_status, traffic_in, traffic_out
    │
    ├── [CRAC / Clim IT] ──── Climatisation dédiée
    │       Points: supply_temp, return_temp, humidity
    │       SERVES -> Datacenter Space
    │
    ├── [UPS IT]
    │       Points: load, battery, input_power
    │       FEEDS -> Racks
    │
    └── [PDU] ─────────────── Distribution électrique rack
            Points: power_per_outlet
            FEEDS -> Serveurs
```

### Relations IT

| Relation | Source | Destination |
|----------|--------|-------------|
| **FEEDS** | UPS | PDU |
| **FEEDS** | PDU | Server |
| **SERVES** | CRAC | Datacenter Space |
| **LOCATED_IN** | Rack | Datacenter Space |

---

## SYNTHÈSE : Relations inter-domaines

```
                    ┌─────────────┐
                    │   TGBT      │
                    └──────┬──────┘
                           │ FEEDS
          ┌────────────────┼────────────────┐
          │                │                │
    ┌─────▼─────┐    ┌─────▼─────┐    ┌─────▼─────┐
    │ TD Étage  │    │   UPS     │    │ TD Parking│
    └─────┬─────┘    └─────┬─────┘    └─────┬─────┘
          │                │                │
          │ FEEDS          │ FEEDS          │ FEEDS
          │                │                │
    ┌─────▼─────┐    ┌─────▼─────┐    ┌─────▼─────┐
    │FCU, Lum,  │    │ Serveurs  │    │Borne EV,  │
    │VAV, etc.  │    │ IT        │    │Ventil.    │
    └───────────┘    └───────────┘    └───────────┘
          │
          │ SERVES
          │
    ┌─────▼─────┐
    │  Space    │◄──── Tenant OCCUPIES
    └───────────┘
```

---

## État du générateur (mise à jour janvier 2025)

### ✅ Problèmes résolus

#### 1. Meters avec localisation
- **Résolu** : MainMeter/SubMeter créés avec `space_id` via `_find_technical_space()`
- Les compteurs sont localisés dans les espaces techniques (technical_elec)

#### 2. FEEDS complet (modèle 3 axes)
- **Résolu** : Chaîne complète `MainMeter -[FEEDS]-> SubMeter -[FEEDS]-> Equipment`
- SubMeter_Usage alimente les équipements par domaine/type (HVAC, Lighting, etc.)

#### 3. Relation Tenant <-> Comptage (modèle 3 axes)
- **Résolu différemment** : Au lieu de `Space -[IS_FED_BY]-> TD`
- Nouvelle relation directe : `SubMeter_Tenant -[METERS_TENANT]-> Tenant`
- Permet Q8/Q9 en 2 hops au lieu de 5

#### 4. Modèle de comptage 3 axes (RE2020/BACS/Décret Tertiaire)
- **Axe 1 - USAGE** : SubMeter_HVAC, SubMeter_Lighting, SubMeter_Plugs, SubMeter_ECS, SubMeter_Elevator
- **Axe 2 - ZONE** : SubMeter_Zone_North, SubMeter_Zone_South, etc. (METERS_ZONE → Space)
- **Axe 3 - TENANT** : SubMeter_Tenant_X (METERS_TENANT → Tenant)

#### 5. SERVES étendu
- **Résolu** : Nouveau scope "floors" pour Elevator → tous les Floors du bâtiment
- PassengerElevator et FreightElevator SERVES tous les étages
- ExhaustFan SERVES les espaces parking (scope floor)
- CRAC SERVES l'espace IT (scope space)

#### 6. Relations MONITORS pour espaces
- **Résolu** : Nouveau `MONITORS_SPACE_RULES` pour capteurs environnementaux
- SmokeDetector MONITORS les espaces (bureau, réunion, corridor, etc.)
- CO_Sensor MONITORS les parkings
- PeopleCounter MONITORS les espaces occupés (bureau open, conférence, lobby)

### ⚠️ Améliorations possibles

#### 1. Domaines partiels
Les 10 domaines sont présents (Electrical, HVAC, Lighting, Plumbing, Elevator, Parking, FireSafety, Security, AV, IT) mais tous les équipements documentés ci-dessus ne sont pas encore implémentés.

---

## Queries et modèle de données

| Query | Pattern | Hops | Status |
|-------|---------|------|--------|
| Q1 | Meter → FEEDS* → Equipment | 1-10 | ✅ Fonctionne |
| Q3 | Space ↔ SERVES/LOCATED_IN/MONITORS ↔ Equipment | 1 | ✅ Enrichi |
| Q4 | Floor → Space → Equipment → Point(temp) | 4 | ✅ Fonctionne |
| Q8 | Tenant ← METERS_TENANT ← SubMeter → Point | 2 | ✅ Simplifié |
| Q9 | Tenant ← METERS_TENANT ← SubMeter → Point | 2 | ✅ Simplifié |
| Q13 | Space(type) ← LOCATED_IN ← Equipment → Point | 3 | ✅ Fonctionne |

