# Chatbot Application - Container Deployment Guide

## Overview

This document provides instructions for containerizing and deploying the Flask-based chatbot application through your organization's pipeline.

## Container Setup

### Prerequisites

- Docker installed
- Access to your organization's container registry
- Database connection details

### Files Required for Container Deployment

#### 1. Dockerfile

- Located in project root
- Configures Python 3.9 environment
- Installs all dependencies
- Exposes port 5000
- Includes health check endpoint

#### 2. requirements.txt

- Contains all Python dependencies
- Already present in project

#### 3. .dockerignore

- Excludes unnecessary files from container
- Reduces container size

#### 4. docker-compose.yml

- For local testing and development
- Configures service with health checks

#### 5. .env.example

- Template for environment variables
- Copy to .env and configure

## Build Instructions

### Local Build

```bash
# Build the container
docker build -t chatbot-app .

# Run locally for testing
docker run -p 5000:5000 chatbot-app
```

### Using Docker Compose

```bash
# Create .env file with your configurations
cp .env.example .env
# Edit .env with your database and other settings

# Build and run
docker-compose up --build
```

## Environment Variables Required

### Essential Variables

- `SECRET_KEY` - Flask secret key for sessions
- `DATABASE_URL` - Database connection string
- `FLASK_ENV` - Set to "production"

### Optional Variables

- `ODOO_URL` - Odoo integration URL
- `ODOO_DB` - Odoo database name
- `ODOO_USERNAME` - Odoo username
- `ODOO_PASSWORD` - Odoo password

## Application Endpoints

### Health Check

- `GET /api/database/test` - Health check endpoint for container orchestration

### Main Application

- Port: 5000
- Main app runs on `/`
- API endpoints under `/api/`
- Admin panel under `/admin/`

## Pipeline Integration

### Container Registry

1. Build container with your CI/CD pipeline
2. Tag with version/commit hash
3. Push to your organization's container registry

### Deployment Pipeline

1. Pull container from registry
2. Configure environment variables
3. Deploy to target environment
4. Health check via `/api/database/test`

### Sample Pipeline Configuration (Adapt to your system)

```yaml
# Example pipeline steps
build:
  - docker build -t chatbot-app:${VERSION} .
  - docker tag chatbot-app:${VERSION} your-registry/chatbot-app:${VERSION}
  - docker push your-registry/chatbot-app:${VERSION}

deploy:
  - docker pull your-registry/chatbot-app:${VERSION}
  - docker run -d -p 5000:5000 --env-file .env your-registry/chatbot-app:${VERSION}
```

## Configuration Notes

### Database Connection

- Application supports MSSQL via pyodbc
- Ensure database server is accessible from container
- Use connection string format in DATABASE_URL

### File Uploads

- Upload directory: `/app/static/uploads`
- Consider mounting external volume for persistence
- Default max file size: 16MB

### Static Files

- Served from `/static/` path
- Includes uploaded files and assets

## Troubleshooting

### Common Issues

1. **Database Connection**: Verify DATABASE_URL format and network access
2. **File Permissions**: Ensure upload directory is writable
3. **Port Conflicts**: Default port 5000, change if needed
4. **Memory**: Application may need 512MB+ RAM

### Health Check

- Endpoint: `GET /api/database/test`
- Returns JSON with database status
- Use for readiness/liveness probes

### Logs

- Application logs to stdout/stderr
- Configure log level via FLASK_ENV

## Security Considerations

### Production Settings

- Set `FLASK_ENV=production`
- Use strong `SECRET_KEY`
- Secure database connections
- Configure proper CORS if needed

### Network Security

- Application runs on port 5000
- Configure firewall/security groups
- Use HTTPS in production (reverse proxy)

## Contact

For questions about this containerization:

- Check with development team
- Reference Gmagica Team implementation (via Arun)
- Review organization's container standards
