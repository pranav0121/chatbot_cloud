# Docker Deployment Guide

This guide will help you deploy the YouCloudTech Chatbot application using Docker on any server.

## Prerequisites

- Docker and Docker Compose installed
- SQL Server database (can be hosted separately)
- Odoo instance (can be hosted separately)

## Quick Start

1. **Clone/Copy the application files to your server**

2. **Configure Environment Variables**

   ```bash
   cp .env.template .env
   ```

   Edit the `.env` file with your production settings:

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
   ODOO_DB=your-odoo-database
   ODOO_USERNAME=your-odoo-username
   ODOO_PASSWORD=your-odoo-password
   ```

3. **Build and Start the Application**

   ```bash
   cd docker
   docker-compose up -d --build
   ```

4. **Check Application Status**

   ```bash
   docker-compose logs -f chatbot
   docker-compose ps
   ```

5. **Access the Application**
   - Open http://your-server-ip:5000 in your browser
   - Health check: http://your-server-ip:5000/health

## Production Deployment

### With Reverse Proxy (Recommended)

Use nginx or traefik as a reverse proxy:

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### SSL/HTTPS Setup

1. Install certbot
2. Get SSL certificate: `certbot --nginx -d yourdomain.com`
3. Update nginx config for HTTPS

### Database Setup

The application will automatically create database tables on first run. Ensure:

- SQL Server is accessible from the Docker container
- Database user has CREATE TABLE permissions
- Connection string is correct in `.env`

### Monitoring

- Health endpoint: `/health`
- Logs: `docker-compose logs chatbot`
- Metrics: Check Docker stats with `docker stats`

## Troubleshooting

### Container Won't Start

```bash
docker-compose logs chatbot
```

### Database Connection Issues

- Verify DB_SERVER can be reached from container
- Check firewall settings
- Verify credentials

### Odoo Connection Issues

- Verify ODOO_URL is accessible
- Check Odoo credentials
- Ensure Odoo API is enabled

### Application Errors

- Check logs: `docker-compose logs -f chatbot`
- Check health endpoint: `curl http://localhost:5000/health`

## Updating the Application

1. Stop the current container:

   ```bash
   docker-compose down
   ```

2. Pull/copy new application files

3. Rebuild and restart:
   ```bash
   docker-compose up -d --build
   ```

## Backup and Restore

### Database Backup

Use SQL Server backup tools to backup the `SupportChatbot` database.

### Application Data

- Upload files are stored in `static/uploads/` (mounted as volume)
- Logs are stored in the `chatbot_logs` volume

## Security Considerations

- Use strong passwords for all accounts
- Keep SQL Server access restricted
- Use HTTPS in production
- Regularly update the Docker images
- Monitor logs for suspicious activity

## Support

For issues or questions, check the application logs first:

```bash
docker-compose logs -f chatbot
```
