#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
# AWS EC2 Setup Script — Fake News Detector
# ═══════════════════════════════════════════════════════════════════
# Tested on: Amazon Linux 2023 / Ubuntu 22.04
# Instance: t2.medium (2 vCPU, 4GB RAM) or larger
#
# Usage:
#   chmod +x setup_ec2.sh
#   sudo ./setup_ec2.sh
# ═══════════════════════════════════════════════════════════════════

set -euo pipefail

echo "═══════════════════════════════════════════════════════════"
echo "  Fake News Detector — EC2 Setup"
echo "═══════════════════════════════════════════════════════════"

# ── 1. System Updates ────────────────────────────────────────────
echo "[1/6] Updating system packages..."
if command -v dnf &> /dev/null; then
    # Amazon Linux 2023
    sudo dnf update -y
    sudo dnf install -y git
elif command -v apt-get &> /dev/null; then
    # Ubuntu
    sudo apt-get update -y
    sudo apt-get upgrade -y
    sudo apt-get install -y git curl
fi

# ── 2. Install Docker ───────────────────────────────────────────
echo "[2/6] Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sh
    sudo systemctl enable docker
    sudo systemctl start docker
    sudo usermod -aG docker $USER
    echo "Docker installed successfully."
else
    echo "Docker already installed."
fi

# ── 3. Install Docker Compose ───────────────────────────────────
echo "[3/6] Installing Docker Compose..."
if ! command -v docker compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
        -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "Docker Compose installed."
else
    echo "Docker Compose already installed."
fi

# ── 4. Clone Repository ─────────────────────────────────────────
echo "[4/6] Cloning repository..."
APP_DIR="/opt/fake-news-detector"

if [ ! -d "$APP_DIR" ]; then
    # Replace with your actual repo URL
    sudo git clone https://github.com/<your-username>/fake-news-detection.git "$APP_DIR"
else
    echo "Repository already exists. Pulling latest..."
    cd "$APP_DIR" && sudo git pull origin main
fi

cd "$APP_DIR"

# ── 5. Configure Environment ────────────────────────────────────
echo "[5/6] Setting up environment..."
if [ ! -f .env ]; then
    sudo cp .env.example .env
    # Generate a random secret key
    SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))" 2>/dev/null || openssl rand -base64 32)
    sudo sed -i "s/change-me-to-a-random-string/$SECRET/" .env
    echo "Created .env file. IMPORTANT: Edit .env to set your NEWS_API_KEY and admin credentials."
else
    echo ".env already exists."
fi

# ── 6. Build and Run ────────────────────────────────────────────
echo "[6/6] Building and starting Docker containers..."
sudo docker compose up -d --build

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  ✅ Setup Complete!"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "  App URL:  http://$(curl -s ifconfig.me):8501"
echo "  Status:   sudo docker compose ps"
echo "  Logs:     sudo docker compose logs -f"
echo "  Stop:     sudo docker compose down"
echo "  Restart:  sudo docker compose restart"
echo ""
echo "  IMPORTANT: Open port 8501 in your EC2 Security Group!"
echo ""
echo "  Default admin credentials (change in .env):"
echo "    Username: admin"
echo "    Password: admin123"
echo ""
