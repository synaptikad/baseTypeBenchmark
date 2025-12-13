#!/bin/bash
# =============================================================================
# Quick setup - À exécuter sur le VPS après première connexion SSH
# Usage: curl -fsSL https://raw.githubusercontent.com/synaptikad/baseTypeBenchmark/main/deploy/quick-setup.sh | bash
# =============================================================================

set -e

echo "=== Quick Setup baseTypeBenchmark ==="

# Installation minimale
apt-get update
apt-get install -y git curl

# Docker
curl -fsSL https://get.docker.com | bash

# Clone repo
cd /opt
git clone https://github.com/synaptikad/baseTypeBenchmark.git benchmark 2>/dev/null || (cd benchmark && git pull)
cd benchmark

# Dépendances Python
apt-get install -y python3 python3-pip
pip3 install --break-system-packages psycopg2-binary neo4j rdflib requests numpy Faker

# Permissions
chmod +x deploy/*.sh

echo ""
echo "=== Setup terminé ! ==="
echo ""
echo "Lancer le benchmark :"
echo "  cd /opt/benchmark"
echo "  ./deploy/run-benchmark.sh small"
echo ""
