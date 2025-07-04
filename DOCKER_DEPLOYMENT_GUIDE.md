# Docker Deployment Guide for Chatbot Application with MSSQL

## Prerequisites

1. **Docker** and **Docker Compose** installed
2. **MSSQL Server** running and accessible (external database)
3. **Environment file** configured (copy from .env.example)
4. **Network connectivity** to MSSQL Server from Docker container

## Quick Start

### 1. Environment Setup

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your MSSQL server configuration
# Required configuration:
# - SECRET_KEY (strong random key)
# - DB_SERVER (your MSSQL server address)
# - DB_DATABASE=SupportChatbot
# - DB_USERNAME and DB_PASSWORD (or Windows Auth)
# - ADMIN_EMAIL, ADMIN_PASSWORD
```

### 2. Build and Run

#### Production Deployment (External MSSQL Server)

```bash
# Build and start the application
docker-compose up --build -d

# View logs to ensure successful startup
docker-compose logs -f chatbot
```

#### Alternative: Direct Docker Run

```bash
# Build the image
docker build -t chatbot-app .

# Run with external MSSQL
docker run -d \
  --name chatbot-app \
  -p 5000:5000 \
  --env-file .env \
  -v $(pwd)/static/uploads:/app/static/uploads \
  chatbot-app
```

### 3. Access the Application

- **Application**: http://localhost:5000
- **Health Check**: http://localhost:5000/api/database/test
- **Admin Panel**: http://localhost:5000/admin

## MSSQL Configuration

### Required Environment Variables for MSSQL

```bash
# Flask Configuration
SECRET_KEY=your-32-character-secret-key-here
FLASK_ENV=production

# MSSQL Database Configuration
DB_SERVER=your-mssql-server-ip-or-hostname
DB_DATABASE=SupportChatbot
DB_USERNAME=your-sql-username
DB_PASSWORD=your-sql-password
DB_USE_WINDOWS_AUTH=False  # Set to True only for Windows Authentication

# Admin Credentials
ADMIN_EMAIL=admin@yourdomain.com
ADMIN_PASSWORD=your-secure-admin-password
```

### MSSQL Connection Examples

#### SQL Server Authentication (Recommended for Docker)

```bash
DB_SERVER=192.168.1.100
DB_DATABASE=SupportChatbot
DB_USERNAME=chatbot_user
DB_PASSWORD=SecurePassword123!
DB_USE_WINDOWS_AUTH=False
```

#### Windows Authentication (for domain environments)

```bash
DB_SERVER=SQLSERVER01.domain.local
DB_DATABASE=SupportChatbot
DB_USERNAME=domain\serviceaccount
DB_PASSWORD=ServiceAccountPassword
DB_USE_WINDOWS_AUTH=True
```

#### Named Instance

```bash
DB_SERVER=192.168.1.100\SQLEXPRESS
DB_DATABASE=SupportChatbot
DB_USERNAME=sa
DB_PASSWORD=YourSAPassword
DB_USE_WINDOWS_AUTH=False
```

### Optional Variables

```bash
# Odoo Integration
ODOO_URL=https://your-odoo-instance.com
ODOO_DB=your-odoo-database
ODOO_USERNAME=your-odoo-user
ODOO_PASSWORD=your-odoo-password

# Application Settings
BABEL_DEFAULT_LOCALE=en
API_TITLE=Support Chatbot API
API_VERSION=v1
```

## Docker Commands

### Building

```bash
# Build the image
docker build -t chatbot-app .

# Build with custom tag
docker build -t chatbot-app:v1.0 .
```

### Running

```bash
# Run container with external database
docker run -d \
  --name chatbot-app \
  -p 5000:5000 \
  --env-file .env \
  chatbot-app

# Run with volume mounts
docker run -d \
  --name chatbot-app \
  -p 5000:5000 \
  --env-file .env \
  -v $(pwd)/static/uploads:/app/static/uploads \
  chatbot-app
```

### Monitoring

```bash
# View logs
docker logs chatbot-app -f

# Execute commands in container
docker exec -it chatbot-app bash

# Check container health
docker inspect chatbot-app | grep Health -A 10
```

## Troubleshooting

### MSSQL Database Connection Issues

1. **Test connectivity from Docker host**:

   ```bash
   # Test if MSSQL server is reachable
   telnet your-mssql-server 1433
   ```

2. **Check environment variables in container**:

   ```bash
   docker exec chatbot-app env | grep DB_
   ```

3. **Test database connection from container**:

   ```bash
   docker exec chatbot-app python -c "
   from config import Config
   from sqlalchemy import create_engine
   try:
       engine = create_engine(Config().SQLALCHEMY_DATABASE_URI)
       conn = engine.connect()
       print('Database connection successful!')
       conn.close()
   except Exception as e:
       print(f'Database connection failed: {e}')
   "
   ```

4. **Check ODBC drivers in container**:

   ```bash
   docker exec chatbot-app odbcinst -q -d
   ```

5. **Verify MSSQL server configuration**:
   - Ensure SQL Server Browser service is running
   - Check if TCP/IP protocol is enabled
   - Verify firewall allows port 1433
   - Confirm user has proper database permissions

### Common MSSQL Issues and Solutions

#### Issue: "Login failed for user"

**Solution**:

- Verify username/password are correct
- Check if user exists in MSSQL
- Ensure user has db_owner or sufficient permissions on SupportChatbot database

#### Issue: "Cannot connect to server"

**Solutions**:

- Verify DB_SERVER address is correct and reachable
- Check firewall settings on MSSQL server
- Ensure SQL Server is running and accepting connections
- For named instances, verify SQL Server Browser is running

#### Issue: "Database 'SupportChatbot' does not exist"

**Solution**:

```sql
-- Connect to MSSQL and create database
CREATE DATABASE SupportChatbot;
```

#### Issue: "Driver not found"

**Solution**: The Dockerfile includes ODBC Driver 17 for SQL Server. If issues persist:

- Rebuild the Docker image
- Check driver installation in container: `docker exec chatbot-app odbcinst -q -d`

### Application Issues

1. **Check application logs**:

   ```bash
   docker logs chatbot-app --tail 100
   ```

2. **Restart the container**:

   ```bash
   docker restart chatbot-app
   ```

3. **Rebuild the image**:
   ```bash
   docker-compose down
   docker-compose up --build
   ```

### Health Check Failures

1. **Check if application is running**:

   ```bash
   curl http://localhost:5000/api/database/test
   ```

2. **Check port binding**:
   ```bash
   docker port chatbot-app
   ```

## Production Deployment with MSSQL

### Pre-deployment Checklist

1. **MSSQL Server Requirements**:

   - SQL Server 2017 or later recommended
   - Database 'SupportChatbot' created
   - User account with db_owner permissions
   - TCP/IP connections enabled
   - Port 1433 accessible from Docker host

2. **Security Best Practices**:

   - Use dedicated SQL user (not 'sa') with minimal required permissions
   - Use strong passwords (minimum 12 characters)
   - Enable SQL Server encryption if possible
   - Restrict network access to MSSQL server
   - Regular security updates for SQL Server

3. **Network Configuration**:
   - Ensure Docker container can reach MSSQL server
   - Configure firewall rules appropriately
   - Use internal network addresses when possible

### Database Setup Script

```sql
-- Run this on your MSSQL server before deployment
USE master;
GO

-- Create database if it doesn't exist
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'SupportChatbot')
BEGIN
    CREATE DATABASE SupportChatbot;
END
GO

-- Create dedicated user for the application
USE SupportChatbot;
GO

-- Create login and user (replace with your credentials)
IF NOT EXISTS (SELECT name FROM sys.server_principals WHERE name = 'chatbot_user')
BEGIN
    CREATE LOGIN chatbot_user WITH PASSWORD = 'YourSecurePassword123!';
END
GO

IF NOT EXISTS (SELECT name FROM sys.database_principals WHERE name = 'chatbot_user')
BEGIN
    CREATE USER chatbot_user FOR LOGIN chatbot_user;
    ALTER ROLE db_owner ADD MEMBER chatbot_user;
END
GO
```

### Performance Optimization for MSSQL

1. **Database Connection Pooling**:

   ```bash
   # Add to .env file
   SQLALCHEMY_ENGINE_OPTIONS={"pool_size": 10, "max_overflow": 20, "pool_timeout": 30}
   ```

2. **Container Resource Limits**:

   ```yaml
   # In docker-compose.yml
   services:
     chatbot:
       deploy:
         resources:
           limits:
             cpus: "1.0"
             memory: 1G
           reservations:
             cpus: "0.5"
             memory: 512M
   ```

3. **MSSQL Performance Tips**:
   - Ensure adequate memory allocation to SQL Server
   - Regular index maintenance
   - Monitor connection count
   - Configure appropriate isolation levels

### Monitoring and Logging

1. **Application Logs**:

   ```bash
   # View real-time logs
   docker logs -f chatbot-app

   # Export logs for analysis
   docker logs chatbot-app > chatbot-app.log 2>&1
   ```

2. **Database Connection Monitoring**:

   ```sql
   -- Monitor active connections to SupportChatbot database
   SELECT
       DB_NAME(database_id) as DatabaseName,
       COUNT(*) as ConnectionCount
   FROM sys.dm_exec_sessions
   WHERE database_id = DB_ID('SupportChatbot')
   GROUP BY database_id;
   ```

3. **Health Check Endpoint**:
   - Monitor: `http://your-server:5000/api/database/test`
   - Should return JSON with database status

### Backup Strategy

1. **Database backups** (external to container)
2. **Upload files backup**:
   ```bash
   docker run --rm -v chatbot_uploads:/data -v $(pwd):/backup alpine tar czf /backup/uploads-backup.tar.gz -C /data .
   ```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build and Deploy

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Build Docker image
        run: docker build -t chatbot-app:${{ github.sha }} .

      - name: Run tests
        run: docker run --rm chatbot-app:${{ github.sha }} python -m pytest

      - name: Deploy to production
        run: |
          # Add your deployment commands here
          echo "Deploying to production..."
```

## Support

For issues and questions:

1. Check the application logs
2. Verify environment configuration
3. Ensure database connectivity
4. Review this deployment guide

## Files Structure for MSSQL Deployment

```
├── Dockerfile                 # Optimized for MSSQL with ODBC drivers
├── docker-compose.yml         # Production-ready MSSQL configuration
├── entrypoint.sh             # Container initialization with DB health checks
├── .dockerignore             # Docker build exclusions
├── .env.example              # MSSQL environment template
├── requirements.txt          # Python dependencies including pyodbc
├── build-and-test.sh         # Linux/Mac build script
├── build-and-test.bat        # Windows build script
└── DOCKER_DEPLOYMENT_GUIDE.md # This comprehensive guide
```

## Quick Deployment Commands

```bash
# 1. Setup environment
cp .env.example .env
# Edit .env with your MSSQL configuration

# 2. Build and deploy
docker-compose up --build -d

# 3. Monitor deployment
docker-compose logs -f chatbot

# 4. Test deployment
curl http://localhost:5000/api/database/test
```

## Support and Maintenance

### Regular Maintenance Tasks

1. **Update Docker images**:

   ```bash
   docker-compose pull
   docker-compose up --build -d
   ```

2. **Backup uploaded files**:

   ```bash
   docker cp chatbot-app:/app/static/uploads ./backup-uploads
   ```

3. **Monitor logs**:

   ```bash
   docker-compose logs --tail=100 chatbot
   ```

4. **Database health check**:
   ```bash
   curl -s http://localhost:5000/api/database/test | jq .
   ```

For production issues:

1. Check MSSQL server connectivity
2. Verify environment variables
3. Review application logs
4. Ensure sufficient database permissions
5. Monitor resource usage (CPU/Memory)

This Docker configuration is optimized specifically for MSSQL deployments and will provide reliable performance in production environments.
