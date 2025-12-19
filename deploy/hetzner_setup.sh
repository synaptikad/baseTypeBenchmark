#!/bin/bash
# =============================================================================
# HETZNER CCX63 SETUP SCRIPT - BaseType Benchmark
# =============================================================================
# Server: Hetzner CCX63 (48 vCPU AMD, 256GB RAM, 960GB NVMe)
# OS: Ubuntu 24.04
# Cost: ~0.952€/h
#
# Usage:
#   ssh root@<IP> 'bash -s' < deploy/hetzner_setup.sh
#   OR
#   scp deploy/hetzner_setup.sh root@<IP>:/root/ && ssh root@<IP> 'bash /root/hetzner_setup.sh'
# =============================================================================

set -e

echo "=============================================="
echo "🚀 HETZNER CCX63 SETUP - BaseType Benchmark"
echo "=============================================="

# =============================================================================
# 1. SYSTEM UPDATE & PACKAGES
# =============================================================================
echo ""
echo "📦 [1/6] System update & packages..."

apt update && apt upgrade -y

apt install -y \
    curl wget git htop tmux vim \
    python3 python3-pip python3-venv \
    docker.io docker-compose \
    build-essential

# Enable Docker
systemctl enable docker
systemctl start docker

# Python packages (global)
pip3 install --break-system-packages pandas numpy matplotlib seaborn jupyter

echo "✓ Packages installed"

# =============================================================================
# 2. CREATE BENCHMARK USER
# =============================================================================
echo ""
echo "👤 [2/6] Creating benchmark user..."

if ! id -u benchmark &>/dev/null; then
    useradd -m -s /bin/bash benchmark
    usermod -aG docker benchmark
    echo "benchmark ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
    echo "✓ User 'benchmark' created"
else
    echo "✓ User 'benchmark' already exists"
fi

# =============================================================================
# 3. CLONE REPOSITORY
# =============================================================================
echo ""
echo "📥 [3/6] Cloning repository..."

cd /home/benchmark

if [ ! -d "baseTypeBenchmark" ]; then
    sudo -u benchmark git clone https://github.com/YOUR_USERNAME/baseTypeBenchmark.git
    echo "✓ Repository cloned"
else
    cd baseTypeBenchmark
    sudo -u benchmark git pull
    echo "✓ Repository updated"
fi

cd /home/benchmark/baseTypeBenchmark

# =============================================================================
# 4. SETUP PYTHON ENVIRONMENT
# =============================================================================
echo ""
echo "🐍 [4/6] Setting up Python environment..."

sudo -u benchmark python3 -m venv /home/benchmark/baseTypeBenchmark/.venv
sudo -u benchmark /home/benchmark/baseTypeBenchmark/.venv/bin/pip install --upgrade pip

# Install project dependencies
if [ -f "requirements.txt" ]; then
    sudo -u benchmark /home/benchmark/baseTypeBenchmark/.venv/bin/pip install -r requirements.txt
fi

# Install project in editable mode
sudo -u benchmark /home/benchmark/baseTypeBenchmark/.venv/bin/pip install -e .

echo "✓ Python environment ready"

# =============================================================================
# 5. PULL DOCKER IMAGES
# =============================================================================
echo ""
echo "🐳 [5/6] Pulling Docker images (this may take a while)..."

docker pull timescale/timescaledb-ha:pg16
docker pull memgraph/memgraph:latest
docker pull oxigraph/oxigraph:latest

echo "✓ Docker images pulled"

# =============================================================================
# 6. GENERATE DATASETS
# =============================================================================
echo ""
echo "📊 [6/6] Generating datasets..."

cd /home/benchmark/baseTypeBenchmark

# Ready for interactive benchmark
sudo -u benchmark bash -c '
source .venv/bin/activate
export PYTHONPATH=/home/benchmark/baseTypeBenchmark/src

echo "  Setup complete. Use run.py to generate datasets and run benchmarks."
echo "  Example: python run.py"
'

echo "Setup complete - use run.py for dataset generation"

# =============================================================================
# SUMMARY
# =============================================================================
echo ""
echo "=============================================="
echo "✅ SETUP COMPLETE!"
echo "=============================================="
echo ""
echo "Server specs:"
echo "  - RAM: $(free -h | awk '/^Mem:/{print $2}')"
echo "  - CPUs: $(nproc)"
echo "  - Disk: $(df -h / | awk 'NR==2{print $2}')"
echo ""
echo "Next steps:"
echo "  1. ssh benchmark@<IP>"
echo "  2. cd baseTypeBenchmark"
echo "  3. source .venv/bin/activate"
echo "  4. See HETZNER_GUIDE.md for benchmark commands"
echo ""
echo "Quick start:"
echo "  python run.py"
echo ""
