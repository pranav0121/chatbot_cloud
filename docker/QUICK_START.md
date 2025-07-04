# 🚀 QUICK START INTEGRATION GUIDE

**For the person deploying this application - everything you need to know in 2 minutes**

## ⚡ TL;DR - Just Want It Running?

```bash
# 1. Copy this project to your server
# 2. Create MSSQL database called "SupportChatbot"
# 3. Run this command:
cd docker
.\complete-deployment.bat    # Windows
# OR
./complete-deployment.sh     # Linux/Mac
```

**That's it! The script does everything automatically.**

---

## 🗄️ Database Requirements (5 minutes setup)

### Create Database & User

```sql
-- 1. Create database
CREATE DATABASE SupportChatbot;

-- 2. Create user (replace password)
USE master;
CREATE LOGIN chatbot_user WITH PASSWORD = 'YourPassword123!';
USE SupportChatbot;
CREATE USER chatbot_user FOR LOGIN chatbot_user;
ALTER ROLE db_owner ADD MEMBER chatbot_user;
```

### Enable TCP/IP Access

1. Open **SQL Server Configuration Manager**
2. Go to **SQL Server Network Configuration** → **Protocols**
3. **Enable TCP/IP**
4. **Restart SQL Server service**

---

## ⚙️ Configuration (2 minutes)

Edit `.env` file in project root:

```env
# Your MSSQL server details
DB_SERVER=192.168.1.100        # Your server IP
DB_DATABASE=SupportChatbot      # Don't change
DB_USERNAME=chatbot_user        # Don't change
DB_PASSWORD=YourPassword123!    # Your password

SECRET_KEY=change-this-to-random-32-chars
```

---

## 🏃‍♂️ Deployment Options

### Option 1: One-Click (Recommended)

```bash
cd docker
.\complete-deployment.bat    # Does everything automatically
```

### Option 2: Docker Compose (Production)

```bash
cd docker
docker-compose up -d
```

### Option 3: Manual

```bash
docker build -f docker/Dockerfile -t chatbot-app .
docker run -d --name chatbot-app -p 5000:5000 --env-file .env chatbot-app
```

---

## ✅ Verification

After deployment:

1. **Open browser**: http://localhost:5000
2. **Test database**: http://localhost:5000/api/database/test
3. **Admin panel**: http://localhost:5000/admin (admin@youcloudtech.com / admin123)

---

## 🆘 Troubleshooting

### Common Issues

| Issue                      | Solution                                                |
| -------------------------- | ------------------------------------------------------- |
| Database connection failed | Check SQL Server is running, TCP/IP enabled             |
| Port 5000 in use           | `docker stop chatbot-app` or use different port         |
| Container won't start      | Check `.env` file, view logs: `docker logs chatbot-app` |
| Build fails                | Clear Docker cache: `docker system prune -a`            |

### Emergency Commands

```bash
# View logs
docker logs chatbot-app

# Restart application
docker restart chatbot-app

# Stop everything
docker stop chatbot-app
docker rm chatbot-app
```

---

## 📞 Self-Help Resources

1. **Full documentation**: `docker/README.md`
2. **Application logs**: `docker logs chatbot-app`
3. **Health check**: http://localhost:5000/api/database/test
4. **Validation script**: `python docker/validate-deployment.py`

---

**🎯 99% of deployments work with the one-click script. If you have issues, check the logs first.**
