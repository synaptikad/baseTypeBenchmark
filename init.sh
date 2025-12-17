#!/bin/bash
# BaseType Benchmark - Bootstrap Script
# Usage: curl -sLO https://raw.githubusercontent.com/synaptikad/baseTypeBenchmark/main/init.sh && bash init.sh

set -e

echo ""
echo "=============================================="
echo "  BaseType Benchmark - Initial Setup"
echo "=============================================="
echo ""
echo "This script will configure your machine for running"
echo "the BaseType database benchmark."
echo ""
echo "Requirements:"
echo "  - Ubuntu/Debian with sudo access"
echo "  - Recommended: 256 GB RAM, 32 vCPU, 500 GB storage"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "ERROR: Do not run this script as root."
    echo "Run as a regular user with sudo privileges."
    exit 1
fi

read -p "Press Enter to start installation, or Ctrl+C to abort..."

# Step 1: System packages
echo ""
echo "----------------------------------------------"
echo "[1/4] Installing system packages"
echo "----------------------------------------------"
echo ""
sudo apt update
sudo apt install -y make git curl docker.io docker-compose-v2 python3-pip python3-venv
echo ""
echo "[OK] System packages installed"

# Step 2: Docker permissions
echo ""
echo "----------------------------------------------"
echo "[2/4] Configuring Docker permissions"
echo "----------------------------------------------"
echo ""
if groups $USER | grep -q docker; then
    echo "User already in docker group"
else
    sudo usermod -aG docker $USER
    echo "Added $USER to docker group"
fi
echo ""
echo "[OK] Docker permissions configured"

# Step 3: Clone repository
echo ""
echo "----------------------------------------------"
echo "[3/4] Cloning repository"
echo "----------------------------------------------"
echo ""
cd ~
if [ -d "baseTypeBenchmark" ]; then
    echo "Directory ~/baseTypeBenchmark already exists."
    read -p "Remove and re-clone? [y/N] " reclone
    if [[ "$reclone" =~ ^[Yy] ]]; then
        rm -rf baseTypeBenchmark
        git clone https://github.com/synaptikad/baseTypeBenchmark.git
    else
        echo "Keeping existing directory"
        cd baseTypeBenchmark
        git pull origin main || true
    fi
else
    git clone https://github.com/synaptikad/baseTypeBenchmark.git
fi
echo ""
echo "[OK] Repository ready at ~/baseTypeBenchmark"

# Step 4: Python dependencies (with docker group)
echo ""
echo "----------------------------------------------"
echo "[4/4] Installing Python dependencies"
echo "----------------------------------------------"
echo ""

# Create continuation script for sg docker context
cat > /tmp/basetype_install.sh << 'INSTALL'
#!/bin/bash
set -e
cd ~/baseTypeBenchmark

echo "Creating Python virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

echo "Installing Python package..."
pip install --upgrade pip --quiet
pip install -e . --quiet
pip install -r requirements.txt --quiet

echo ""
echo "[OK] Python dependencies installed"

# Verify Docker access
echo ""
echo "Verifying Docker access..."
if docker info > /dev/null 2>&1; then
    echo "[OK] Docker is accessible"
else
    echo "[WARN] Docker not accessible yet - you may need to logout/login"
fi

# Verify Python package
echo ""
echo "Verifying Python package..."
python3 -c "import basetype_benchmark; print('[OK] basetype_benchmark package ready')" 2>/dev/null || echo "[WARN] Package import failed"

echo ""
echo "=============================================="
echo "  Setup complete"
echo "=============================================="
echo ""
echo "Next step: Run the benchmark workflow"
echo ""
echo "  cd ~/baseTypeBenchmark"
echo "  source .venv/bin/activate"
echo "  python3 run.py"
echo ""
echo "The workflow will guide you through:"
echo "  1. Dataset generation (choose profile size)"
echo "  2. Benchmark execution (starts required containers)"
echo "  3. Results publication to HuggingFace"
echo ""

read -p "Start the benchmark workflow now? [Y/n] " start_now
if [[ ! "$start_now" =~ ^[Nn] ]]; then
    cd ~/baseTypeBenchmark
    source .venv/bin/activate
    python3 run.py
fi
INSTALL
chmod +x /tmp/basetype_install.sh

echo "Applying Docker permissions and installing dependencies..."
sg docker -c "bash /tmp/basetype_install.sh"
