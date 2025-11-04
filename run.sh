#!/bin/bash

# HEX Automation Hub Runner Script
# Works on Termux and regular Linux systems

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

# Detect platform
detect_platform() {
    if [ -d "/data/data/com.termux" ]; then
        PLATFORM="termux"
        print_status "Detected Termux platform"
    else
        PLATFORM="linux"
        print_status "Detected Linux platform"
    fi
}

# Check if running in Termux
is_termux() {
    [ "$PLATFORM" = "termux" ]
}

# Install dependencies
install_dependencies() {
    print_status "Installing dependencies..."
    
    if is_termux; then
        # Termux specific installation
        pkg update -y
        pkg install -y python python-pip git chromium
    else
        # Regular Linux installation
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y python3 python3-pip git chromium-browser
        elif command -v yum &> /dev/null; then
            sudo yum install -y python3 python3-pip git chromium
        elif command -v pacman &> /dev/null; then
            sudo pacman -Syu python python-pip git chromium
        else
            print_error "Unsupported package manager. Please install dependencies manually."
            exit 1
        fi
    fi
    
    # Install Python dependencies
    pip3 install -r requirements.txt
    
    # Install Playwright browsers
    print_status "Installing Playwright browsers..."
    python3 -m playwright install-deps
    python3 -m playwright install chromium
    
    print_status "Dependencies installed successfully."
}

# Run the application
run_app() {
    if [ $# -eq 0 ]; then
        print_error "No arguments provided. Please specify target and options."
        echo "Usage: $0 run --target <target> [--config <config>] [--once] [--daemon] [--dry-run]"
        exit 1
    fi
    
    print_status "Running HEX Automation Hub..."
    python3 cli.py "$@"
}

# Main script logic
main() {
    detect_platform
    
    case "$1" in
        install)
            install_dependencies
            ;;
        run)
            shift
            run_app "$@"
            ;;
        *)
            echo "HEX Automation Hub Runner Script"
            echo "Usage: $0 {install|run}"
            echo ""
            echo "Commands:"
            echo "  install  - Install dependencies"
            echo "  run      - Run the application with specified arguments"
            echo ""
            echo "Example:"
            echo "  $0 install"
            echo "  $0 run --target web_scraper --config config.json --once"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"