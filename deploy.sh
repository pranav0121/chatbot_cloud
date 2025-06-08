#!/bin/bash

# Production deployment script for YouCloudPay Chatbot

set -e

echo "🚀 Starting YouCloudPay Chatbot deployment..."

# Load environment variables
if [ -f .env.production ]; then
    export $(cat .env.production | grep -v '#' | xargs)
fi

# Build and start services
echo "📦 Building Docker images..."
docker-compose -f docker-compose.yml build --no-cache

echo "🗄️ Setting up database..."
docker-compose up -d db redis

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 10

# Run database migrations
echo "🔄 Running database migrations..."
docker-compose run --rm web python -c "
from app import create_app, db
from app.models.user import User

app = create_app('production')
with app.app_context():
    db.create_all()
    
    # Create admin user if not exists
    admin_email = app.config['ADMIN_EMAIL']
    admin_password = app.config['ADMIN_PASSWORD']
    
    admin = User.query.filter_by(email=admin_email).first()
    if not admin:
        admin = User(
            name='Administrator',
            email=admin_email,
            role='admin',
            language='en',
            is_active=True
        )
        admin.set_password(admin_password)
        db.session.add(admin)
        db.session.commit()
        print(f'Admin user created: {admin_email}')
    else:
        print(f'Admin user exists: {admin_email}')
"

echo "🌐 Starting all services..."
docker-compose up -d

echo "🔍 Checking service health..."
sleep 15

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ All services are running successfully!"
    echo ""
    echo "🎉 YouCloudPay Chatbot is now deployed!"
    echo "📱 Access the application at: http://localhost"
    echo "🔐 Admin login: admin@youcloudpay.com / secure-admin-password"
    echo ""
    echo "📊 To view logs: docker-compose logs -f"
    echo "🛑 To stop: docker-compose down"
    echo "🔄 To restart: docker-compose restart"
else
    echo "❌ Some services failed to start. Check logs:"
    docker-compose logs
    exit 1
fi
