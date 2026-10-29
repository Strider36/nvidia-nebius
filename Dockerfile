# Multi-stage optimized Dockerfile for Aegis AI
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final runtime image
FROM python:3.11-slim

# Security: run as non-root user
RUN groupadd -r aegis && useradd -r -g aegis aegis

WORKDIR /app

# Copy python packages from builder
COPY --from=builder /root/.local /home/aegis/.local
ENV PATH=/home/aegis/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

# Copy application source
COPY --chown=aegis:aegis app/ ./app/
COPY --chown=aegis:aegis frontend/ ./frontend/
COPY --chown=aegis:aegis skills/ ./skills/
COPY --chown=aegis:aegis main.py .
COPY --chown=aegis:aegis pyproject.toml .

# Create workspace and database mount targets
RUN mkdir -p /app/workspace /app/data && chown -R aegis:aegis /app

USER aegis

# Default environment configuration
ENV AEGIS_WORKSPACE=/app/workspace
ENV AEGIS_DATABASE_PATH=/app/data/aegis.db
ENV AEGIS_HOST=0.0.0.0
ENV AEGIS_PORT=8000

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health')"

CMD ["python", "main.py"]

