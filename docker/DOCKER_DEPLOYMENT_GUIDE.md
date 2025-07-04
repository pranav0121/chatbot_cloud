# Docker Deployment Guide - Chatbot Cloud Application

## Overview

This Flask-based chatbot application uses Docker for containerization and deployment. The application integrates with SQL Server and Odoo systems.

## Docker Files Summary

### 1. Dockerfile

**Location**: `docker/Dockerfile`

- **Base Image**: Python 3.9-slim
- **Key Features**:
  - Installs Microsoft ODBC Driver 17 for SQL Server
  - Sets up production environment variables
  - Includes health checks via `/api/database/test` endpoint
  - Uses entrypoint script for initialization
  - Creates directories for file uploads and translations

### 2. docker-compose.yml (Development)

**Location**: `docker/docker-compose.yml`

- **Port**: 5000:5000
- **Environment**: Production
- **Health Check**: 60s start period
- **Volumes**: Persistent storage for uploads and translations

### 3. docker-compose.prod.yml (Production)

**Location**: `docker/docker-compose.prod.yml`

- **Port**: 5000:5000
- **Environment**: Production
- **Health Check**: 40s start period (faster for production)
- **Volumes**: Persistent storage for uploads and translations

### 4. entrypoint.sh

**Location**: `docker/entrypoint.sh`

- **Database Readiness**: Waits up to 30 retries for database connection
- **Auto-Migration**: Creates/updates database tables on startup
- **Error Handling**: Graceful handling of database setup failures

## Required Environment Variables (.env file)

### Database Configuration (SQL Server)

```env
DB_SERVER=your-sql-server-instance
DB_DATABASE=SupportChatbot
DB_USERNAME=chatbot_user
DB_PASSWORD=your-secure-password
DB_USE_WINDOWS_AUTH=False
```

### Application Configuration

```env
FLASK_DEBUG=False
SECRET_KEY=your-production-secret-key
```

### Odoo Integration

```env
ODOO_URL=https://your-odoo-instance.com
ODOO_DB=your-odoo-database
ODOO_USERNAME=your-odoo-username
ODOO_PASSWORD=your-odoo-password
```

## Database Setup

### SQL Server Requirements

- Microsoft SQL Server (2016 or later recommended)
- Database: `SupportChatbot`
- User with db_owner permissions or equivalent

### Key Tables (Auto-created by application)

- **Users**: User authentication and management
- **Tickets**: Support ticket management
- **Escalations**: Ticket escalation tracking
- **DeviceInfo**: Device tracking information
- **Partners**: Odoo partner integration

### Sample Database Creation Script

```sql
-- Create database
CREATE DATABASE SupportChatbot;
GO

-- Create user (if not using Windows Auth)
USE SupportChatbot;
CREATE USER [chatbot_user] FOR LOGIN [chatbot_user];
ALTER ROLE db_owner ADD MEMBER [chatbot_user];
GO
```

## Deployment Instructions

### 1. Prerequisites

- Docker and Docker Compose installed
- SQL Server accessible from container
- Valid .env file with production values

### 2. Build and Run (Development)

```bash
cd docker
docker-compose up --build
```

### 3. Build and Run (Production)

```bash
cd docker
docker-compose -f docker-compose.prod.yml up --build -d
```

### 4. Health Check Verification

```bash
curl http://localhost:5000/api/database/test
```

## CI/CD Pipeline Considerations

### Build Stage

```bash
docker build -t chatbot-app:latest -f docker/Dockerfile .
```

### Test Stage

- Application includes health check endpoint
- Database connectivity is verified on startup
- Automated tests can be run with pytest

### Deploy Stage

```bash
docker-compose -f docker/docker-compose.prod.yml up -d
```

## Security Notes

1. **Environment Variables**: Never commit .env files with production credentials
2. **Database Access**: Use dedicated service account with minimal required permissions
3. **Secret Management**: Use Docker secrets or external secret management in production
4. **Network Security**: Configure appropriate firewall rules for port 5000

## Monitoring and Logs

- **Health Check**: Built-in health check on `/api/database/test`
- **Application Logs**: Available via `docker logs <container-name>`
- **Database Connectivity**: Automatic retry logic with detailed logging

## Troubleshooting

### Common Issues

1. **Database Connection**: Check SQL Server accessibility and credentials
2. **ODBC Driver**: Ensure Microsoft ODBC Driver 17 is properly installed in container
3. **Permissions**: Verify database user has sufficient permissions
4. **Port Conflicts**: Ensure port 5000 is available on host system

### Debug Commands

```bash
# Check container logs
docker logs chatbot-app

# Access container shell
docker exec -it chatbot-app /bin/bash

# Test database connection manually
docker exec chatbot-app python -c "from config import Config; print(Config().SQLALCHEMY_DATABASE_URI)"
```

## Dependencies

See `requirements.txt` for complete Python package list:

- Flask 2.0.1
- Flask-SQLAlchemy 2.5.1
- pyodbc 4.0.32 (SQL Server connectivity)
- Flask-SocketIO 5.3.2 (Real-time features)
- Flask-Babel 2.0.0 (Internationalization)

## Support

For deployment issues or questions, contact the development team with:

- Container logs
- Environment configuration (sanitized)
- Error messages
- Network/infrastructure details
