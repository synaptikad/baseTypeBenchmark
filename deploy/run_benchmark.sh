#!/bin/bash
# =============================================================================
# ONE-LINER BENCHMARK LAUNCHER
# =============================================================================
# Usage:
#   ./deploy/run_benchmark.sh [PHASE]
#
# Phases:
#   validate  - Quick validation (15 min)
#   small     - Full benchmark on small-1w (2-4h)
#   medium    - Full benchmark on medium-10w (4-8h)
#   large     - Full benchmark on large-100w (12-24h)
#   all       - Complete benchmark suite (24-48h)
#   publish   - Publish dataset to HuggingFace Hub
#
# Example:
#   ./deploy/run_benchmark.sh validate
#   ./deploy/run_benchmark.sh small
# =============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Activate venv if exists
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

# Load .env file if exists
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
    log "Loaded .env file"
fi

export PYTHONPATH="$PROJECT_DIR/src"

# =============================================================================
# FUNCTIONS
# =============================================================================

log() {
    echo -e "${BLUE}[$(date +%H:%M:%S)]${NC} $1"
}

success() {
    echo -e "${GREEN}✓${NC} $1"
}

warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

error() {
    echo -e "${RED}✗${NC} $1"
}

check_prerequisites() {
    log "Checking prerequisites..."

    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker not installed"
        exit 1
    fi

    # Check Docker images
    for img in "timescale/timescaledb-ha:pg16" "memgraph/memgraph:latest" "oxigraph/oxigraph:latest"; do
        if ! docker images --format '{{.Repository}}:{{.Tag}}' | grep -q "$img"; then
            warn "Docker image $img not found, pulling..."
            docker pull "$img"
        fi
    done

    # Check Python
    if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
        error "Python not installed"
        exit 1
    fi

    success "Prerequisites OK"
}

show_system_info() {
    echo ""
    echo "=============================================="
    echo "SYSTEM INFO"
    echo "=============================================="
    echo "RAM: $(free -h | awk '/^Mem:/{print $2}')"
    echo "CPUs: $(nproc)"
    echo "Disk: $(df -h . | awk 'NR==2{print $4}') available"
    echo ""
}

# =============================================================================
# BENCHMARK PHASES
# =============================================================================

phase_validate() {
    log "PHASE: VALIDATE (quick tests ~15 min)"
    echo ""

    # Launch interactive benchmark runner
    log "Launching interactive benchmark runner..."
    log "Select 'Generate Dataset' then 'Run Benchmark' with small-1w profile"
    python run.py

    success "Validation complete!"
}

phase_small() {
    log "PHASE: SMALL-1W (full benchmark ~2-4h)"
    echo ""

    log "Running benchmark on small-1w profile..."
    log "Use the interactive menu to:"
    log "  1. Generate Dataset (small-1w)"
    log "  2. Run Benchmark (all 6 scenarios: P1, P2, M1, M2, O1, O2)"
    python run.py

    success "Small benchmark complete! Results in data/results/"
}

phase_medium() {
    log "PHASE: MEDIUM (full benchmark ~4-8h)"
    echo ""

    log "Running benchmark on medium profile..."
    log "Use the interactive menu to:"
    log "  1. Generate Dataset (medium-1m)"
    log "  2. Run Benchmark (all 6 scenarios: P1, P2, M1, M2, O1, O2)"
    python run.py

    success "Medium benchmark complete! Results in data/results/"
}

phase_large() {
    log "PHASE: LARGE (full benchmark ~12-24h)"
    echo ""

    log "Running benchmark on large profile..."
    log "Use the interactive menu to:"
    log "  1. Generate Dataset (large-1m or large-1y)"
    log "  2. Run Benchmark (all 6 scenarios: P1, P2, M1, M2, O1, O2)"
    python run.py

    success "Large benchmark complete! Results in data/results/"
}

phase_all() {
    log "PHASE: ALL (complete benchmark suite ~24-48h)"
    echo ""

    log "For complete benchmark suite, use the interactive menu:"
    log "  1. Generate all datasets (small, medium, large)"
    log "  2. Run benchmarks on each profile"
    log ""
    log "Profiles available:"
    log "  - small-1w, small-1m, small-6m, small-1y"
    log "  - medium-1w, medium-1m, medium-6m, medium-1y"
    log "  - large-1w, large-1m, large-6m, large-1y"
    log ""
    log "Scenarios: P1, P2 (PostgreSQL), M1, M2 (Memgraph), O1, O2 (Oxigraph)"
    python run.py

    success "Complete benchmark suite finished!"
    log "Results saved in data/results/"
}

phase_publish() {
    log "PHASE: PUBLISH (dataset to HuggingFace Hub)"
    echo ""

    # Check HF_TOKEN
    if [ -z "$HF_TOKEN" ]; then
        error "HF_TOKEN not set!"
        echo ""
        echo "Configure your HuggingFace token:"
        echo "  export HF_TOKEN=hf_your_token_here"
        echo ""
        echo "Or add it to .env file:"
        echo "  echo 'HF_TOKEN=hf_your_token_here' >> .env"
        exit 1
    fi

    success "HF_TOKEN configured"

    log "Publishing dataset to HuggingFace..."
    log "Use the interactive menu option 'Publish Results'"
    python run.py

    success "Dataset published to HuggingFace!"
}

# =============================================================================
# MAIN
# =============================================================================

show_system_info
check_prerequisites

PHASE="${1:-validate}"

case "$PHASE" in
    validate)
        phase_validate
        ;;
    small)
        phase_small
        ;;
    medium)
        phase_medium
        ;;
    large)
        phase_large
        ;;
    all)
        phase_all
        ;;
    publish)
        phase_publish
        ;;
    *)
        echo "Usage: $0 [validate|small|medium|large|all|publish]"
        echo ""
        echo "Phases:"
        echo "  validate  - Quick validation (~15 min)"
        echo "  small     - Full benchmark on small-1w (~2-4h)"
        echo "  medium    - Full benchmark on medium-10w (~4-8h)"
        echo "  large     - Full benchmark on large-100w (~12-24h)"
        echo "  all       - Complete benchmark suite (~24-48h)"
        echo "  publish   - Publish dataset to HuggingFace Hub"
        exit 1
        ;;
esac
