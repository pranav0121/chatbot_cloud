# MSSQL Docker Setup for Ops Team

This documentation explains how to set up, initialize, and health-check the Microsoft SQL Server (MSSQL) database for the chatbot project using Docker.

## Folder Contents
- `Dockerfile.db`: Dockerfile for building the MSSQL container.
- `docker-compose.db.yml`: Compose file to run the MSSQL container.
- `init-db.sql`: SQL script to initialize the database and create the `Users` table.
- `healthcheck.sql`: Simple SQL script to check MSSQL health.
- `wait-for-mssql.sh`: Script to wait for MSSQL readiness (for use in orchestration).
- `.env.docker`: Environment variables for connecting to the MSSQL container.

## Prerequisites
- Docker and Docker Compose installed on your machine.

## Steps

### 1. Build and Start the MSSQL Container
```sh
cd docker_db
# Build and start the MSSQL container
docker compose -f docker-compose.db.yml up -d --build
```

### 2. Check MSSQL Health
You can run the health check SQL script using a tool like Azure Data Studio, DBeaver, or sqlcmd:
```sql
-- In your SQL client, connect to localhost:1433 with username 'sa' and password 'YourStrong!Passw0rd'
-- Then run:
SELECT 1 AS HealthCheck, GETDATE() AS CheckedAt;
```

### 3. Initialize the Database
Run the `init-db.sql` script in your SQL client to create the database and tables:
```sh
# Example using sqlcmd (if installed):
sqlcmd -S localhost -U sa -P YourStrong!Passw0rd -i init-db.sql
```

### 4. Environment Variables
Use the `.env.docker` file for application database connectivity:
```
DB_SERVER=localhost
DB_DATABASE=SupportChatbot
DB_USERNAME=sa
DB_PASSWORD=YourStrong!Passw0rd
DB_USE_WINDOWS_AUTH=False
```

### 5. Stopping the Container
```sh
docker compose -f docker-compose.db.yml down
```

## Notes
- Change the default SA password in production.
- The `wait-for-mssql.sh` script can be used in multi-container setups to ensure the app waits for MSSQL to be ready.
- For any issues, check Docker logs:
  ```sh
  docker logs chatbot-mssql
  ```

---
For further assistance, contact the development team.
