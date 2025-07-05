# Docker Production Deployment Guide

# YouCloudTech Flask Chatbot with MSSQL and Odoo Integration

## 🚀 Quick Start

### Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- 4GB+ RAM available
- 10GB+ disk space

### 1. Clone and Setup Environment

```bash
# Clone the project
git clone <your-repo-url>
cd chatbot_cloud

# Copy environment template
cp env.template .env

# Edit .env with your actual values
nano .env
```

### 2. Configure Environment Variables

Edit `.env` file with your settings:

```bash
# Database (use containerized MSSQL or external)
DB_SERVER=mssql-server  # For containerized DB
DB_PASSWORD=YourStrong@Password123
DB_USERNAME=sa
DB_DATABASE=SupportChatbot

# Odoo Integration
ODOO_URL=https://youcloudpay.odoo.com
ODOO_USERNAME=your-username
ODOO_PASSWORD=your-password
ODOO_DB=youcloudpay

# Security
SECRET_KEY=your-super-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key
```

### 3. Build and Run

```bash
# Build the application
docker-compose build

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f chatbot-app
```

### 4. Verify Deployment

```bash
# Health check
curl http://localhost:5000/health

# Test application
curl http://localhost:5000/

# Admin login
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@youcloudtech.com", "password": "admin123"}'
```

## 🔧 Production Configuration

### Using External MSSQL Server

Edit `.env`:

```bash
DB_SERVER=your-mssql-server.domain.com
DB_USERNAME=your-username
DB_PASSWORD=your-password
DB_USE_WINDOWS_AUTH=False
```

Then disable MSSQL service in `docker-compose.yml`:

```yaml
# Comment out or remove mssql-server service
# mssql-server:
#   image: mcr.microsoft.com/mssql/server:2019-latest
#   ...
```

### SSL/HTTPS Setup

1. Place SSL certificates in `docker/ssl/`:

```
docker/ssl/cert.pem
docker/ssl/key.pem
```

2. Uncomment HTTPS server block in `docker/nginx.conf`

3. Update environment:

```bash
FORCE_HTTPS=True
SECURE_COOKIE=True
```

### Scaling

```bash
# Scale Flask app instances
docker-compose up -d --scale chatbot-app=3

# Use external load balancer
# Update nginx upstream with multiple servers
```

## 📊 Monitoring

### Health Checks

```bash
# Application health
curl http://localhost:5000/health

# Database connectivity
curl http://localhost:5000/readiness

# Nginx health
curl http://localhost/nginx-health
```

### Logs

```bash
# Application logs
docker-compose logs -f chatbot-app

# Database logs
docker-compose logs -f mssql-server

# Nginx logs
docker-compose logs -f nginx

# All logs
docker-compose logs -f
```

### Metrics

```bash
# Container stats
docker stats

# Resource usage
docker system df

# Service status
docker-compose ps
```

## 🛠️ Troubleshooting

### Database Connection Issues

```bash
# Check MSSQL container
docker-compose exec mssql-server /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P $DB_PASSWORD -Q "SELECT 1"

# Check from app container
docker-compose exec chatbot-app python -c "
import pyodbc
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=mssql-server;DATABASE=master;UID=sa;PWD=$DB_PASSWORD')
print('Connected successfully')
"
```

### Application Issues

```bash
# Restart application
docker-compose restart chatbot-app

# Rebuild and restart
docker-compose down
docker-compose build --no-cache chatbot-app
docker-compose up -d

# Check environment variables
docker-compose exec chatbot-app env | grep -E "(DB_|ODOO_|FLASK_)"
```

### Database Initialization

```bash
# Manual database setup
docker-compose exec mssql-server /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P $DB_PASSWORD -i /docker-entrypoint-initdb.d/01-init.sql

# Reset database
docker-compose down -v
docker-compose up -d mssql-server
# Wait for startup, then:
docker-compose up -d chatbot-app
```

## 🔄 Backup and Recovery

### Database Backup

```bash
# Backup database
docker-compose exec mssql-server /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P $DB_PASSWORD -Q "BACKUP DATABASE SupportChatbot TO DISK = '/var/opt/mssql/backup/chatbot.bak'"

# Copy backup to host
docker cp $(docker-compose ps -q mssql-server):/var/opt/mssql/backup/chatbot.bak ./backup/
```

### Application Backup

```bash
# Backup volumes
docker run --rm -v chatbot_cloud_mssql-data:/data -v $(pwd)/backup:/backup alpine tar czf /backup/mssql-data.tar.gz -C /data .

# Backup uploads
docker run --rm -v chatbot_cloud_uploads:/data -v $(pwd)/backup:/backup alpine tar czf /backup/uploads.tar.gz -C /data .
```

## 🚀 Server Deployment

### System Requirements

- Ubuntu 20.04+ or RHEL 8+
- Docker Engine 20.10+
- Docker Compose 2.0+
- 4GB+ RAM
- 20GB+ disk space
- Firewall ports: 80, 443, 5000

### Installation Script

```bash
#!/bin/bash
# Server deployment script

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/2.12.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Create application directory
sudo mkdir -p /opt/chatbot
cd /opt/chatbot

# Clone application
git clone <your-repo-url> .

# Setup environment
cp env.template .env
# Edit .env with production values

# Setup SSL (if using HTTPS)
sudo mkdir -p docker/ssl
# Copy your SSL certificates

# Start application
docker-compose up -d

# Setup systemd service for auto-start
sudo tee /etc/systemd/system/chatbot.service > /dev/null <<EOF
[Unit]
Description=YouCloudTech Chatbot Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/chatbot
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable chatbot.service
sudo systemctl start chatbot.service
```

### Firewall Configuration

```bash
# Ubuntu/Debian
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 5000/tcp  # For direct access if needed

# RHEL/CentOS
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --reload
```

## 📋 Operations Checklist

### Pre-deployment

- [ ] Environment variables configured
- [ ] SSL certificates in place (if using HTTPS)
- [ ] Database credentials verified
- [ ] Odoo credentials verified
- [ ] Firewall rules configured
- [ ] Docker and Docker Compose installed

### Post-deployment

- [ ] Health checks passing
- [ ] Database connectivity verified
- [ ] Admin login working
- [ ] Odoo integration working
- [ ] File uploads working
- [ ] Logs being generated
- [ ] Backup procedures tested

### Maintenance

- [ ] Regular health checks
- [ ] Log rotation configured
- [ ] Database backups scheduled
- [ ] Security updates applied
- [ ] Performance monitoring
- [ ] SSL certificate renewal

## 🆘 Support Contacts

- **Application Issues**: dev-team@youcloudtech.com
- **Infrastructure**: ops-team@youcloudtech.com
- **Database**: dba-team@youcloudtech.com
- **Security**: security@youcloudtech.com

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Docker Documentation](https://docs.docker.com/)
- [MSSQL on Docker](https://docs.microsoft.com/en-us/sql/linux/sql-server-linux-docker-container-deployment)
- [Nginx Configuration](https://nginx.org/en/docs/)
- [Odoo API Documentation](https://www.odoo.com/documentation/15.0/developer/misc/api/odoo.html)
