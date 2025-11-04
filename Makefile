# HEX Automation Hub Makefile

# Variables
PYTHON := python3
PIP := pip3
DOCKER := docker
DOCKER_COMPOSE := docker-compose
TEST_DIR := tests
SRC_DIR := automation

# Default target
.PHONY: help
help:
	@echo "HEX Automation Hub - Makefile"
	@echo ""
	@echo "Usage:"
	@echo "  make install        Install dependencies"
	@echo "  make test           Run all tests"
	@echo "  make test-unit      Run unit tests"
	@echo "  make lint           Run code linting"
	@echo "  make clean          Clean temporary files"
	@echo "  make docker-build   Build Docker image"
	@echo "  make docker-run     Run Docker container"
	@echo "  make deploy         Deploy using docker-compose"
	@echo "  make stop           Stop docker-compose services"
	@echo "  make logs           Show docker-compose logs"

# Install dependencies
.PHONY: install
install:
	$(PIP) install -r requirements.txt
	$(PYTHON) -m playwright install-deps
	$(PYTHON) -m playwright install chromium

# Run all tests
.PHONY: test
test: test-unit

# Run unit tests
.PHONY: test-unit
test-unit:
	$(PYTHON) -m pytest $(TEST_DIR)/ -v

# Run specific module tests
.PHONY: test-web-scraper
test-web-scraper:
	$(PYTHON) -m pytest $(TEST_DIR)/test_web_scraper.py -v

.PHONY: test-api
test-api:
	$(PYTHON) -m pytest $(TEST_DIR)/test_api_automation.py -v

.PHONY: test-browser
test-browser:
	$(PYTHON) -m pytest $(TEST_DIR)/test_browser.py -v

.PHONY: test-rpa
test-rpa:
	$(PYTHON) -m pytest $(TEST_DIR)/test_rpa.py -v

.PHONY: test-social
test-social:
	$(PYTHON) -m pytest $(TEST_DIR)/test_social_bots.py -v

# Run code linting
.PHONY: lint
lint:
	$(PIP) install flake8
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

# Clean temporary files
.PHONY: clean
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf *.log
	rm -rf screenshots/
	rm -rf data/
	rm -rf logs/

# Docker commands
.PHONY: docker-build
docker-build:
	$(DOCKER) build -t hex-automation-hub .

.PHONY: docker-run
docker-run:
	$(DOCKER) run --rm -it hex-automation-hub

# Docker Compose commands
.PHONY: deploy
deploy:
	$(DOCKER_COMPOSE) up -d

.PHONY: stop
stop:
	$(DOCKER_COMPOSE) down

.PHONY: logs
logs:
	$(DOCKER_COMPOSE) logs -f

.PHONY: status
status:
	$(DOCKER_COMPOSE) ps