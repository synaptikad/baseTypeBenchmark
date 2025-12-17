#!/bin/bash

# Script automatisé pour exécuter les benchmarks séquentiellement avec rigueur académique
# Garantit un contexte propre entre chaque run (nettoyage volumes, pauses)
# Usage: ./run_benchmarks.sh [profile]  # profile optionnel pour relancer un seul

# set -uo pipefail  # Désactivé pour permettre la continuation en cas d'échec

# Configuration
SCALE_MODE="${SCALE_MODE:-small}"
SEED="${SEED:-42}"
PAUSE_BETWEEN_RUNS=60
HEALTH_CHECK_TIMEOUT=120
RESULTS_DIR="bench/results"
LOG_FILE="benchmark_run_$(date +%Y%m%d_%H%M%S).log"

# Profils à exécuter (dans l'ordre recommandé)
PROFILES=("pg_rel" "pg_jsonb" "memgraph" "oxigraph")

# Fonction de logging
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $*" | tee -a "$LOG_FILE"
}

# Vérifier si un conteneur est healthy (plus robuste)
wait_healthy() {
    local container="$1"
    local timeout="$2"
    local start_time=$(date +%s)

    log "Attente de la santé de $container (timeout: ${timeout}s)"
    while true; do
        local health_status
        health_status=$(docker compose ps --format "table {{.Name}}\t{{.Status}}" | grep "^${container}" | awk '{print $2}' || echo "")
        if [[ "$health_status" == *"healthy"* ]]; then
            log "$container est healthy"
            return 0
        fi
        if (( $(date +%s) - start_time > timeout )); then
            log "ERREUR: $container n'est pas healthy après ${timeout}s"
            docker compose logs "$container" >> "$LOG_FILE"
            return 1
        fi
        sleep 5
    done
}

# Valider un run (plus robuste)
validate_run() {
    local profile="$1"
    local result_files
    mapfile -t result_files < <(find "$RESULTS_DIR" -name "${profile}_${profile}_*.json" -type f)

    # Vérifier qu'il y a exactement un fichier résultat
    if [[ ${#result_files[@]} -eq 0 ]]; then
        log "ERREUR: Aucun fichier résultat trouvé pour $profile"
        return 1
    elif [[ ${#result_files[@]} -gt 1 ]]; then
        log "AVERTISSEMENT: Plusieurs fichiers résultats pour $profile: ${result_files[*]}"
        # Prendre le plus récent
        local latest_file
        latest_file=$(printf '%s\n' "${result_files[@]}" | xargs ls -t | head -n1)
        log "Utilisation du fichier le plus récent: $latest_file"
        result_files=("$latest_file")
    fi

    local result_file="${result_files[0]}"

    # Vérifier le nombre d'éléments (doit être > 0)
    local items
    items=$(grep -o '"items":[0-9]*' "$result_file" | cut -d: -f2 | head -n1)
    if [[ -z "$items" || "$items" -eq 0 ]]; then
        log "ERREUR: Nombre d'éléments invalide ($items) pour $profile"
        return 1
    fi

    log "Run $profile validé: $items éléments ingérés"
    return 0
}

# Nettoyer complètement
cleanup() {
    log "Nettoyage complet des conteneurs et volumes"
    docker compose down -v --remove-orphans 2>/dev/null || true
    sleep 5
}

# Générer les données
generate_data() {
    if [[ ! -f "dataset_gen/out/nodes.csv" ]]; then
        log "Génération des données (SCALE_MODE=$SCALE_MODE, SEED=$SEED)"
        python -m dataset_gen.run
    else
        log "Données déjà générées, skip"
    fi
}

# Exécuter un profil
run_profile() {
    local profile="$1"

    log "=== DÉBUT RUN $profile ==="

    # Nettoyage
    cleanup

    # Déterminer le service à démarrer
    local service_to_start
    case "$profile" in
        pg_rel|pg_jsonb)
            service_to_start="timescaledb"
            ;;
        memgraph)
            service_to_start="memgraph"
            ;;
        oxigraph)
            service_to_start="oxigraph"
            ;;
        *)
            log "ERREUR: Service inconnu pour $profile"
            return 1
            ;;
    esac

    # Démarrage du service spécifique
    log "Démarrage du conteneur $service_to_start pour $profile"
    if ! docker compose up -d "$service_to_start"; then
        log "ERREUR: Échec du démarrage de $service_to_start pour $profile"
        return 1
    fi

    # Attente santé
    local container_name
    case "$profile" in
        pg_rel|pg_jsonb)
            container_name="btb_timescaledb"
            ;;
        memgraph)
            container_name="btb_memgraph"
            ;;
        oxigraph)
            container_name="btb_oxigraph"
            ;;
    esac

    if ! wait_healthy "$container_name" "$HEALTH_CHECK_TIMEOUT"; then
        log "ERREUR: Santé non atteinte pour $profile"
        return 1
    fi

    # Exécution du benchmark
    log "Lancement du benchmark $profile"
    if ! python -m bench.runner "$profile"; then
        log "ERREUR: Échec du benchmark $profile"
        docker compose logs "$service_to_start" >> "$LOG_FILE"
        return 1
    fi

    # Validation
    if ! validate_run "$profile"; then
        return 1
    fi

    log "=== FIN RUN $profile ==="
    return 0
}

# Fonction principale
main() {
    local specific_profile="${1:-}"

    log "DÉBUT DE LA CAMPAGNE DE BENCHMARKS"
    log "Configuration: SCALE_MODE=$SCALE_MODE, SEED=$SEED"
    log "Profils: ${PROFILES[*]}"
    log "Log file: $LOG_FILE"

    # Préparation
    generate_data

    # Exécution
    local profiles_to_run=("${PROFILES[@]}")
    if [[ -n "$specific_profile" ]]; then
        if [[ " ${PROFILES[*]} " =~ " $specific_profile " ]]; then
            profiles_to_run=("$specific_profile")
        else
            log "ERREUR: Profil '$specific_profile' inconnu"
            exit 1
        fi
    fi

    local -A profile_statuses
    local failed_profiles=()

    for profile in "${profiles_to_run[@]}"; do
        if run_profile "$profile"; then
            profile_statuses["$profile"]="SUCCÈS"
            log "SUCCÈS: $profile terminé"
        else
            profile_statuses["$profile"]="ÉCHEC"
            failed_profiles+=("$profile")
            log "ÉCHEC: $profile a échoué"
        fi

        # Pause entre runs (sauf le dernier)
        if [[ "$profile" != "${profiles_to_run[-1]}" ]]; then
            log "Pause de ${PAUSE_BETWEEN_RUNS}s avant le prochain run"
            sleep "$PAUSE_BETWEEN_RUNS"
        fi
    done

    # Rapport final
    log "=== RAPPORT FINAL ==="
    local total_profiles=${#profiles_to_run[@]}
    local successful_profiles=$((total_profiles - ${#failed_profiles[@]}))
    log "Profils exécutés: $total_profiles"
    log "Profils réussis: $successful_profiles"
    log "Profils échoués: ${#failed_profiles[@]}"

    for profile in "${!profile_statuses[@]}"; do
        log "  $profile: ${profile_statuses[$profile]}"
    done

    if [[ ${#failed_profiles[@]} -eq 0 ]]; then
        log "CAMPAGNE TERMINÉE AVEC SUCCÈS"
        exit 0
    else
        log "CAMPAGNE TERMINÉE AVEC ÉCHECS: ${failed_profiles[*]}"
        exit 1
    fi
}

# Gestion des signaux pour cleanup
trap cleanup EXIT

main "$@"