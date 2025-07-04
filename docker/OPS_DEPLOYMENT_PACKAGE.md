# 📦 YouCloudTech Chatbot - Complete Ops Deployment Package

## 🎯 **EVERYTHING THE OPS TEAM NEEDS IS IN THIS FOLDER**

This folder contains the **complete deployment package** for the YouCloudTech Chatbot application. No other files are needed for deployment.

---

## 📂 **PACKAGE CONTENTS**

### 🚀 **QUICK START FILES**

- **`README.md`** - This comprehensive ops guide (START HERE)
- **`deploy.sh`** - Automated deployment script (Linux/Mac)
- **`deploy.bat`** - Automated deployment script (Windows)

### 🐳 **DOCKER CONFIGURATION**

- **`Dockerfile`** - Production-ready Docker image
- **`docker-compose.yml`** - Container orchestration
- **`entrypoint.sh`** - Smart startup script with health checks

### ⚙️ **ENVIRONMENT SETUP**

- **`.env.template`** - Environment variables template
- **`.env.production`** - Production configuration example

### 📚 **DOCUMENTATION**

- **`DOCKER_DEPLOYMENT.md`** - Detailed deployment guide
- **`DEPLOYMENT_CHECKLIST.md`** - Step-by-step checklist
- **`READY_FOR_DEPLOYMENT.md`** - Quick deployment overview

---

## ⚡ **3-STEP DEPLOYMENT**

### 1️⃣ **Configure Environment**

```bash
cp .env.template .env
nano .env  # Edit with your database/Odoo settings
```

### 2️⃣ **Deploy Application**

```bash
# Linux/Mac
chmod +x deploy.sh && ./deploy.sh

# Windows
deploy.bat

# Manual (any OS)
docker build -t chatbot-app:latest -f Dockerfile ..
docker-compose up -d
```

### 3️⃣ **Verify Deployment**

```bash
curl http://localhost:5000/health
docker-compose logs -f
```

---

## 🔑 **REQUIRED ENVIRONMENT VARIABLES**

Edit `.env` with these settings:

```bash
# Database (REQUIRED)
DB_SERVER=your-sql-server-host
DB_DATABASE=SupportChatbot
DB_USERNAME=your-db-username
DB_PASSWORD=your-secure-password

# Security (REQUIRED)
SECRET_KEY=your-super-secret-production-key
FLASK_ENV=production
FLASK_DEBUG=False

# Odoo Integration (OPTIONAL)
ODOO_URL=https://your-odoo-instance.odoo.com
ODOO_DB=your-database-name
ODOO_USERNAME=your-odoo-username
ODOO_PASSWORD=your-odoo-password
```

---

## 🛠️ **MANAGEMENT COMMANDS**

| Action      | Command                             |
| ----------- | ----------------------------------- |
| **Deploy**  | `./deploy.sh` or `deploy.bat`       |
| **Start**   | `docker-compose up -d`              |
| **Stop**    | `docker-compose down`               |
| **Restart** | `docker-compose restart`            |
| **Status**  | `docker-compose ps`                 |
| **Logs**    | `docker-compose logs -f`            |
| **Health**  | `curl http://localhost:5000/health` |
| **Shell**   | `docker-compose exec chatbot bash`  |

---

## 📊 **MONITORING**

### Health Check Endpoint

```bash
curl http://localhost:5000/health
```

### Expected Response (Healthy)

```json
{
  "status": "healthy",
  "database": "connected",
  "message": "Database connection successful",
  "timestamp": "2025-07-04T13:00:00Z"
}
```

### Log Monitoring

```bash
# Real-time logs
docker-compose logs -f chatbot

# Error logs only
docker-compose logs chatbot | grep -i error

# Database connection logs
docker-compose logs chatbot | grep -i database
```

---

## 🌐 **PRODUCTION SETUP**

### Server Requirements

- **OS**: Linux (Ubuntu 20.04+) or Windows Server
- **Docker**: 20.10+
- **Docker Compose**: 1.29+
- **RAM**: 4GB recommended
- **Storage**: 10GB minimum
- **Network**: Access to SQL Server

### Security Checklist

- [ ] Configure firewall (allow ports 80, 443)
- [ ] Set up reverse proxy (Nginx/IIS)
- [ ] Install SSL certificate
- [ ] Secure `.env` file permissions
- [ ] Use strong passwords and keys

### Reverse Proxy Setup (Nginx)

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 🔧 **TROUBLESHOOTING**

### Container Won't Start

```bash
# Check logs for errors
docker-compose logs chatbot

# Verify configuration
docker-compose config

# Check file permissions
ls -la .env
```

### Database Connection Issues

```bash
# Test database connectivity
telnet your-db-server 1433

# Verify credentials
docker-compose exec chatbot env | grep DB_

# Check startup logs
docker-compose logs chatbot | head -50
```

### Application Not Responding

```bash
# Check container status
docker-compose ps

# Test internal connectivity
docker-compose exec chatbot curl localhost:5000/health

# Check port availability
netstat -tulpn | grep 5000
```

---

## 📞 **SUPPORT**

### Emergency Actions

1. **Service Down**: `docker-compose restart`
2. **Database Issues**: Check SQL Server connectivity
3. **Memory Issues**: `docker system prune -f`
4. **Complete Reset**:
   ```bash
   docker-compose down
   docker system prune -f
   docker-compose up -d
   ```

### Key Files for Troubleshooting

- **Application Logs**: `docker-compose logs chatbot`
- **Environment Config**: `.env` file
- **Container Status**: `docker-compose ps`
- **Health Status**: `curl http://localhost:5000/health`

---

## ✅ **POST-DEPLOYMENT VERIFICATION**

After deployment, verify:

- [ ] Container is running: `docker-compose ps`
- [ ] Health check passes: `curl http://localhost:5000/health`
- [ ] Application loads: `curl http://localhost:5000`
- [ ] No errors in logs: `docker-compose logs chatbot`
- [ ] Database connectivity confirmed
- [ ] SSL certificate working (production)

---

## 🎉 **DEPLOYMENT SUCCESS**

**Your YouCloudTech Chatbot is now ready for production!**

- ✅ **Complete Docker configuration**
- ✅ **Automated deployment scripts**
- ✅ **Health monitoring**
- ✅ **Security best practices**
- ✅ **Comprehensive documentation**

---

_Everything needed for deployment is in this docker folder. No additional files required._

**📧 For technical support, refer to the detailed documentation files in this folder.**
