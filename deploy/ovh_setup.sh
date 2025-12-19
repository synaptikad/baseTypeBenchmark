#!/bin/bash
# =============================================================================
# Script de déploiement BaseType Benchmark sur OVH B3-256
# =============================================================================
# Usage: ./ovh_setup.sh
#
# Prérequis:
#   - Instance OVH B3-256 (256GB RAM, 8 vCPUs)
#   - Ubuntu 22.04 LTS
#   - Accès SSH root
#
# Ce script:
#   1. Met à jour le système
#   2. Installe Docker et Docker Compose
#   3. Installe Python 3.11 et dépendances
#   4. Clone le repository
#   5. Prépare l'environnement de benchmark
# =============================================================================

set -e  # Exit on error

echo "=============================================="
echo "🚀 BaseType Benchmark - OVH B3-256 Setup"
echo "=============================================="
echo ""

# Variables
REPO_URL="https://github.com/synaptikad/baseTypeBenchmark.git"
INSTALL_DIR="/opt/basetype-benchmark"
DATA_DIR="/data/benchmark"

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# =============================================================================
# 1. Vérification système
# =============================================================================
log_info "Vérification du système..."

# Vérifier RAM
TOTAL_RAM_GB=$(free -g | awk '/^Mem:/{print $2}')
if [ "$TOTAL_RAM_GB" -lt 200 ]; then
    log_warn "RAM détectée: ${TOTAL_RAM_GB}GB (recommandé: 256GB)"
else
    log_success "RAM: ${TOTAL_RAM_GB}GB"
fi

# Vérifier espace disque
DISK_FREE_GB=$(df -BG / | awk 'NR==2 {print $4}' | tr -d 'G')
if [ "$DISK_FREE_GB" -lt 300 ]; then
    log_warn "Espace disque: ${DISK_FREE_GB}GB (recommandé: 400GB)"
else
    log_success "Espace disque: ${DISK_FREE_GB}GB"
fi

# =============================================================================
# 2. Mise à jour système
# =============================================================================
log_info "Mise à jour du système..."
apt-get update -qq
apt-get upgrade -y -qq
log_success "Système à jour"

# =============================================================================
# 3. Installation Docker
# =============================================================================
log_info "Installation de Docker..."

if command -v docker &> /dev/null; then
    log_success "Docker déjà installé: $(docker --version)"
else
    # Installation Docker officielle
    apt-get install -y -qq \
        ca-certificates \
        curl \
        gnupg \
        lsb-release

    mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg

    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

    apt-get update -qq
    apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-compose-plugin

    # Démarrer Docker
    systemctl start docker
    systemctl enable docker

    log_success "Docker installé: $(docker --version)"
fi

# =============================================================================
# 4. Installation Python 3.11
# =============================================================================
log_info "Installation de Python 3.11..."

if python3.11 --version &> /dev/null; then
    log_success "Python 3.11 déjà installé"
else
    apt-get install -y -qq software-properties-common
    add-apt-repository -y ppa:deadsnakes/ppa
    apt-get update -qq
    apt-get install -y -qq python3.11 python3.11-venv python3.11-dev python3-pip
    log_success "Python 3.11 installé"
fi

# =============================================================================
# 5. Clone du repository
# =============================================================================
log_info "Clone du repository..."

if [ -d "$INSTALL_DIR" ]; then
    log_warn "Répertoire existant, mise à jour..."
    cd "$INSTALL_DIR"
    git pull
else
    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

log_success "Repository cloné dans $INSTALL_DIR"

# =============================================================================
# 6. Création environnement Python
# =============================================================================
log_info "Configuration environnement Python..."

cd "$INSTALL_DIR"
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip -q
pip install -e . -q
pip install -r requirements.txt -q

log_success "Environnement Python configuré"

# =============================================================================
# 7. Création répertoires de données
# =============================================================================
log_info "Création des répertoires de données..."

mkdir -p "$DATA_DIR"/{cache,exports,results}
ln -sf "$DATA_DIR" "$INSTALL_DIR/data"

log_success "Répertoires créés: $DATA_DIR"

# =============================================================================
# 8. Configuration Docker Compose
# =============================================================================
log_info "Préparation Docker Compose..."

cd "$INSTALL_DIR"
if [ -f "docker/docker-compose.yml" ]; then
    docker compose -f docker/docker-compose.yml pull
    log_success "Images Docker téléchargées"
else
    log_warn "docker-compose.yml non trouvé"
fi

# =============================================================================
# 9. Vérification finale
# =============================================================================
echo ""
echo "=============================================="
echo "✅ Installation terminée!"
echo "=============================================="
echo ""
echo "📊 Spécifications détectées:"
echo "   RAM: ${TOTAL_RAM_GB}GB"
echo "   Disk: ${DISK_FREE_GB}GB libre"
echo "   Docker: $(docker --version | cut -d' ' -f3)"
echo "   Python: $(python3.11 --version)"
echo ""
echo "📁 Répertoires:"
echo "   Code: $INSTALL_DIR"
echo "   Data: $DATA_DIR"
echo ""
echo "Pour lancer les benchmarks:"
echo "   cd $INSTALL_DIR"
echo "   source venv/bin/activate"
echo "   python run.py"
echo ""
echo "💡 Profils disponibles avec 256GB RAM:"
echo "   ✅ 12 profils × 3 paradigmes = 36 benchmarks"
echo "   ✅ Inclut large-1m, large-6m, large-1y"
echo ""
echo "⏱️  Durée estimée suite complète: 8-12 heures"
echo ""
