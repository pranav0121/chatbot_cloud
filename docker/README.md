# 🐳 Complete Docker Deployment Guide for Chatbot Application

This folder contains all Docker-related files for deploying the Flask chatbot application with MSSQL Server integration. **Everything you need is here - no additional support required.**

## 📁 Folder Contents

- **`Dockerfile`** - Production-ready container configuration with MSSQL ODBC drivers
- **`docker-compose.yml`** - MSSQL-optimized orchestration configuration
- **`entrypoint.sh`** - Smart initialization script with database health checks
- **`.dockerignore`** - Build optimization exclusions
- **`complete-deployment.bat`** - **One-click Windows deployment script (RECOMMENDED)**
- **`complete-deployment.sh`** - **One-click Linux/Mac deployment script (RECOMMENDED)**
- **`build-and-test.bat`** - Windows build and test script
- **`build-and-test.sh`** - Linux/Mac build and test script
- **`validate-deployment.py`** - Automated deployment validation and health checks
- **`DOCKER_DEPLOYMENT_GUIDE.md`** - Comprehensive deployment documentation
- **`DEPLOYMENT_SUCCESS.md`** - Quick reference and success summary

## �️ CRITICAL: Database Setup (MUST DO FIRST)

### Step 1: MSSQL Server Setup

```sql
-- 1. Create database
CREATE DATABASE SupportChatbot;
GO

-- 2. Create login and user
USE master;
CREATE LOGIN chatbot_user WITH PASSWORD = 'YourSecurePassword123!';
GO

USE SupportChatbot;
CREATE USER chatbot_user FOR LOGIN chatbot_user;
ALTER ROLE db_owner ADD MEMBER chatbot_user;
GO

-- 3. Enable TCP/IP (Required for external connections)
-- Run SQL Server Configuration Manager -> SQL Server Network Configuration
-- -> Protocols for MSSQLSERVER -> Enable TCP/IP -> Restart SQL Server Service
```

### Step 2: Test Database Connection

```bash
# Test connection using sqlcmd (Windows)
sqlcmd -S your_server_name -U chatbot_user -P YourSecurePassword123! -d SupportChatbot -Q "SELECT 1"

# Should return: (1 rows affected)
```

### Step 3: Environment Configuration

Copy `.env.example` to `.env` and configure:

```env
# Database Configuration (REQUIRED)
DB_SERVER=your_server_name_or_ip
DB_DATABASE=SupportChatbot
DB_USERNAME=chatbot_user
DB_PASSWORD=YourSecurePassword123!
DB_DRIVER=ODBC Driver 17 for SQL Server

# Application Configuration
SECRET_KEY=your-super-secret-key-here
FLASK_ENV=production

# Optional: Odoo Integration
ODOO_URL=https://your-odoo-instance.com
ODOO_DB=your_odoo_database
ODOO_USERNAME=your_odoo_user
ODOO_PASSWORD=your_odoo_password
```

## 🚀 Deployment Instructions

### Option A: Complete Automated Deployment (Recommended for Beginners)

```bash
# Windows - One-click deployment
cd docker
.\complete-deployment.bat

# Linux/Mac - One-click deployment
cd docker
chmod +x complete-deployment.sh
./complete-deployment.sh
```

**This handles everything: building, running, validation, and troubleshooting guidance.**

### Option B: Step-by-Step Build and Test

```bash
# Windows
cd docker
.\build-and-test.bat

# Linux/Mac
cd docker
chmod +x build-and-test.sh
./build-and-test.sh
```

### Option C: Manual Deployment (Advanced Users)

```bash
# 1. From project root directory
docker build -f docker/Dockerfile -t chatbot-app .

# 2. Run container
docker run -d --name chatbot-app -p 5000:5000 --env-file .env chatbot-app

# 3. Check logs
docker logs chatbot-app
```

### Option D: Docker Compose (Production)

```bash
# From docker folder
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## ✅ Deployment Validation

After deployment, run the validation script:

```bash
# Automatic validation
python validate-deployment.py

# Custom URL validation
python validate-deployment.py --url http://your-server:5000
```

## 📋 Prerequisites Checklist

✅ **Docker & Docker Compose** installed  
✅ **MSSQL Server** running and accessible  
✅ **Database `SupportChatbot`** created  
✅ **User `chatbot_user`** with `db_owner` permissions  
✅ **TCP/IP enabled** on MSSQL Server port 1433  
✅ **Environment file `.env`** configured with correct database details

## 🔧 Application Features & Endpoints

Once deployed, the application provides:

### Core Features

- **Multi-language Support**: English, Arabic, Hindi, Urdu, Spanish, French
- **Device Tracking**: Automatic device information capture
- **Ticket Escalation**: Automated SLA-based escalation system
- **Admin Panel**: Complete ticket management dashboard
- **Live Chat**: Real-time customer support
- **API Integration**: RESTful APIs for external systems

### Key Endpoints

```bash
# Health Check
GET http://localhost:5000/api/database/test

# Admin Panel
GET http://localhost:5000/admin

# API Documentation
GET http://localhost:5000/api/tickets
GET http://localhost:5000/api/users
GET http://localhost:5000/api/escalations
```

## 🚨 Troubleshooting Guide

### Common Issues & Solutions

#### 1. Database Connection Failed

```bash
# Check SQL Server is running
net start MSSQLSERVER

# Verify TCP/IP is enabled
# SQL Server Configuration Manager -> Protocols -> TCP/IP -> Enabled

# Test connection
sqlcmd -S server_name -U chatbot_user -P password -d SupportChatbot
```

#### 2. Container Build Fails

```bash
# Clear Docker cache
docker system prune -a

# Rebuild from scratch
docker build --no-cache -f docker/Dockerfile -t chatbot-app .
```

#### 3. Application Startup Errors

```bash
# Check container logs
docker logs chatbot-app

# Common fixes:
# - Verify .env file exists and has correct values
# - Ensure database is accessible from container
# - Check firewall settings (port 1433)
```

#### 4. Port Already in Use

```bash
# Find process using port 5000
netstat -ano | findstr :5000

# Kill process (Windows)
taskkill /PID <process_id> /F

# Or use different port
docker run -p 5001:5000 chatbot-app
```

## 📊 Database Schema Auto-Creation

The application automatically creates all required tables on first startup:

- `users` - User accounts and authentication
- `tickets` - Support ticket management
- `escalations` - Ticket escalation tracking
- `devices` - Device information tracking
- `faq` - Frequently asked questions
- `chat_sessions` - Live chat history

**No manual database setup required beyond creating the database and user.**

## 🔐 Security Configuration

### Production Security Checklist

✅ Change default `SECRET_KEY` in `.env`  
✅ Use strong database password  
✅ Enable HTTPS (configure reverse proxy)  
✅ Restrict database access to application IP only  
✅ Regular backup schedule  
✅ Monitor application logs

### Network Configuration

```bash
# Allow MSSQL Server through firewall (Windows)
netsh advfirewall firewall add rule name="SQL Server" dir=in action=allow protocol=TCP localport=1433

# Docker network (if using custom networks)
docker network create chatbot-network
```

## 📈 Performance Optimization

### Recommended Server Specs

- **Minimum**: 2 CPU cores, 4GB RAM, 20GB storage
- **Recommended**: 4 CPU cores, 8GB RAM, 50GB storage
- **High Traffic**: 8+ CPU cores, 16GB+ RAM, SSD storage

### Database Optimization

```sql
-- Enable performance monitoring
ALTER DATABASE SupportChatbot SET QUERY_STORE = ON;

-- Create indexes for better performance (auto-created by app)
-- The application handles all index creation automatically
```

## 🔄 Backup & Recovery

### Database Backup

```sql
-- Full backup
BACKUP DATABASE SupportChatbot TO DISK = 'C:\Backup\SupportChatbot_Full.bak'

-- Restore
RESTORE DATABASE SupportChatbot FROM DISK = 'C:\Backup\SupportChatbot_Full.bak'
```

### Container Data Backup

```bash
# Backup uploaded files
docker cp chatbot-app:/app/static/uploads ./backup/uploads

# Backup translations
docker cp chatbot-app:/app/translations ./backup/translations
```

## 🆘 Emergency Contacts & Support

### Self-Help Resources

1. **Application Logs**: `docker logs chatbot-app`
2. **Database Logs**: SQL Server Error Log
3. **System Health**: `http://localhost:5000/api/database/test`

### Common Commands

```bash
# Restart application
docker restart chatbot-app

# Update application
docker pull chatbot-app:latest
docker stop chatbot-app
docker rm chatbot-app
docker run -d --name chatbot-app -p 5000:5000 --env-file .env chatbot-app:latest

# View real-time logs
docker logs -f chatbot-app
```

## ✅ Deployment Success Verification

After deployment, verify everything works:

1. **Database Connection**: Visit `http://localhost:5000/api/database/test`
2. **Admin Access**: Visit `http://localhost:5000/admin`
3. **API Health**: Test API endpoints
4. **File Uploads**: Test file upload functionality
5. **Translations**: Check multi-language support

**If all checks pass, your deployment is successful! 🎉**

---

**📝 Note**: This is a complete, self-contained deployment guide. No additional developer support should be needed if you follow these instructions carefully.
DB_USERNAME=your-username
DB_PASSWORD=your-password
DB_USE_WINDOWS_AUTH=False
SECRET_KEY=your-secret-key

````

## 🛡️ Security Features

- ✅ **MSSQL ODBC Driver 17** - Latest secure drivers
- ✅ **Non-root container** - Enhanced security
- ✅ **Environment-based config** - No hardcoded credentials
- ✅ **Health checks** - Automatic failure detection
- ✅ **Resource limits** - Configurable resource constraints

## 📊 Monitoring

### Check Container Status
```bash
docker-compose ps
````

### View Logs

```bash
docker-compose logs -f chatbot
```

### Health Check

```bash
curl http://localhost:5000/api/database/test
```

## 🔄 CI/CD Integration

The Docker configuration supports:

- **GitHub Actions**
- **Jenkins**
- **Azure DevOps**
- **AWS CodePipeline**
- **Any standard CI/CD platform**

Example build command for CI/CD:

```bash
docker build -f docker/Dockerfile -t chatbot-app:${BUILD_NUMBER} .
```

## 📖 Documentation

For detailed deployment instructions, troubleshooting, and production considerations, see:

- **`DOCKER_DEPLOYMENT_GUIDE.md`** - Complete documentation
- **`DEPLOYMENT_SUCCESS.md`** - Quick reference

## 🆘 Support

If you encounter issues:

1. Check the deployment guide for troubleshooting
2. Verify MSSQL connectivity
3. Review container logs
4. Ensure environment variables are correct

---

**Ready for production deployment! 🚀**
