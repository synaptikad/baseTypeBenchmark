# Plan d'Enrichissement du Générateur

## Objectif
Créer un modèle smart building réaliste qui démontre l'avantage des graphes pour les requêtes complexes.

---

## 1. Nouveaux Node Types

### 1.1 Entités Maintenance
```
WorkOrder (Ticket de maintenance)
├── Properties: id, title, status, priority, created_at, due_date, completed_at
├── Status: open, in_progress, on_hold, completed, cancelled
└── Priority: critical, high, medium, low

Alarm (Alarme temps réel)
├── Properties: id, severity, message, triggered_at, acknowledged_at, resolved_at
├── Severity: critical, warning, info
└── Source: equipment malfunction, threshold breach, scheduled

Incident (Incident historique)
├── Properties: id, type, description, started_at, ended_at, root_cause
└── Type: equipment_failure, power_outage, hvac_fault, security_breach

Technician (Intervenant)
├── Properties: id, name, company, specialties[], certifications[]
└── Specialties: HVAC, Electrical, Security, IT, Fire
```

### 1.2 Entités Planning
```
Schedule (Horaire occupation/fonctionnement)
├── Properties: id, name, type, timezone
├── Type: occupancy, hvac, lighting, access
└── Contains: ScheduleEntry[]

ScheduleEntry
├── Properties: day_of_week, start_time, end_time, mode
└── Mode: occupied, unoccupied, standby, night_setback
```

### 1.3 Entités Contractuelles (enrichies)
```
Lease (Bail locataire)
├── Properties: id, start_date, end_date, rent_per_m2, charges
└── Links: Tenant, Space[]

ServiceContract (Contrat maintenance)
├── Properties: id, type, provider, start_date, end_date, sla_response_hours
└── Type: preventive, corrective, full_service
└── Covers: Equipment[], Zone[]
```

---

## 2. Nouvelles Relations (Edge Types)

### 2.1 Equipment ↔ Equipment
```
CONTROLS      Equipment → Equipment    (BMS→VAV, Dimmer→LightingCircuit)
MONITORS      Equipment → Equipment    (Sensor→Equipment being monitored)
BACKS_UP      Equipment → Equipment    (UPS→Server, Generator→MainMeter)
CONNECTED_TO  Equipment → Equipment    (NetworkSwitch→Server, Gateway→Sensors)
SUPPLIES      Equipment → Equipment    (Chiller→AHU, Boiler→AHU)
```

### 2.2 Maintenance Relations
```
ASSIGNED_TO       WorkOrder → Technician
CONCERNS          WorkOrder → Equipment | Space
TRIGGERED_BY      Alarm → Equipment | Point
ACKNOWLEDGED_BY   Alarm → Technician
CAUSED            Incident → WorkOrder[]
AFFECTED          Incident → Equipment | Space
RESOLVED_BY       Incident → Technician
```

### 2.3 Planning Relations
```
HAS_SCHEDULE      Space | Equipment | Zone → Schedule
FOLLOWS           Equipment → Schedule (pour fonctionnement)
```

### 2.4 Contractual Relations
```
LEASES            Tenant → Space (avec dates, conditions)
COVERED_BY        Equipment → ServiceContract
MAINTAINED_BY     Equipment → Technician (responsable habituel)
PROVIDES_SERVICE  Technician → ServiceContract
```

### 2.5 Spatial Enrichies
```
ACCESSIBLE_FROM   Space → Space (avec badge/clearance level)
EMERGENCY_EXIT    Space → Space (chemin évacuation)
VENTILATED_BY     Space → Equipment (AHU/FCU qui ventile)
```

---

## 3. Equipment Types à Instancier

### 3.1 HVAC Complet
```
Chiller           → SUPPLIES → AHU (production froid)
Boiler            → SUPPLIES → AHU (production chaud)
CRAC              → SERVES → technical_it (climatisation IT)
CoolingTower      → SUPPLIES → Chiller
HeatPump          → SUPPLIES → AHU | FCU
```

### 3.2 Lighting
```
DALI_Gateway      → CONTROLS → LED_Driver_DALI2[]
LED_Driver_DALI2  → SERVES → Space (éclairage zone)
Dimmer            → CONTROLS → Lighting_Circuit
Emergency_Lighting → SERVES → corridor, stairwell (secours)
Lighting_Circuit  → SERVES → Space[]
```

### 3.3 Fire Safety
```
FireAlarmPanel    → MONITORS → SmokeDetector[], ManualCallPoint[]
SmokeDetector     → MONITORS → Space
ManualCallPoint   → LOCATED_IN → corridor, stairwell
Sprinkler         → SERVES → Space
FireExtinguisher  → LOCATED_IN → corridor, technical spaces
```

### 3.4 Parking
```
BarrierGate       → CONTROLS → parking entry/exit
ParkingSensorMagnetic → MONITORS → parking_spot
ParkingGuidanceController → CONTROLS → ParkingSensorMagnetic[]
EVChargerLevel2   → SERVES → parking_spot (borne recharge)
TicketDispenser   → LOCATED_IN → parking entry
```

### 3.5 BMS/Sensors Complet
```
Occupancy_Sensor  → MONITORS → Space (présence)
CO2_Sensor        → MONITORS → Space (tous bureaux, pas que open)
Humidity_Sensor   → MONITORS → Space
AirQuality_Sensor → MONITORS → Space
WaterLeakSensor   → MONITORS → technical spaces
```

### 3.6 Electrical Complet
```
Transformer_HT_BT → FEEDS → MainMeter
Generator         → BACKS_UP → MainMeter
Breaker           → FEEDS → SubMeter | Equipment
PDU               → FEEDS → RackServer[] (distribution rack)
```

---

## 4. Coverage par Space Type

| Space Type | Equipment Requis |
|------------|------------------|
| office_* | VAV/FCU, TemperatureSensor, Occupancy_Sensor, CO2_Sensor, Lighting_Circuit |
| meeting_* | VAV/FCU, TemperatureSensor, Occupancy_Sensor, CO2_Sensor, Lighting_Circuit |
| corridor | Emergency_Lighting, SmokeDetector, Occupancy_Sensor (économie énergie) |
| restroom | Ventilation_Fan, Occupancy_Sensor, Lighting_Circuit |
| lobby | BadgeReader, IPCamera, TemperatureSensor, Lighting_Circuit |
| parking | ParkingSensor[], BarrierGate, EVCharger, IPCamera, Emergency_Lighting |
| storage | SmokeDetector, TemperatureSensor (si sensible) |
| kitchen | Ventilation_Hood, SmokeDetector, CO2_Sensor |
| technical_hvac | AHU, Chiller/Boiler, TemperatureSensor, WaterLeakSensor |
| technical_elec | MainMeter, SubMeter[], Transformer, TemperatureSensor |
| technical_it | UPS, PDU, RackServer[], NetworkSwitch, CRAC, TemperatureSensor |
| rooftop | CoolingTower, Chiller (si rooftop), WeatherStation |

---

## 5. Scénarios de Maintenance

### 5.1 WorkOrders Types
```python
WORKORDER_TEMPLATES = [
    {"type": "preventive", "title": "Maintenance préventive {equipment_type}",
     "frequency_days": 90, "duration_hours": 2},
    {"type": "corrective", "title": "Réparation {equipment_type} - {symptom}",
     "priority": "high", "sla_hours": 4},
    {"type": "inspection", "title": "Inspection {zone_type}",
     "frequency_days": 30, "duration_hours": 1},
]
```

### 5.2 Alarm Scenarios
```python
ALARM_SCENARIOS = [
    {"trigger": "temperature > threshold", "severity": "warning", "equipment": "HVAC"},
    {"trigger": "power_consumption > limit", "severity": "critical", "equipment": "Electrical"},
    {"trigger": "occupancy_after_hours", "severity": "info", "equipment": "Security"},
    {"trigger": "smoke_detected", "severity": "critical", "equipment": "FireSafety"},
    {"trigger": "water_leak", "severity": "critical", "equipment": "BMS"},
]
```

### 5.3 Incident History
```python
INCIDENT_TEMPLATES = [
    {"type": "equipment_failure", "mttr_hours": 4, "generates_workorders": 2},
    {"type": "power_outage", "mttr_hours": 1, "affects": ["IT", "Security"]},
    {"type": "hvac_fault", "mttr_hours": 8, "affects_spaces": True},
]
```

---

## 6. Queries Graph-Native à Ajouter

Ces queries démontrent l'avantage des graphes :

### 6.1 Impact Analysis (Q23 reformulé)
```
"Si cet équipement tombe en panne, quels espaces/équipements sont impactés ?"
→ Traverse FEEDS, SERVES, SUPPLIES, BACKS_UP
→ SQL: CTE récursif complexe, graphe: 3 lignes Cypher
```

### 6.2 Maintenance Chain
```
"Quel technicien a traité le plus d'incidents sur les équipements HVAC ce mois ?"
→ Traverse: Incident → CAUSED → WorkOrder → ASSIGNED_TO → Technician
→ Filter: Equipment.domain = 'HVAC'
```

### 6.3 Compliance Check
```
"Quels équipements critiques n'ont pas de contrat de maintenance actif ?"
→ Traverse: Equipment WHERE critical = true
→ Check: NOT EXISTS (Equipment)-[:COVERED_BY]->(ServiceContract WHERE end_date > now())
```

### 6.4 Energy Path
```
"Quel est le chemin électrique complet de la source au serveur X ?"
→ Traverse: Transformer → FEEDS* → RackServer
→ SQL: CTE avec profondeur variable, graphe: shortestPath()
```

### 6.5 Evacuation Path
```
"Chemin d'évacuation le plus court depuis cet espace ?"
→ Traverse: Space -[:EMERGENCY_EXIT|ACCESSIBLE_FROM]-> ... -> exit
→ SQL: Impossible efficacement, graphe: shortestPath avec filtre
```

### 6.6 Tenant Impact
```
"Si je coupe ce circuit, quels tenants sont affectés ?"
→ Traverse: SubMeter → FEEDS → Equipment → SERVES → Space ← OCCUPIES ← Tenant
```

---

## 7. Plan d'Implémentation

### Phase 1: Nouveaux Node Types (generator.py)
- [ ] Ajouter classes/création pour WorkOrder, Alarm, Incident, Technician
- [ ] Ajouter Schedule, ScheduleEntry
- [ ] Enrichir Lease, ServiceContract

### Phase 2: Equipment Instantiation
- [ ] Lighting: DALI_Gateway, LED_Driver, Emergency_Lighting
- [ ] FireSafety: FireAlarmPanel, SmokeDetector, Sprinkler
- [ ] Parking: BarrierGate, ParkingSensor, EVCharger
- [ ] HVAC: Chiller, Boiler, CRAC, CoolingTower
- [ ] Electrical: Transformer, Generator, Breaker, PDU
- [ ] BMS: Occupancy_Sensor, CO2 étendu, WaterLeakSensor

### Phase 3: Relations Enrichies
- [ ] Equipment↔Equipment: CONTROLS, MONITORS, BACKS_UP, SUPPLIES
- [ ] Maintenance: ASSIGNED_TO, CONCERNS, TRIGGERED_BY, CAUSED
- [ ] Planning: HAS_SCHEDULE, FOLLOWS
- [ ] Spatial: ACCESSIBLE_FROM, EMERGENCY_EXIT, VENTILATED_BY

### Phase 4: Maintenance Scenarios
- [ ] Générer WorkOrders (préventifs + correctifs)
- [ ] Générer Alarms (actives + historiques)
- [ ] Générer Incidents avec chaîne causale
- [ ] Assigner Technicians

### Phase 5: Coverage 100%
- [ ] Équiper tous les types d'espaces
- [ ] Vérifier tous les floors ont tous les domaines pertinents

### Phase 6: Nouvelles Queries
- [ ] Q24+: Maintenance chain
- [ ] Q25+: Compliance check
- [ ] Q26+: Energy path
- [ ] Q27+: Evacuation path

---

## 8. Métriques Cibles

| Métrique | Actuel | Cible |
|----------|--------|-------|
| Node types | 9 | 15+ |
| Edge types | 13 | 25+ |
| Equipment types instanciés | 10/32 (31%) | 28/32 (87%) |
| Spaces avec equipment | ~50% | 100% |
| Equipment↔Equipment edges | ~20 | ~200+ |
| Maintenance entities | 0 | 50+ par building |

---

## 9. Validation

Après enrichissement, vérifier :
1. **Connectivité** : Pas de composants isolés (sauf orphan intentionnel)
2. **Couverture** : Tous espaces ont au moins 2 équipements
3. **Chaînes** : FEEDS chain complète de Transformer à endpoint
4. **Maintenance** : Chaque équipement critique a un contrat
5. **Queries** : Nouvelles queries démontrent avantage graphe
