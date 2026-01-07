// Q6: Hourly Aggregation
// Status: IMPOSSIBLE pour M1 (Memgraph Standalone)
// Raison: M1 n'a pas de moteur timeseries intégré.
//         Les agrégations temporelles (time_bucket, AVG, MIN, MAX par heure)
//         ne sont pas supportées nativement.
//
// Alternative: Utiliser M2 (Memgraph + TimescaleDB externe)
//
// Paramètres attendus:
//   $point_id: ID du point de mesure
//   $date_start: Début de période (Unix timestamp ms)
//   $date_end: Fin de période (Unix timestamp ms)
//
// Cette query retourne toujours un résultat vide pour M1.

RETURN "IMPOSSIBLE: M1 ne supporte pas les agrégations timeseries" AS error;
