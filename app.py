from app import create_app, db
from app.models.user import User
from app.models.complaint import Complaint
from app.models.message import Message
from app.models.attachment import Attachment
from app.models.faq import FAQ
import os

app = create_app(os.getenv('FLASK_ENV', 'development'))

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Complaint': Complaint,
        'Message': Message,
        'Attachment': Attachment,
        'FAQ': FAQ
    }

@app.cli.command()
def init_db():
    """Initialize the database."""
    db.create_all()
    print('Database initialized.')

@app.cli.command()
def create_admin():
    """Create admin user."""
    from werkzeug.security import generate_password_hash
    
    admin_email = app.config['ADMIN_EMAIL']
    admin_password = app.config['ADMIN_PASSWORD']
    
    # Check if admin already exists
    admin = User.query.filter_by(email=admin_email).first()
    if admin:
        print(f'Admin user {admin_email} already exists.')
        return
    
    # Create admin user
    admin = User(
        name='Administrator',
        email=admin_email,
        password_hash=generate_password_hash(admin_password),
        role='admin',
        language='en'
    )
    
    db.session.add(admin)
    db.session.commit()
    print(f'Admin user created: {admin_email}')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
