# Métriques

## Métriques de performance

| Métrique | Unité | Description |
|----------|-------|-------------|
| p50 | secondes | Médiane des latences de requêtes |
| p95 | secondes | 95e percentile des latences |
| min | secondes | Latence minimale observée |
| max | secondes | Latence maximale observée |
| time_to_ingest | secondes | Temps d'ingestion complet |

## Métriques de ressources

| Métrique | Unité | Description |
|----------|-------|-------------|
| RAM steady-state | Mo | Consommation mémoire en régime nominal |
| RAM peak | Mo | Consommation mémoire maximale |
| CPU moyen | % | Utilisation CPU moyenne pendant l'exécution |
| Disque | Mo | Occupation du volume Docker |

## Interprétation énergétique

Les métriques de ressources peuvent être traduites en impact énergétique :

| Ressource | Estimation |
|-----------|------------|
| RAM | ~0.125 W par Go (rafraîchissement permanent) |
| RAM 256 Go | ~32 W permanent = ~280 kWh/an |
| SSD repos | ~1-2 W |
| SSD actif | ~5-10 W |

Ces estimations permettent de contextualiser les différences de consommation mémoire entre paradigmes.

## Format d'export

Les résultats sont exportés en JSON et CSV dans `bench/results/` :

```json
{
  "engine": "pg_rel",
  "profile": "pg_rel", 
  "scale_mode": "small",
  "seed": 42,
  "ingestion": {"time_s": 12.5, "items": 18000},
  "queries": [
    {
      "query": "Q1",
      "measure_runs": [0.234, 0.228, ...],
      "stats": {"p50": 0.231, "p95": 0.245, "min": 0.220, "max": 0.251}
    }
  ],
  "resources": {
    "steady_state_mem_mb": 128,
    "peak_mem_mb": 256,
    "avg_cpu_pct": 15.2,
    "volume_mb": 45
  }
}
```

## Comparabilité

Pour garantir la comparabilité des résultats :

- Les mesures de warmup ne sont jamais incluses dans les statistiques
- Chaque requête est exécutée N fois (configurable, défaut 10)
- Les métriques système sont échantillonnées pendant toute la durée d'exécution
- Les versions des moteurs sont loggées avec les résultats
