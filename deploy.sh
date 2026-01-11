#!/bin/bash
# Quick Deployment Script for CAIMF
# Supports: Docker, Local, Cloud

set -e

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║           CAIMF Quick Deployment Script                            ║"
echo "║           Child Aadhaar Inclusion Monitoring Framework             ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if Docker is installed
check_docker() {
    if command -v docker &> /dev/null; then
        echo "✓ Docker installed: $(docker --version)"
        return 0
    else
        echo "✗ Docker not installed. Please install Docker first."
        return 1
    fi
}

# Deploy with Docker Compose
deploy_docker() {
    echo ""
    echo "[1/4] Building Docker images..."
    docker-compose build

    echo ""
    echo "[2/4] Starting services..."
    docker-compose up -d

    echo ""
    echo "[3/4] Waiting for services to start..."
    sleep 5

    echo ""
    echo "[4/4] Verifying deployment..."
    docker-compose ps

    echo ""
    echo "✅ Deployment complete!"
    echo ""
    echo "Access your services:"
    echo "  📊 Dashboard: http://localhost:8501"
    echo "  📡 API: http://localhost:8000"
    echo "  📖 API Docs: http://localhost:8000/docs"
    echo ""
    echo "View logs:"
    echo "  docker-compose logs -f caimf-api"
    echo "  docker-compose logs -f caimf-dashboard"
    echo ""
    echo "Stop services:"
    echo "  docker-compose down"
}

# Deploy locally
deploy_local() {
    echo ""
    echo "[1/3] Checking virtual environment..."
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python -m venv venv
    fi

    echo "Activating virtual environment..."
    source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null

    echo ""
    echo "[2/3] Installing dependencies..."
    pip install -q -r requirements.txt

    echo ""
    echo "[3/3] Starting services..."
    echo ""
    echo "Terminal 1 - API Server:"
    echo "  python -m uvicorn caimf.api:app --reload --host 0.0.0.0 --port 8000"
    echo ""
    echo "Terminal 2 - Dashboard:"
    echo "  python -m streamlit run caimf/dashboard.py"
    echo ""
    echo "Or run the full pipeline:"
    echo "  python auto_load.py"
    echo ""
}

# Display menu
show_menu() {
    echo "Choose deployment method:"
    echo ""
    echo "  1. Docker Compose (Recommended)"
    echo "  2. Local Development"
    echo "  3. View Deployment Guide"
    echo "  4. Exit"
    echo ""
    read -p "Enter choice [1-4]: " choice
}

# Main
main() {
    while true; do
        show_menu

        case $choice in
            1)
                if check_docker; then
                    deploy_docker
                fi
                break
                ;;
            2)
                deploy_local
                break
                ;;
            3)
                if command -v less &> /dev/null; then
                    less DEPLOYMENT.md
                else
                    cat DEPLOYMENT.md
                fi
                break
                ;;
            4)
                echo "Exiting..."
                exit 0
                ;;
            *)
                echo "Invalid choice. Please try again."
                ;;
        esac
    done
}

main "$@"
