#!/bin/bash
# Entrypoint script for Flask Chatbot application
# Handles database initialization, migrations, and application startup

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Flask Chatbot Application Startup ===${NC}"

# Function to wait for database
wait_for_db() {
    echo -e "${YELLOW}Waiting for database to be ready...${NC}"
    
    max_attempts=30
    attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        echo -e "${BLUE}Database connection attempt $attempt/$max_attempts${NC}"
        
        if python -c "
import sys
sys.path.append('/app')
try:
    from app import db
    from sqlalchemy import text
    
    # Test database connection
    with db.engine.connect() as conn:
        result = conn.execute(text('SELECT 1'))
        print('Database connection successful!')
    exit(0)
except Exception as e:
    print(f'Database connection failed: {e}')
    exit(1)
        "; then
            echo -e "${GREEN}Database is ready!${NC}"
            return 0
        fi
        
        echo -e "${YELLOW}Database not ready yet. Waiting 5 seconds...${NC}"
        sleep 5
        attempt=$((attempt + 1))
    done
    
    echo -e "${RED}Database connection failed after $max_attempts attempts${NC}"
    exit 1
}

# Function to initialize database
init_database() {
    echo -e "${YELLOW}Initializing database...${NC}"
    
    python -c "
import sys
sys.path.append('/app')
try:
    from app import app, db
    from models import User, Ticket, FAQ, Partner, EscalationLevel, SLARule, Organization
    
    with app.app_context():
        print('Creating database tables...')
        db.create_all()
        
        # Check if admin user exists
        from werkzeug.security import generate_password_hash
        admin_user = User.query.filter_by(email='admin@youcloudtech.com').first()
        
        if not admin_user:
            print('Creating default admin user...')
            admin_user = User(
                username='admin',
                email='admin@youcloudtech.com',
                password_hash=generate_password_hash('admin123'),
                is_admin=True,
                role='super_admin'
            )
            db.session.add(admin_user)
            
        # Create default organization if not exists
        default_org = Organization.query.filter_by(name='YouCloudTech').first()
        if not default_org:
            print('Creating default organization...')
            default_org = Organization(
                name='YouCloudTech',
                domain='youcloudtech.com',
                created_by=1
            )
            db.session.add(default_org)
            
        db.session.commit()
        print('Database initialization completed successfully!')
        
except Exception as e:
    print(f'Database initialization failed: {e}')
    import traceback
    traceback.print_exc()
    exit(1)
    "
}

# Function to compile translations
compile_translations() {
    echo -e "${YELLOW}Compiling translations...${NC}"
    
    if [ -d "/app/translations" ]; then
        find /app/translations -name "*.po" -exec pybabel compile -f -d /app/translations -D messages {} + || true
        echo -e "${GREEN}Translations compiled successfully!${NC}"
    else
        echo -e "${YELLOW}No translations directory found, skipping...${NC}"
    fi
}

# Function to run health check
health_check() {
    echo -e "${YELLOW}Running application health check...${NC}"
    
    python -c "
import sys
sys.path.append('/app')
try:
    from app import app
    
    with app.app_context():
        # Basic import test
        from models import User, Ticket
        print('Application modules loaded successfully!')
        
    # Test Flask app creation
    test_client = app.test_client()
    response = test_client.get('/health')
    
    if response.status_code == 200:
        print('Application health check passed!')
    else:
        print(f'Health check returned status: {response.status_code}')
        
except Exception as e:
    print(f'Health check failed: {e}')
    import traceback
    traceback.print_exc()
    exit(1)
    "
}

# Main execution flow
main() {
    echo -e "${BLUE}Starting application initialization...${NC}"
    
    # Wait for database to be available
    wait_for_db
    
    # Initialize database
    init_database
    
    # Compile translations
    compile_translations
    
    # Run health check
    health_check
    
    echo -e "${GREEN}Application initialization completed successfully!${NC}"
    echo -e "${BLUE}Starting Flask application...${NC}"
    
    # Execute the main command
    exec "$@"
}

# Add health endpoint route for health checks
create_health_endpoint() {
    cat > /tmp/health_routes.py << 'EOF'
# Health check routes for container
@app.route('/health')
def health_check():
    """Health check endpoint for container orchestration"""
    try:
        # Test database connection
        from sqlalchemy import text
        with db.engine.connect() as conn:
            conn.execute(text('SELECT 1'))
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0',
            'database': 'connected'
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }), 503

@app.route('/readiness')
def readiness_check():
    """Readiness check endpoint"""
    try:
        # More comprehensive checks
        from models import User
        user_count = User.query.count()
        
        return jsonify({
            'status': 'ready',
            'timestamp': datetime.utcnow().isoformat(),
            'user_count': user_count
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'not_ready',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }), 503
EOF
    
    # Append health routes to app.py if not already present
    if ! grep -q "/health" /app/app.py; then
        echo -e "${YELLOW}Adding health check endpoints...${NC}"
        cat /tmp/health_routes.py >> /app/app.py
    fi
}

# Create health endpoint
create_health_endpoint

# Run main function
main "$@"
