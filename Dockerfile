# Multi-Stage Dockerfile für Marker Engine
# Stage 1: Builder - Installiert alle Dependencies und bereitet die App vor
FROM python:3.12-slim-bookworm AS builder

# Arbeitsverzeichnis setzen
WORKDIR /app

# System-Dependencies für Build-Tools installieren
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Poetry installieren (für Dependency Management)
RUN pip install --no-cache-dir poetry==1.7.1

# Projekt-Dependencies kopieren
# Zuerst nur pyproject.toml und poetry.lock für besseres Layer-Caching
COPY pyproject.toml poetry.lock* ./

# Dependencies installieren
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Restlichen Code kopieren
COPY . .

# Projekt installieren
RUN poetry install --no-interaction --no-ansi

# Stage 2: Runtime - Schlankes Production Image
FROM python:3.12-slim-bookworm AS runtime

# Arbeitsverzeichnis setzen
WORKDIR /app

# Nur notwendige Runtime-Dependencies installieren
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Python-Packages vom Builder kopieren
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# App-Code kopieren
COPY --from=builder /app /app

# Environment Variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Standard-Command (wird später durch marker-cli ersetzt)
CMD ["python", "-m", "pytest", "-q"]

# Stage 3: Development - Mit Hot-Reload Support
FROM builder AS development

# Arbeitsverzeichnis
WORKDIR /app

# Development-Tools installieren
RUN pip install --no-cache-dir \
    pytest \
    pytest-cov \
    pytest-asyncio \
    ipython \
    watchdog

# Environment für Development
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV ENVIRONMENT=development

# Volume für Hot-Reload
VOLUME ["/app"]

# Development Server (wird später angepasst)
CMD ["python", "-m", "pytest", "--watch"] 