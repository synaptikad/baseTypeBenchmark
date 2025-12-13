#!/bin/bash
# =============================================================================
# Setup VPS OVH pour baseTypeBenchmark
# Compatible: Ubuntu 22.04 / Debian 12
# Usage: curl -fsSL <url> | sudo bash
# =============================================================================

set -e

echo "=========================================="
echo "  Setup VPS pour baseTypeBenchmark"
echo "=========================================="

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Vérifier root
if [ "$EUID" -ne 0 ]; then
    log_error "Ce script doit être exécuté en root (sudo)"
    exit 1
fi

# Mise à jour système
log_info "Mise à jour du système..."
apt-get update && apt-get upgrade -y

# Installation des dépendances de base
log_info "Installation des dépendances..."
apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    git \
    htop \
    python3 \
    python3-pip \
    python3-venv

# Installation Docker
log_info "Installation de Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | bash
    systemctl enable docker
    systemctl start docker
    log_info "Docker installé avec succès"
else
    log_info "Docker déjà installé"
fi

# Ajouter l'utilisateur courant au groupe docker (si non-root)
if [ -n "$SUDO_USER" ]; then
    usermod -aG docker "$SUDO_USER"
    log_info "Utilisateur $SUDO_USER ajouté au groupe docker"
fi

# Vérification Docker Compose (inclus dans Docker récent)
log_info "Vérification Docker Compose..."
docker compose version

# Installation des dépendances Python
log_info "Installation des dépendances Python..."
pip3 install --break-system-packages \
    psycopg2-binary \
    neo4j \
    rdflib \
    requests \
    numpy \
    Faker

# Créer répertoire de travail
WORK_DIR="/opt/benchmark"
log_info "Création du répertoire de travail: $WORK_DIR"
mkdir -p "$WORK_DIR"

# Afficher les versions
echo ""
echo "=========================================="
echo "  Installation terminée !"
echo "=========================================="
echo ""
docker --version
docker compose version
python3 --version
echo ""
log_info "Prochaine étape: cloner le repo et lancer deploy.sh"
echo ""
echo "  cd /opt/benchmark"
echo "  git clone https://github.com/synaptikad/baseTypeBenchmark.git ."
echo "  chmod +x deploy/*.sh"
echo "  ./deploy/run-benchmark.sh small"
echo ""
