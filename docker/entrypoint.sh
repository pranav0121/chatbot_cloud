#!/bin/bash
set -e

echo "🚀 Starting chatbot application..."
echo ""
echo ""
echo "==================== DATABASE CHECKS ===================="
echo ""

# Check if we should skip database checks
if [ "${SKIP_DB_CHECK}" = "true" ]; then
    echo "⏭️  Skipping database checks (SKIP_DB_CHECK=true)"
    echo ""
else
    # Wait for database to be ready (if using external DB)
    echo "🔍 Checking database connection..."
    python -c "
from config import Config
from sqlalchemy import create_engine
import time
import sys

config = Config()
max_retries = 30
retry_count = 0

while retry_count < max_retries:
    try:
        engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
        connection = engine.connect()
        connection.close()
        print('✅ Database connection successful!')
        break
    except Exception as e:
        retry_count += 1
        print(f'⚠️  Database connection attempt {retry_count}/{max_retries} failed: {str(e)}')
        if retry_count >= max_retries:
            print('❌ Failed to connect to database after maximum retries')
            sys.exit(1)
        time.sleep(2)
"
fi

echo ""
echo "==================== APPLICATION STARTUP ===================="
echo ""

# Run database migrations if needed
echo "🗄️  Running database setup..."
python -c "
try:
    from database import db
    from app import app
    with app.app_context():
        db.create_all()
        print('✅ Database tables created/updated successfully')
except Exception as e:
    print(f'⚠️  Database setup warning: {str(e)}')
    # Don't exit on database setup errors - let the app handle it
"

# Start the Flask application
echo ""
echo "🚀 Starting Flask application on port 5000..."
exec python app.py
