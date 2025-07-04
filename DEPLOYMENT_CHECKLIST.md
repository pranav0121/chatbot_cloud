# Deployment Checklist ✅

## Pre-Deployment Verification

### ✅ Docker Setup Complete

- [x] Dockerfile with production settings
- [x] docker-compose.yml with proper configuration
- [x] entrypoint.sh script with database checks
- [x] Health check endpoint (/health)
- [x] Non-root user configuration
- [x] Volume mounts for persistence
- [x] All dependencies in requirements.txt

### ✅ Environment Configuration

- [x] .env.template for easy setup
- [x] .env.production example
- [x] All environment variables documented
- [x] Security settings (FLASK_DEBUG=False)

### ✅ Application Ready

- [x] Circular import issues resolved (database.py module)
- [x] Health endpoint working
- [x] Database initialization code
- [x] Error handling and logging

## Deployment Instructions for New Server

### 1. Prerequisites on Target Server

```bash
# Install Docker and Docker Compose
sudo apt update
sudo apt install docker.io docker-compose

# Enable Docker service
sudo systemctl enable docker
sudo systemctl start docker

# Add user to docker group (optional)
sudo usermod -aG docker $USER
```

### 2. Copy Files to Server

Copy these essential files to your server:

```
📂 Project Structure:
├── app.py
├── models.py
├── database.py
├── config.py
├── auth.py
├── bot_service.py
├── requirements.txt
├── .env.template
├── .env.production
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── entrypoint.sh
├── static/
│   └── uploads/
├── translations/
├── templates/
└── DOCKER_DEPLOYMENT.md
```

### 3. Environment Setup

```bash
# Copy template and configure
cp .env.template .env

# Edit .env with your settings
nano .env
```

**Required Environment Variables:**

- `DB_SERVER` - Your SQL Server host
- `DB_DATABASE` - Database name (SupportChatbot)
- `DB_USERNAME` - Database username
- `DB_PASSWORD` - Database password
- `SECRET_KEY` - Flask secret key (generate new)
- `ODOO_URL` - Your Odoo instance URL
- `ODOO_USERNAME` - Odoo username
- `ODOO_PASSWORD` - Odoo password

### 4. Build and Run

```bash
# Navigate to docker directory
cd docker/

# Build the image
docker build -t chatbot-app:latest -f Dockerfile ..

# Start with docker-compose
docker-compose up -d

# Check logs
docker-compose logs -f
```

### 5. Verify Deployment

```bash
# Check container status
docker-compose ps

# Test health endpoint
curl http://localhost:5000/health

# Check application logs
docker-compose logs chatbot
```

## Port Configuration

- **Application Port**: 5000
- **Health Check**: http://localhost:5000/health
- **Main Application**: http://localhost:5000

## Production Considerations

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

### SSL Certificate (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### Firewall

```bash
# Allow HTTP and HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Optionally allow direct access to application port
sudo ufw allow 5000
```

## Troubleshooting

### Check Application Status

```bash
# Container logs
docker-compose logs chatbot

# Health check
curl -v http://localhost:5000/health

# Database connectivity test
docker-compose exec chatbot python -c "from database import db; print('DB OK')"
```

### Common Issues

1. **Database Connection**: Verify DB_SERVER, credentials, and network access
2. **Permission Issues**: Check file ownership and Docker permissions
3. **Port Conflicts**: Ensure port 5000 is available
4. **Environment Variables**: Verify .env file is properly loaded

### File Permissions

```bash
# Ensure proper permissions
sudo chown -R 1000:1000 static/uploads
sudo chown -R 1000:1000 translations
chmod +x docker/entrypoint.sh
```

## Performance Monitoring

- Monitor Docker container resource usage
- Check application logs regularly
- Set up log rotation for production
- Monitor database performance
- Set up automated backups

## Security Checklist

- [x] Non-root user in container
- [x] Production SECRET_KEY
- [x] FLASK_DEBUG=False
- [x] Secure database credentials
- [x] HTTPS in production
- [x] Firewall configuration
- [ ] Regular security updates
- [ ] Database backup strategy

## Support

For deployment issues, check:

1. DOCKER_DEPLOYMENT.md - Detailed deployment guide
2. Application logs via `docker-compose logs`
3. Health endpoint: http://localhost:5000/health
4. Database connectivity test scripts
