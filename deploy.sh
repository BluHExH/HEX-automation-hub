#!/bin/bash

# HEX Automation Hub Deployment Script

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_warning "Running as root. It's recommended to run this script as a regular user."
fi

# Check dependencies
check_dependencies() {
    print_status "Checking dependencies..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "docker-compose is not installed. Please install docker-compose first."
        exit 1
    fi
    
    print_status "All dependencies are installed."
}

# Deploy the application
deploy() {
    print_status "Starting deployment..."
    
    # Pull latest images
    print_status "Pulling latest Docker images..."
    docker-compose pull
    
    # Build images
    print_status "Building Docker images..."
    docker-compose build
    
    # Create necessary directories
    print_status "Creating data and logs directories..."
    mkdir -p data logs
    
    # Copy config if it doesn't exist
    if [ ! -f config.json ]; then
        print_status "Creating default config from example..."
        cp config_example.json config.json
    fi
    
    # Start services
    print_status "Starting services..."
    docker-compose up -d
    
    # Show status
    print_status "Deployment completed!"
    docker-compose ps
}

# Stop the application
stop() {
    print_status "Stopping services..."
    docker-compose down
    print_status "Services stopped."
}

# Show logs
logs() {
    print_status "Showing logs..."
    docker-compose logs -f
}

# Show status
status() {
    print_status "Current status:"
    docker-compose ps
}

# Main script logic
case "$1" in
    deploy)
        check_dependencies
        deploy
        ;;
    stop)
        stop
        ;;
    logs)
        logs
        ;;
    status)
        status
        ;;
    *)
        echo "HEX Automation Hub Deployment Script"
        echo "Usage: $0 {deploy|stop|logs|status}"
        echo ""
        echo "Commands:"
        echo "  deploy  - Deploy the application"
        echo "  stop    - Stop the application"
        echo "  logs    - Show application logs"
        echo "  status  - Show application status"
        exit 1
        ;;
esac