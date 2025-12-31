.PHONY: help install build deploy reload clean test

# Configuration - can be overridden
VPS_HOST ?= user@your-vps.com
VPS_PATH ?= /var/www/thebuildmaestro
BUILD_DIR ?= build

help:
	@echo "Available targets:"
	@echo "  make install    - Install Python and Node dependencies"
	@echo "  make build      - Build static site to build/"
	@echo "  make deploy     - Deploy built site to VPS"
	@echo "  make reload     - Reload nginx on VPS"
	@echo "  make clean      - Remove build artifacts"
	@echo "  make test       - Test the Flask app locally"
	@echo ""
	@echo "Configuration (override with environment variables):"
	@echo "  VPS_HOST=$(VPS_HOST)"
	@echo "  VPS_PATH=$(VPS_PATH)"
	@echo "  BUILD_DIR=$(BUILD_DIR)"

install:
	@echo "Installing dependencies..."
	python3 -m venv venv || true
	. venv/bin/activate && \
		pip install --upgrade pip && \
		pip install -r requirements.txt
	npm install

build:
	@echo "Building static site..."
	./scripts/build.sh

deploy: build
	@echo "Deploying to VPS..."
	VPS_HOST=$(VPS_HOST) VPS_PATH=$(VPS_PATH) ./scripts/deploy.sh

reload:
	@echo "Reloading web server..."
	VPS_HOST=$(VPS_HOST) ./scripts/reload.sh

deploy-full: deploy reload
	@echo "Deployment complete!"

clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/ __pycache__/ *.pyc
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true

test:
	@echo "Testing Flask app..."
	. venv/bin/activate && python3 -c "from niski84 import app; print('✓ App loads successfully')"

