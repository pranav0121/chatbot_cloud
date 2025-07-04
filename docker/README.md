# 🚀 YouCloudTech Chatbot - Docker Deployment Package

## 📦 Complete Ops Deployment Package

This docker folder contains **everything the ops team needs** to deploy the YouCloudTech Chatbot application on any server.

---

## 📂 **FILES IN THIS FOLDER**

### Core Docker Files

- **`Dockerfile`** - Production-ready Docker image configuration
- **`docker-compose.yml`** - Container orchestration setup
- **`entrypoint.sh`** - Smart startup script with health checks

### Environment Configuration

- **`.env.template`** - Template for environment variables (copy to `.env`)
- **`.env.production`** - Production example configuration

### Deployment & Documentation

- **`deploy.sh`** - Automated deployment script (Linux/Mac)
- **`DOCKER_DEPLOYMENT.md`** - Detailed deployment guide
- **`DEPLOYMENT_CHECKLIST.md`** - Step-by-step deployment checklist
- **`READY_FOR_DEPLOYMENT.md`** - Quick deployment overview

---

## ⚡ **QUICK DEPLOYMENT** (3 Steps)

### 1. Setup Environment

```bash
# Copy and configure environment
cp .env.template .env
nano .env  # Edit with your database and Odoo settings
```

### 2. Deploy Application

```bash
# Option A: Automated deployment (Linux/Mac)
chmod +x deploy.sh
./deploy.sh

# Option B: Manual deployment (Any OS)
docker build -t chatbot-app:latest -f Dockerfile ..
docker-compose up -d
```

### 3. Verify Deployment

```bash
# Check health
curl http://localhost:5000/health

# Check logs
docker-compose logs -f
```

---

## 🔧 **ENVIRONMENT CONFIGURATION**

### Required Variables in `.env`

```bash
# Database Configuration
DB_SERVER=your-sql-server-host
DB_DATABASE=SupportChatbot
DB_USERNAME=your-db-username
DB_PASSWORD=your-secure-password
DB_USE_WINDOWS_AUTH=false

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-super-secret-production-key

# Odoo Configuration
ODOO_URL=https://your-odoo-instance.odoo.com
ODOO_DB=your-database-name
ODOO_USERNAME=your-odoo-username
ODOO_PASSWORD=your-odoo-password
```

---

## 🐳 **DOCKER COMMANDS**

### Build & Start

```bash
# Build image
docker build -t chatbot-app:latest -f Dockerfile ..

# Start services
docker-compose up -d

# Start with rebuild
docker-compose up -d --build
```

### Monitoring

```bash
# Check status
docker-compose ps

# View logs (real-time)
docker-compose logs -f

# View logs (chatbot only)
docker-compose logs -f chatbot

# Health check
curl http://localhost:5000/health
```

### Management

```bash
# Stop services
docker-compose down

# Restart services
docker-compose restart

# Update and restart
docker-compose pull && docker-compose up -d

# Clean rebuild
docker-compose down
docker build --no-cache -t chatbot-app:latest -f Dockerfile ..
docker-compose up -d
```

---

## 📊 **MONITORING & TROUBLESHOOTING**

### Health Check Endpoint

```bash
# Test application health
curl -v http://localhost:5000/health

# Expected response (healthy):
{
  "status": "healthy",
  "database": "connected",
  "message": "Database connection successful",
  "timestamp": "2025-07-04T13:00:00Z"
}
```

### Common Issues & Solutions

**Container Won't Start**

```bash
# Check logs for errors
docker-compose logs chatbot

# Verify environment file
docker-compose config

# Check file permissions
ls -la .env
```

**Database Connection Failed**

```bash
# Test database connectivity
telnet your-db-server 1433

# Verify credentials
docker-compose exec chatbot env | grep DB_

# Check database server logs
docker-compose logs chatbot | grep -i database
```

**Application Not Responding**

```bash
# Check if container is running
docker-compose ps

# Test internal connectivity
docker-compose exec chatbot curl localhost:5000/health

# Check port binding
netstat -tulpn | grep 5000
```

---

## 🌐 **PRODUCTION DEPLOYMENT**

### Server Requirements

- **OS**: Linux (Ubuntu 20.04+ recommended)
- **Docker**: 20.10+
- **Docker Compose**: 1.29+
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 10GB minimum
- **Network**: Access to SQL Server and Odoo instances

### Security Checklist

- [ ] Configure firewall (ports 80, 443, 5000)
- [ ] Set up reverse proxy (Nginx/Apache)
- [ ] Install SSL certificate (Let's Encrypt)
- [ ] Secure `.env` file permissions (600)
- [ ] Use strong SECRET_KEY
- [ ] Enable Docker daemon security

### Reverse Proxy (Nginx)

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 🔄 **BACKUP & MAINTENANCE**

### Backup Strategy

```bash
# Backup application data
docker-compose exec chatbot tar -czf /tmp/app-backup.tar.gz /app/static/uploads
docker cp container_name:/tmp/app-backup.tar.gz ./backups/

# Backup configuration
cp .env ./backups/.env.backup.$(date +%Y%m%d)

# Database backup (SQL Server)
# Use your organization's SQL Server backup procedures
```

### Updates

```bash
# Update application code
git pull origin main  # If using git
docker-compose down
docker build --no-cache -t chatbot-app:latest -f Dockerfile ..
docker-compose up -d

# Check logs after update
docker-compose logs -f chatbot
```

---

## 📞 **SUPPORT & CONTACTS**

### Logs Location

- **Application Logs**: `docker-compose logs chatbot`
- **System Logs**: `/var/log/docker/`
- **Health Endpoint**: `http://localhost:5000/health`

### Emergency Procedures

1. **Service Down**: `docker-compose restart`
2. **Database Issues**: Check DB server connectivity
3. **Memory Issues**: `docker system prune -f`
4. **Complete Reset**:
   ```bash
   docker-compose down
   docker system prune -f
   docker-compose up -d
   ```

### Key Metrics to Monitor

- Container CPU/Memory usage
- Database connection status
- Application response time
- Health check endpoint status
- Disk space usage

---

## ✅ **DEPLOYMENT VERIFICATION**

After deployment, verify these items:

- [ ] Container is running: `docker-compose ps`
- [ ] Health check passes: `curl http://localhost:5000/health`
- [ ] Application accessible: `curl http://localhost:5000`
- [ ] Logs show no errors: `docker-compose logs chatbot`
- [ ] Database connectivity confirmed
- [ ] File uploads working (if applicable)

---

## 🎯 **QUICK REFERENCE**

| Action  | Command                                 |
| ------- | --------------------------------------- |
| Deploy  | `./deploy.sh` or `docker-compose up -d` |
| Stop    | `docker-compose down`                   |
| Restart | `docker-compose restart`                |
| Logs    | `docker-compose logs -f chatbot`        |
| Health  | `curl http://localhost:5000/health`     |
| Status  | `docker-compose ps`                     |
| Shell   | `docker-compose exec chatbot bash`      |

---

**📧 For support, check the detailed guides in this folder or contact the development team.**

_This package contains everything needed for production deployment. No additional files required._
