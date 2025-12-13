#!/bin/bash
# =============================================================================
# Script principal pour lancer le benchmark complet
# Usage: ./run-benchmark.sh [small|large|enterprise]
#
# Profils disponibles:
#   small      - 15k points, 3k équipements   (RAM: 4 Go min)
#   large      - 50k points, 8k équipements   (RAM: 8 Go min)
#   enterprise - 500k points, 100k équipements (RAM: 32 Go min)
#
# Alias: laptop=small, server=large, prod=enterprise, worst=enterprise
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

# Profil par défaut
SCALE_MODE="${1:-small}"
SEED="${2:-42}"

# Vérification RAM pour enterprise
if [ "$SCALE_MODE" = "enterprise" ] || [ "$SCALE_MODE" = "prod" ] || [ "$SCALE_MODE" = "worst" ]; then
    TOTAL_RAM_GB=$(free -g | awk '/^Mem:/{print $2}')
    if [ "$TOTAL_RAM_GB" -lt 24 ]; then
        echo "ATTENTION: Profil enterprise requiert 32 Go RAM minimum"
        echo "RAM détectée: ${TOTAL_RAM_GB} Go"
        echo "Continuer quand même ? (y/N)"
        read -r confirm
        if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
            exit 1
        fi
    fi
fi

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${BLUE}[STEP]${NC} $1"; }

echo "=========================================="
echo "  baseTypeBenchmark - Profil: $SCALE_MODE"
echo "=========================================="
echo ""

# 1. Vérifier l'environnement
log_step "1/6 - Vérification de l'environnement..."
docker --version || { log_error "Docker non installé"; exit 1; }
docker compose version || { log_error "Docker Compose non disponible"; exit 1; }
python3 --version || { log_error "Python3 non installé"; exit 1; }
log_info "Environnement OK"

# 2. Configurer .env
log_step "2/6 - Configuration de l'environnement..."
if [ ! -f .env ]; then
    cp .env.example .env
    log_info "Fichier .env créé"
else
    log_info "Fichier .env existe déjà"
fi

# 3. Démarrer les services Docker
log_step "3/6 - Démarrage des services Docker..."
docker compose down 2>/dev/null || true
docker compose up -d

# Attendre que les services soient healthy
log_info "Attente des services (peut prendre 30-60s)..."
SERVICES=("btb_timescaledb" "btb_memgraph" "btb_oxigraph")
MAX_WAIT=120
WAIT_INTERVAL=5

for service in "${SERVICES[@]}"; do
    elapsed=0
    while [ $elapsed -lt $MAX_WAIT ]; do
        status=$(docker inspect --format='{{.State.Health.Status}}' "$service" 2>/dev/null || echo "not_found")
        if [ "$status" = "healthy" ]; then
            log_info "$service: healthy"
            break
        elif [ "$status" = "not_found" ]; then
            log_warn "$service: non trouvé, skip"
            break
        fi
        sleep $WAIT_INTERVAL
        elapsed=$((elapsed + WAIT_INTERVAL))
        echo -n "."
    done
    if [ $elapsed -ge $MAX_WAIT ] && [ "$status" != "healthy" ]; then
        log_warn "$service: timeout (status=$status)"
    fi
done
echo ""

# Afficher l'état des services
docker compose ps

# 4. Générer le dataset
log_step "4/6 - Génération du dataset (SCALE_MODE=$SCALE_MODE, SEED=$SEED)..."
SCALE_MODE="$SCALE_MODE" SEED="$SEED" python3 -m dataset_gen.run

# 5. Exécuter les benchmarks
log_step "5/6 - Exécution des benchmarks..."

ENGINES=("pg_rel" "pg_jsonb" "memgraph" "oxigraph")
RESULTS_DIR="$PROJECT_DIR/bench/results"
mkdir -p "$RESULTS_DIR"

# Fichier de log des erreurs
ERROR_LOG="$RESULTS_DIR/errors.log"
> "$ERROR_LOG"

for engine in "${ENGINES[@]}"; do
    echo ""
    log_info "Benchmark: $engine"
    echo "----------------------------------------"
    if python3 -m bench.runner "$engine" 2>&1; then
        log_info "$engine: OK"
    else
        log_error "$engine: ERREUR (voir $ERROR_LOG)"
        echo "[$engine] $(date): Benchmark failed" >> "$ERROR_LOG"
    fi
done

# 6. Afficher les résultats
log_step "6/6 - Résultats du benchmark..."
echo ""
echo "=========================================="
echo "  RÉSULTATS COMPARATIFS"
echo "=========================================="
echo ""

# Lister les fichiers de résultats
if ls "$RESULTS_DIR"/*.json 1>/dev/null 2>&1; then
    log_info "Fichiers de résultats générés:"
    ls -la "$RESULTS_DIR"/*.json
    echo ""

    # Afficher un résumé si Python peut le faire
    python3 << 'PYTHON_SCRIPT'
import json
import os
from pathlib import Path

results_dir = Path("bench/results")
results = {}

for f in results_dir.glob("*.json"):
    try:
        with open(f) as fp:
            data = json.load(fp)
            engine = f.stem
            results[engine] = data
    except Exception as e:
        print(f"Erreur lecture {f}: {e}")

if results:
    print(f"{'Engine':<12} {'p50 (ms)':<12} {'p95 (ms)':<12} {'RAM (MB)':<12} {'Disk (MB)':<12}")
    print("-" * 60)
    for engine, data in sorted(results.items()):
        p50 = data.get('latency_p50_ms', 'N/A')
        p95 = data.get('latency_p95_ms', 'N/A')
        ram = data.get('ram_mb', 'N/A')
        disk = data.get('disk_mb', 'N/A')

        p50_str = f"{p50:.2f}" if isinstance(p50, (int, float)) else str(p50)
        p95_str = f"{p95:.2f}" if isinstance(p95, (int, float)) else str(p95)
        ram_str = f"{ram:.1f}" if isinstance(ram, (int, float)) else str(ram)
        disk_str = f"{disk:.1f}" if isinstance(disk, (int, float)) else str(disk)

        print(f"{engine:<12} {p50_str:<12} {p95_str:<12} {ram_str:<12} {disk_str:<12}")
else:
    print("Aucun résultat trouvé")
PYTHON_SCRIPT
else
    log_warn "Aucun fichier de résultats trouvé"
fi

echo ""
echo "=========================================="
echo "  Benchmark terminé !"
echo "=========================================="
echo ""
log_info "Résultats disponibles dans: $RESULTS_DIR"
log_info "Pour arrêter les services: docker compose down"
echo ""
