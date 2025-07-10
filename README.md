# Marker Engine

Semantic Behavior Marker Analysis Engine - Ein System zur Erkennung und Analyse von kommunikativen Markern in digitalen Dialogen.

## 🚀 Quick Start mit Docker

### Production Build

```bash
# Runtime-Image bauen
docker build . --target runtime -t marker-engine:latest

# Smoke-Test ausführen
docker run --rm marker-engine:latest

# Mit eigenen Tests
docker run --rm -v $(pwd)/tests:/app/tests marker-engine:latest
```

### Development mit Docker Compose

```bash
# Development-Container starten
docker-compose -f docker-compose.dev.yml up -d

# In den Container verbinden
docker-compose -f docker-compose.dev.yml exec marker-engine-dev bash

# Tests ausführen
docker-compose -f docker-compose.dev.yml exec marker-engine-dev pytest

# API starten (später)
docker-compose -f docker-compose.dev.yml exec marker-engine-dev uvicorn api.main:app --reload
```

## 🛠️ Lokale Entwicklung (ohne Docker)

### Voraussetzungen

- Python 3.12+
- Poetry (Dependency Management)
- Node.js 20+ (für Commit-Hooks)

### Setup

```bash
# Poetry installieren
curl -sSL https://install.python-poetry.org | python3 -

# Dependencies installieren
poetry install

# Pre-commit Hooks aktivieren
npm install

# Tests ausführen
poetry run pytest
```

## 📁 Projektstruktur

```
marker-engine/
├── api/          # FastAPI REST/WebSocket Server
├── client/       # CLI und SDK
├── engine/       # Core Marker Detection Engine  
├── kb/           # Knowledge Base (Marker Definitionen)
├── tests/        # Test Suite
├── Dockerfile    # Multi-Stage Build
└── pyproject.toml # Poetry Dependencies
```

## 🧪 Testing

```bash
# Alle Tests
poetry run pytest

# Mit Coverage
poetry run pytest --cov=engine --cov=api

# Nur Smoke Tests
poetry run pytest tests/test_smoke.py
```

## 🔧 CI/CD

Die GitHub Actions Pipeline führt automatisch folgende Schritte aus:

1. Docker Image Build (Runtime & Development)
2. Image-Größe Validierung (< 300MB)
3. Smoke Tests im Container
4. Linting mit Ruff
5. Artifact Upload

## ⚙️ Umgebungsvariablen

Erstelle eine `.env` Datei im Projekt-Root:

```bash
# OpenAI API
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=gpt-4-turbo-preview

# API Server
API_HOST=0.0.0.0
API_PORT=8000
API_KEY=your-secure-api-key

# Environment
ENVIRONMENT=development
LOG_LEVEL=INFO
```

## 📝 Commit Convention

Wir nutzen [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` Neue Features
- `fix:` Bugfixes  
- `docs:` Dokumentation
- `test:` Tests
- `chore:` Maintenance

Commits werden automatisch via Husky/Commitlint validiert.

