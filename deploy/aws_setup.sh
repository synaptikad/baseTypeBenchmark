#!/bin/bash
# =============================================================================
# AWS EC2 m8g.16xlarge SETUP SCRIPT - BaseType Benchmark
# =============================================================================
# Instance: m8g.16xlarge (64 vCPU Graviton4, 256GB RAM, EBS storage)
# OS: Ubuntu 24.04 LTS (ARM64)
# Cost: ~$2.74/h (eu-west-1)
#
# Why Graviton4 (ARM64)?
#   - 30-40% better energy efficiency vs x86
#   - Representative of modern cloud deployments
#   - Native ARM support for PostgreSQL, Memgraph, Oxigraph
#
# Note: This instance uses EBS storage (no local NVMe).
#       Configure a large gp3 volume (500GB+) for best performance.
#
# Usage:
#   curl -sSL https://raw.githubusercontent.com/synaptikad/baseTypeBenchmark/main/deploy/aws_setup.sh | sudo bash
# =============================================================================

set -e

echo "=============================================="
echo "AWS EC2 SETUP - BaseType Benchmark"
echo "=============================================="

# =============================================================================
# 1. SYSTEM UPDATE & PACKAGES
# =============================================================================
echo ""
echo "[1/7] System update & packages..."

apt update && apt upgrade -y

apt install -y \
    curl wget git htop tmux vim \
    python3 python3-pip python3-venv \
    docker.io docker-compose \
    build-essential nvme-cli

# Enable Docker
systemctl enable docker
systemctl start docker
# Detect user (admin for Debian, ubuntu for Ubuntu)
MAIN_USER=$(ls /home | head -1)
usermod -aG docker $MAIN_USER

echo "Packages installed"

# =============================================================================
# 2. SETUP DATA DIRECTORY
# =============================================================================
echo ""
echo "[2/7] Setting up data directory..."

# For m8g (EBS only), use /data on root volume or attached EBS
# For instances with NVMe, mount them
NVME_DEVICES=$(lsblk -d -n -o NAME,TYPE | grep nvme | grep -v nvme0 | awk '{print $1}' || true)

if [ -n "$NVME_DEVICES" ]; then
    echo "  NVMe drives detected, mounting..."
    MOUNT_INDEX=1
    for DEVICE in $NVME_DEVICES; do
        MOUNT_POINT="/data/nvme${MOUNT_INDEX}"
        echo "  Formatting /dev/${DEVICE}..."
        mkfs.ext4 -F /dev/${DEVICE}
        mkdir -p ${MOUNT_POINT}
        mount /dev/${DEVICE} ${MOUNT_POINT}
        echo "/dev/${DEVICE} ${MOUNT_POINT} ext4 defaults,nofail 0 2" >> /etc/fstab
        chown $MAIN_USER:$MAIN_USER ${MOUNT_POINT}
        MOUNT_INDEX=$((MOUNT_INDEX + 1))
    done
    DATA_DIR="/data/nvme1"
else
    echo "  No NVMe drives (EBS instance), using /data on root volume..."
    mkdir -p /data
    chown $MAIN_USER:$MAIN_USER /data
    DATA_DIR="/data"
fi

echo "Data directory: $DATA_DIR"
df -h $DATA_DIR

# =============================================================================
# 3. CONFIGURE DOCKER
# =============================================================================
echo ""
echo "[3/7] Configuring Docker..."

systemctl stop docker
mkdir -p $DATA_DIR/docker
if [ -d /var/lib/docker ]; then
    mv /var/lib/docker/* $DATA_DIR/docker/ 2>/dev/null || true
fi

cat > /etc/docker/daemon.json <<EOF
{
    "data-root": "$DATA_DIR/docker"
}
EOF

systemctl start docker
echo "Docker configured (data: $DATA_DIR/docker)"

# =============================================================================
# 4. CLONE REPOSITORY
# =============================================================================
echo ""
echo "[4/7] Cloning repository..."

cd $DATA_DIR

if [ ! -d "baseTypeBenchmark" ]; then
    sudo -u $MAIN_USER git clone https://github.com/synaptikad/baseTypeBenchmark.git
    echo "Repository cloned"
else
    cd baseTypeBenchmark
    sudo -u $MAIN_USER git pull
    echo "Repository updated"
fi

# =============================================================================
# 5. SETUP PYTHON ENVIRONMENT
# =============================================================================
echo ""
echo "[5/7] Setting up Python environment..."

cd $DATA_DIR/baseTypeBenchmark

sudo -u $MAIN_USER python3 -m venv .venv
sudo -u $MAIN_USER .venv/bin/pip install --upgrade pip

# Install project and all dependencies (including HuggingFace)
sudo -u $MAIN_USER .venv/bin/pip install -e .
sudo -u $MAIN_USER .venv/bin/pip install -r requirements.txt

echo "Python environment ready"

# =============================================================================
# 6. PULL DOCKER IMAGES
# =============================================================================
echo ""
echo "[6/7] Pulling Docker images..."

docker pull timescale/timescaledb-ha:pg16
docker pull memgraph/memgraph:latest
docker pull oxigraph/oxigraph:latest

echo "Docker images pulled"

# =============================================================================
# 7. GENERATE DATASETS
# =============================================================================
echo ""
echo "[7/7] Generating datasets..."

cd $DATA_DIR/baseTypeBenchmark

sudo -u $MAIN_USER DATA_DIR=$DATA_DIR bash -c '
source .venv/bin/activate
export PYTHONPATH=$DATA_DIR/baseTypeBenchmark/src

echo "  Generating small-1w..."
python -c "
from basetype_benchmark.data_generator.graph_builder import BuildingGraphGenerator
g = BuildingGraphGenerator()
g.generate_from_profile(\"small-1w\")
g.export_all(\"data/small-1w\")
" 2>/dev/null || echo "  small-1w generation skipped or failed"

echo "  Dataset generation complete"
'

# =============================================================================
# SUMMARY
# =============================================================================
echo ""
echo "=============================================="
echo "SETUP COMPLETE!"
echo "=============================================="
echo ""
echo "Server specs:"
echo "  - RAM: $(free -h | awk '/^Mem:/{print $2}')"
echo "  - CPUs: $(nproc)"
echo "  - Storage: $(df -h $DATA_DIR | awk 'NR==2{print $2}')"
echo ""
echo "Data directory: $DATA_DIR"
echo ""
echo "Next steps:"
echo "  1. Reconnect SSH (for Docker group):"
echo "     exit"
echo "     ssh -i ~/.ssh/btb-benchmark.pem ubuntu@<IP>"
echo ""
echo "  2. Run benchmarks:"
echo "     cd $DATA_DIR/baseTypeBenchmark"
echo "     source .venv/bin/activate"
echo "     ./deploy/run_benchmark.sh validate"
echo ""
echo "  3. Configure HuggingFace token (for dataset publication):"
echo "     echo 'export HF_TOKEN=hf_your_token_here' >> ~/.bashrc"
echo "     source ~/.bashrc"
echo ""
echo "  4. Publish dataset to HuggingFace:"
echo "     make hf-publish"
echo ""
echo "IMPORTANT: Don't forget to STOP the instance when done!"
echo "           Cost: ~\$2.74/hour (m8g.16xlarge Graviton4)"
echo ""
