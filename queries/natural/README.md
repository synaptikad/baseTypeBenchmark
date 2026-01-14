# BaseType Benchmark - Questions en Langage Naturel

Ce dossier contient les 42 requêtes du benchmark exprimées en langage naturel (FR/EN).

This folder contains the 42 benchmark queries expressed in natural language (FR/EN).

---

## Légende / Legend

| Symbole | Status | Description |
|---------|--------|-------------|
| ✅ | NATIVE | Support natif optimal |
| ⚠️ | DEGRADED | Possible avec limitations |
| 🔶 | VERY_DEGRADED | Possible mais complexe |
| ❌ | IMPOSSIBLE | Non supporté |

### Paradigmes / Paradigms

- **P1**: PostgreSQL Relationnel
- **P2**: PostgreSQL JSONB
- **M1**: Memgraph (graphe seul)
- **M2**: Memgraph + TimescaleDB
- **O2**: Oxigraph (RDF) + TimescaleDB

---

## Index des Requêtes / Query Index

### Graph-Only (Q1-Q5)
Traversées structurelles pures / Pure structural traversals

| Query | Nom | Question (FR) |
|-------|-----|---------------|
| [Q1](graph-only/Q1-energy-chain.md) | Energy Chain | Quels équipements sont alimentés par ce compteur ? |
| [Q2](graph-only/Q2-functional-impact.md) | Functional Impact | Quels équipements parents sont affectés par cette panne ? |
| [Q3](graph-only/Q3-space-services.md) | Space Services | Quels équipements desservent cet espace ? |
| [Q4](graph-only/Q4-floor-temperature-inventory.md) | Floor Temperature Inventory | Quels capteurs de température couvrent cet étage ? |
| [Q5](graph-only/Q5-orphans.md) | Orphans | Quels équipements n'ont aucune relation ? |

### Timeseries (Q6)
Agrégations temporelles / Temporal aggregations

| Query | Nom | Question (FR) |
|-------|-----|---------------|
| [Q6](timeseries/Q6-hourly-aggregation.md) | Hourly Aggregation | Quels sont les agrégats horaires de ce point ? |

### Hybrid (Q7-Q13)
Sélection graphe + agrégation timeseries / Graph selection + timeseries aggregation

| Query | Nom | Question (FR) |
|-------|-----|---------------|
| [Q7](hybrid/Q7-drift-top20.md) | Drift Top-20 | Quels points ont la plus grande variance ? |
| [Q8](hybrid/Q8-tenant-energy.md) | Tenant Energy | Quelle est la consommation d'énergie de ce locataire ? |
| [Q9](hybrid/Q9-tenant-carbon-footprint.md) | Tenant Carbon Footprint | Quelle est l'empreinte carbone de ce locataire ? |
| [Q10](hybrid/Q10-security-access-analysis.md) | Security Access Analysis | Quels équipements de sécurité couvrent ce bâtiment ? |
| [Q11](hybrid/Q11-it-infrastructure-impact.md) | IT Infrastructure Impact | Quels serveurs dépendent de cette alimentation ? |
| [Q12](hybrid/Q12-full-building-analytics.md) | Full Building Analytics | Quelles sont les métriques globales du bâtiment ? |
| [Q13](hybrid/Q13-office-hours-comfort.md) | Office Hours Comfort | Quel est le confort des bureaux aux heures de travail ? |

### JSONB-Specific (Q14-Q19)
Requêtes exploitant les propriétés JSONB / JSONB property queries

| Query | Nom | Question (FR) |
|-------|-----|---------------|
| [Q14](jsonb-specific/Q14-protocol-query.md) | Protocol Query | Quels points communiquent avec ce device BACnet ? |
| [Q15](jsonb-specific/Q15-warranty-expiry.md) | Warranty Expiry | Quels équipements ont une garantie qui expire bientôt ? |
| [Q16](jsonb-specific/Q16-semantic-tag-search.md) | Semantic Tag Search | Quels équipements correspondent à ces tags sémantiques ? |
| [Q17](jsonb-specific/Q17-capability-filter.md) | Capability Filter | Quels équipements ont cette capacité HVAC ? |
| [Q18](jsonb-specific/Q18-calibration-chain.md) | Calibration Chain | Quels points ont une calibration échue dans cette chaîne ? |
| [Q19](jsonb-specific/Q19-equipment-digital-twin.md) | Equipment Digital Twin | Quel est le document JSON complet de cet équipement ? |

### Graph-Native (Q20-Q23, Q27-Q30)
Algorithmes graphe natifs / Native graph algorithms

| Query | Nom | Question (FR) |
|-------|-----|---------------|
| [Q20](graph-native/Q20-shortest-hvac-path.md) | Shortest HVAC Path | Quel est le chemin le plus court vers cet espace ? |
| [Q21](graph-native/Q21-electrical-resilience.md) | Electrical Resilience | Quels sont les chemins d'alimentation et les SPOF ? |
| [Q22](graph-native/Q22-equipment-siblings.md) | Equipment Siblings | Quels équipements partagent le même parent ? |
| [Q23](graph-native/Q23-failure-impact-analysis.md) | Failure Impact Analysis | Quels nœuds sont impactés par cette panne ? |
| [Q27](graph-native/Q27-evacuation-path.md) | Evacuation Path | Quel est le chemin d'évacuation le plus court ? |
| [Q28](graph-native/Q28-tenant-impact-chain.md) | Tenant Impact Chain | Quels locataires sont impactés par cette panne ? |
| [Q29](graph-native/Q29-all-power-paths.md) | All Power Paths | Quels sont tous les chemins d'alimentation ? |
| [Q30](graph-native/Q30-weighted-failure-impact.md) | Weighted Failure Impact | Quel est l'impact pondéré de cette panne ? |

### SQL-Native (Q31-Q34)
Fonctionnalités SQL avancées / Advanced SQL features

| Query | Nom | Question (FR) |
|-------|-----|---------------|
| [Q31](sql-native/Q31-rolling-aggregation.md) | Rolling Aggregation | Quels sont les agrégats glissants ? |
| [Q32](sql-native/Q32-json-schema-validation.md) | JSON Schema Validation | Les données JSONB respectent-elles le schéma ? |
| [Q33](sql-native/Q33-latest-value-per-space.md) | Latest Value per Space | Quelle est la dernière valeur par espace ? |
| [Q34](sql-native/Q34-materialized-energy-summary.md) | Materialized Energy Summary | Quel est le résumé énergétique matérialisé ? |

### Validation (Q24-Q26, Q35-Q41)
Lectures de validation post-écriture / Post-write validation reads

| Query | Nom | Question (FR) |
|-------|-----|---------------|
| [Q24](validation/Q24-maintenance-history.md) | Maintenance History | Quel est l'historique de maintenance ? |
| [Q25](validation/Q25-equipment-audit-trail.md) | Equipment Audit Trail | Quel est le journal d'audit de cet équipement ? |
| [Q26](validation/Q26-capability-evolution.md) | Capability Evolution | Comment les capacités ont-elles évolué ? |
| [Q35](validation/Q35-validate-timeseries-append.md) | Validate Timeseries Append | Les mesures ont-elles été insérées ? |
| [Q36](validation/Q36-validate-metadata-update.md) | Validate Metadata Update | Les métadonnées ont-elles été mises à jour ? |
| [Q37](validation/Q37-validate-relation-mutation.md) | Validate Relation Mutation | La relation a-t-elle été modifiée ? |
| [Q38](validation/Q38-validate-property-removal.md) | Validate Property Removal | La propriété a-t-elle été supprimée ? |
| [Q39](validation/Q39-verify-tenant-spaces.md) | Verify Tenant Spaces | Les espaces du locataire sont-ils corrects ? |
| [Q40](validation/Q40-verify-tenant-meters.md) | Verify Tenant Meters | Les compteurs du locataire sont-ils corrects ? |
| [Q41](validation/Q41-verify-tenant-consolidation.md) | Verify Tenant Consolidation | La consolidation locataire est-elle correcte ? |

### Write Operations (QW1-QW12)
Opérations d'écriture / Write operations

| Query | Nom | Question (FR) |
|-------|-----|---------------|
| [QW1](write/QW1-timeseries-append.md) | Timeseries Append | Insérer de nouvelles mesures IoT |
| [QW2](write/QW2-metadata-update.md) | Metadata Update | Mettre à jour les métadonnées |
| [QW3](write/QW3-relation-mutation.md) | Relation Mutation | Modifier une relation |
| [QW4](write/QW4-maintenance-event-append.md) | Maintenance Event Append | Ajouter un événement de maintenance |
| [QW5](write/QW5-deep-calibration-update.md) | Deep Calibration Update | Mettre à jour la calibration |
| [QW6](write/QW6-metadata-merge.md) | Metadata Merge | Fusionner des métadonnées |
| [QW7](write/QW7-add-capability.md) | Add Capability | Ajouter une capacité |
| [QW8](write/QW8-remove-metadata-key.md) | Remove Metadata Key | Supprimer une clé de métadonnées |
| [QW9](write/QW9-tenant-move-in.md) | Tenant Move-In | Emménagement d'un locataire |
| [QW10](write/QW10-tenant-move-out.md) | Tenant Move-Out | Déménagement d'un locataire |
| [QW11](write/QW11-space-reassignment.md) | Space Reassignment | Réassignation d'espace |
| [QW12](write/QW12-tenant-merge.md) | Tenant Merge | Fusion de locataires |
