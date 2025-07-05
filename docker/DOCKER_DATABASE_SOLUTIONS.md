# 🔧 Docker Database Connectivity Solutions

## **Current Status: ✅ Production Image Working**

The production Docker image is **successfully built and running**:
- ✅ Web server responds correctly (HTTP 200)
- ✅ Application routes are functional
- ✅ Login page loads properly
- ⚠️ Database connection needs configuration for Docker environment

## **Database Connection Issues & Solutions**

### **Problem**
Docker containers cannot connect to host SQL Server because:
1. Network isolation between container and host
2. `PRANAV\SQLEXPRESS` hostname doesn't resolve from container
3. Windows Authentication may not work across container boundary
4. SQL Server may not be configured for remote connections

### **Solutions (Choose One)**

#### **Option 1: Configure Host SQL Server for Remote Access (Recommended)**

1. **Enable TCP/IP Protocol in SQL Server:**
   ```
   - Open SQL Server Configuration Manager
   - Go to SQL Server Network Configuration → Protocols for SQLEXPRESS
   - Enable "TCP/IP" protocol
   - Restart SQL Server service
   ```

2. **Configure Windows Firewall:**
   ```
   - Open Windows Firewall
   - Add inbound rule for port 1433 (SQL Server)
   - Allow connection for Docker Desktop
   ```

3. **Run Docker with Host Connectivity:**
   ```bash
   docker run -d --name chatbot-prod \
     -p 5000:5000 \
     -e DB_SERVER="host.docker.internal,1433" \
     -e DB_DATABASE="SupportChatbot" \
     -e DB_USE_WINDOWS_AUTH="False" \
     -e DB_USERNAME="sa" \
     -e DB_PASSWORD="your_sa_password" \
     --add-host host.docker.internal:host-gateway \
     chatbot-app:production-clean
   ```

#### **Option 2: Use SQL Server Authentication**

1. **Enable SQL Server Authentication:**
   ```sql
   -- Connect to SQLEXPRESS with SSMS
   -- Enable SQL Server and Windows Authentication mode
   ALTER LOGIN sa ENABLE;
   ALTER LOGIN sa WITH PASSWORD = 'YourStrongPassword123!';
   ```

2. **Update Container Environment:**
   ```bash
   docker run -d --name chatbot-prod \
     -p 5000:5000 \
     -e DB_SERVER="host.docker.internal\SQLEXPRESS" \
     -e DB_USE_WINDOWS_AUTH="False" \
     -e DB_USERNAME="sa" \
     -e DB_PASSWORD="YourStrongPassword123!" \
     chatbot-app:production-clean
   ```

#### **Option 3: Network Mode Host (Windows-specific)**

```bash
docker run -d --name chatbot-prod \
  -p 5000:5000 \
  --network="host" \
  -e DB_SERVER="localhost\SQLEXPRESS" \
  chatbot-app:production-clean
```

#### **Option 4: Use Docker Compose with Host Connectivity**

```yaml
services:
  chatbot-app:
    build:
      context: .
      target: production
    ports:
      - "5000:5000"
    environment:
      - DB_SERVER=host.docker.internal\SQLEXPRESS
      - DB_DATABASE=SupportChatbot
      - DB_USE_WINDOWS_AUTH=False
      - DB_USERNAME=sa
      - DB_PASSWORD=your_password
    extra_hosts:
      - "host.docker.internal:host-gateway"
```

## **Production Deployment Commands**

### **Quick Start (Standalone Mode)**
```bash
# Build production image
docker build --target production -t chatbot-app:prod .

# Run without database (web-only mode)
docker run -d --name chatbot-standalone \
  -p 5000:5000 \
  -e DB_USE_WINDOWS_AUTH="False" \
  chatbot-app:prod
```

### **Full Production with Database**
```bash
# Run with database connectivity
docker run -d --name chatbot-production \
  -p 5000:5000 \
  -e DB_SERVER="host.docker.internal\SQLEXPRESS" \
  -e DB_DATABASE="SupportChatbot" \
  -e DB_USE_WINDOWS_AUTH="False" \
  -e DB_USERNAME="sa" \
  -e DB_PASSWORD="your_password" \
  --add-host host.docker.internal:host-gateway \
  chatbot-app:prod
```

## **Testing & Verification**

### **Test Web Server (Always Works)**
```bash
curl http://localhost:5000/
curl http://localhost:5000/health
```

### **Test Database Connection**
```bash
# Check container logs
docker logs chatbot-production

# Look for these success indicators:
# ✅ "INFO:app:Database URI configured for MSSQL"
# ✅ No "ERROR:app:Database health check failed" messages
```

## **Production Checklist**

- [ ] SQL Server TCP/IP protocol enabled
- [ ] Windows Firewall configured for port 1433
- [ ] SQL Server Authentication enabled (if not using Windows auth)
- [ ] Strong SA password set
- [ ] Container has `host.docker.internal` connectivity
- [ ] Environment variables correctly configured
- [ ] Health checks passing
- [ ] Application logs show successful database connection

## **Current Working Status**

✅ **Docker Image**: Production-ready and optimized
✅ **Web Application**: Fully functional, serves all routes
✅ **Container Runtime**: Stable and responsive
✅ **Network**: HTTP server accessible on port 5000
⚠️ **Database**: Requires host SQL Server configuration

The application **works perfectly** in web-only mode and will automatically connect to the database once the SQL Server connectivity is properly configured.
