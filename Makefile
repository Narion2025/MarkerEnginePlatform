.PHONY: help build test dev clean lint format

# Default target
help:
	@echo "Marker Engine - Verfügbare Befehle:"
	@echo ""
	@echo "  make build       - Baut das Docker Runtime Image"
	@echo "  make test        - Führt Tests im Docker Container aus"
	@echo "  make dev         - Startet Development Environment"
	@echo "  make clean       - Entfernt Docker Images und Cache"
	@echo "  make lint        - Führt Code-Linting aus"
	@echo "  make format      - Formatiert Python Code"
	@echo ""

# Docker Build
build:
	@echo "🔨 Building Docker Runtime Image..."
	docker build . --target runtime -t marker-engine:latest

# Tests ausführen
test: build
	@echo "🧪 Running Tests..."
	docker run --rm marker-engine:latest

# Development Environment
dev:
	@echo "🚀 Starting Development Environment..."
	docker-compose -f docker-compose.dev.yml up -d
	@echo "✅ Development container is running!"
	@echo "   Connect: docker-compose -f docker-compose.dev.yml exec marker-engine-dev bash"

# Development Environment stoppen
dev-stop:
	@echo "🛑 Stopping Development Environment..."
	docker-compose -f docker-compose.dev.yml down

# Aufräumen
clean:
	@echo "🧹 Cleaning up..."
	docker-compose -f docker-compose.dev.yml down -v
	docker rmi marker-engine:latest marker-engine:runtime marker-engine:dev || true
	find . -type d -name "__pycache__" -exec rm -rf {} + || true
	find . -type f -name "*.pyc" -delete || true

# Code Linting
lint:
	@echo "🔍 Running Linter..."
	@if command -v ruff >/dev/null 2>&1; then \
		ruff check .; \
	else \
		echo "⚠️  Ruff not installed. Install with: pip install ruff"; \
	fi

# Code Formatting
format:
	@echo "✨ Formatting Code..."
	@if command -v ruff >/dev/null 2>&1; then \
		ruff format .; \
	else \
		echo "⚠️  Ruff not installed. Install with: pip install ruff"; \
	fi

# Lokale Poetry Installation
install:
	@echo "📦 Installing Dependencies..."
	poetry install

# Image Größe prüfen
check-size: build
	@echo "📏 Checking Image Size..."
	@SIZE=$$(docker images marker-engine:latest --format "{{.Size}}"); \
	echo "Image size: $$SIZE" 