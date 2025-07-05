# Multi-stage Dockerfile for Flask Chatbot with MSSQL and Odoo Integration
# Supports both development and production deployments

FROM python:3.9-slim-bullseye AS base

# Set environment variables for Python optimization
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    FLASK_APP=app.py \
    DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install system dependencies required for MSSQL connectivity
RUN apt-get update && apt-get install -y \
    # MSSQL/ODBC dependencies
    curl \
    apt-transport-https \
    gnupg2 \
    software-properties-common \
    unixodbc \
    unixodbc-dev \
    # Build dependencies
    gcc \
    g++ \
    build-essential \
    # Additional utilities
    gettext \
    # Health check utility
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Microsoft ODBC Driver 17 for SQL Server
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies with security optimizations
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# Development stage
FROM base AS development

ENV FLASK_ENV=development

# Install development tools
RUN pip install --no-cache-dir flask-debugtoolbar pytest

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser -s /bin/bash appuser

# Copy application code
COPY --chown=appuser:appuser . .

# Create necessary directories and set permissions
RUN mkdir -p /app/static/uploads /app/logs /app/translations /app/instance \
    && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose the application port
EXPOSE 5000

# Development command with hot reload
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000", "--debug"]

# Production stage
FROM base AS production

ENV FLASK_ENV=production

# Install production WSGI server
RUN pip install --no-cache-dir gunicorn gevent

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser -s /bin/bash appuser

# Copy application code (excluding unnecessary files via .dockerignore)
COPY --chown=appuser:appuser . .

# Create necessary directories and set permissions
RUN mkdir -p /app/static/uploads /app/logs /app/translations /app/instance \
    && chmod +x /app/*.sh 2>/dev/null || true \
    && chown -R appuser:appuser /app

# Switch to non-root user early for security
USER appuser

# Expose the application port
EXPOSE 5000

# Add labels for better container management
LABEL maintainer="chatbot-team" \
      version="1.0" \
      description="Flask Chatbot with MSSQL and Odoo Integration"

# Health check to ensure the application is running
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Use gunicorn for production deployment with optimal settings
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--worker-class", "gevent", "--worker-connections", "1000", "--timeout", "120", "--keep-alive", "2", "--max-requests", "1000", "--max-requests-jitter", "100", "--preload", "app:app"]
