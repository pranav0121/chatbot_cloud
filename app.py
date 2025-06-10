from flask import Flask, render_template, request, jsonify, send_from_directory, url_for, redirect, session, flash
from flask_login import LoginManager, login_required, current_user, UserMixin
from flask_babel import Babel, _
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pyodbc
import logging
from config import Config
import os
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from PIL import Image
import uuid
from sqlalchemy import text
from sqlalchemy.sql import case
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
config_obj = Config()
app.config.from_object(config_obj)

# Initialize Flask-Babel for i18n with fallback handling
app.config['BABEL_DEFAULT_LOCALE'] = 'en'  # English as default language
app.config['BABEL_SUPPORTED_LOCALES'] = [
    'en', 'es', 'ar', 'hi', 'it', 'ja', 'ko', 'pt', 'ru', 'ur', 'zh'  # All working languages with English first
]
app.config['LANGUAGES'] = {
    'en': 'English',
    'es': 'Español',
    'ar': 'العربية',
    'hi': 'हिन्दी',
    'it': 'Italiano',
    'ja': '日本語',
    'ko': '한국어',
    'pt': 'Português',
    'ru': 'Русский',
    'ur': 'اردو',
    'zh': '中文'
}
babel = Babel(app)

# Add error handling for translation loading
@app.errorhandler(UnicodeDecodeError)
def handle_unicode_error(error):
    """Handle Unicode decode errors in translation files"""
    logger.error(f"Unicode decode error in translations: {str(error)}")
    # Redirect to Spanish (known working language) with error message
    return redirect(url_for('index', lang='es', _error='translation'))

def get_available_languages():
    """Return only languages with properly working translation files"""
    # Include English plus languages that we know have working .mo files (>1000 bytes)
    working_languages = ['en', 'ar', 'es', 'hi', 'it', 'ja', 'ko', 'pt', 'ru', 'ur', 'zh']
    
    # Verify they exist and have substantial content
    translations_dir = os.path.join(app.root_path, 'translations')
    verified_langs = []
    
    if os.path.exists(translations_dir):
        for lang_code in working_languages:
            mo_file = os.path.join(translations_dir, lang_code, 'LC_MESSAGES', 'messages.mo')
            if os.path.exists(mo_file):
                try:
                    # Only include languages with substantial .mo files (actual translations)
                    if os.path.getsize(mo_file) > 500:  # Files with real translations
                        verified_langs.append(lang_code)
                except OSError:
                    continue
    
    # Always include English as the core language
    if 'en' not in verified_langs:
        verified_langs.append('en')
    
    return sorted(verified_langs)

@app.context_processor
def inject_conf_var():
    # Inject available languages and locale into template context
    return dict(
        available_languages=get_available_languages(),
        get_locale=get_locale
    )

# Flask-Login setup
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'
login_manager.init_app(app)

# Add error handlers for authentication
@app.errorhandler(401)
def unauthorized(error):
    return redirect(url_for('auth.login'))

# Handle unauthorized access
@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('auth.login'))

# Babel locale selector with error handling
@babel.localeselector
def get_locale():
    # Check URL parameter first
    requested_lang = request.args.get('lang')
    available_langs = get_available_languages()
    
    if requested_lang and requested_lang in available_langs:
        return requested_lang
    
    # Use user's preferred language if authenticated and available
    if current_user.is_authenticated and hasattr(current_user, 'PreferredLanguage') and current_user.PreferredLanguage:
        if current_user.PreferredLanguage in available_langs:
            return current_user.PreferredLanguage
    
    # Fallback to best match from available languages, default to English
    if available_langs:
        best_match = request.accept_languages.best_match(available_langs)
        return best_match if best_match else ('en' if 'en' in available_langs else available_langs[0])
    else:
        return 'en'  # Ultimate fallback to English

@app.route('/set_language/<lang_code>')
def set_language(lang_code):
    from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
    
    # Change user preferred language
    available_langs = get_available_languages()
    if lang_code in available_langs:
        if current_user.is_authenticated:
            # Save to user profile for authenticated users
            current_user.PreferredLanguage = lang_code
            try:
                db.session.commit()
            except:
                db.session.rollback()
        
        # Redirect with language parameter for session-based language switching
        referrer = request.referrer or url_for('index')
        
        # Parse the URL and update/add the lang parameter properly
        parsed_url = urlparse(referrer)
        query_params = parse_qs(parsed_url.query)
        
        # Update or add the lang parameter
        query_params['lang'] = [lang_code]
        
        # Reconstruct the URL with updated parameters
        new_query = urlencode(query_params, doseq=True)
        new_url = urlunparse((
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            parsed_url.params,
            new_query,
            parsed_url.fragment
        ))
        
        return redirect(new_url)
    
    return redirect(request.referrer or url_for('index'))

# Enhanced database connection with better error handling
def setup_database():
    """Setup database connection with comprehensive error handling"""
    try:
        app.config['SQLALCHEMY_DATABASE_URI'] = config_obj.SQLALCHEMY_DATABASE_URI
        logger.info(f"Database URI configured: {config_obj.SQLALCHEMY_DATABASE_URI}")
        return True
    except Exception as e:
        logger.error(f"Failed to configure database URI: {e}")
        try:
            app.config['SQLALCHEMY_DATABASE_URI'] = config_obj.SQLALCHEMY_DATABASE_URI_FALLBACK
            logger.warning("Falling back to SQLite database")
            return True
        except Exception as fallback_error:
            logger.error(f"Even fallback database failed: {fallback_error}")
            return False

# Setup database
if not setup_database():
    logger.critical("Database setup failed completely")
    exit(1)

# Configure Flask-SocketIO - use default threading mode
from flask_socketio import SocketIO, emit, join_room, leave_room
socketio = SocketIO(app, cors_allowed_origins="*")
db = SQLAlchemy(app)

# SocketIO event handlers for real-time chat
@socketio.on('join_room')
def handle_join_room(data):
    room = f"ticket_{data['ticket_id']}"
    join_room(room)

@socketio.on('leave_room')
def handle_leave_room(data):
    room = f"ticket_{data['ticket_id']}"
    leave_room(room)

@socketio.on('send_message')
def handle_send_message(data):
    ticket_id = data.get('ticket_id')
    content = data.get('content')
    is_admin = data.get('is_admin', False)
    sender_id = getattr(current_user, 'UserID', None)
    # Save message to database
    msg = Message(TicketID=ticket_id, SenderID=sender_id,
                  Content=content, IsAdminReply=is_admin)
    db.session.add(msg)
    # Update ticket status and timestamp
    ticket = Ticket.query.get(ticket_id)
    if ticket:
        ticket.UpdatedAt = datetime.utcnow()
        if not is_admin and ticket.Status == 'open':
            ticket.Status = 'in_progress'
    db.session.commit()
    # Handle attachments if present
    attachments_info = []
    if data.get('attachments'):
        for att in data.get('attachments'):
            # Link existing Attachment record to this message
            attachment = Attachment.query.get(att.get('id'))
            if attachment:
                attachment.MessageID = msg.MessageID
                db.session.add(attachment)
                attachments_info.append({
                    'id': attachment.AttachmentID,
                    'original_name': attachment.OriginalName,
                    'url': url_for('uploaded_file', filename=attachment.StoredName, _external=False),
                    'file_size': attachment.FileSize,
                    'mime_type': attachment.MimeType
                })
    db.session.commit()
    # Prepare message payload
    msg_data = {
        'ticket_id': ticket_id,
        'id': msg.MessageID,
        'content': msg.Content,
        'is_admin': msg.IsAdminReply,
        'created_at': msg.CreatedAt.isoformat(),
        'attachments': attachments_info
    }
    # Broadcast to room
    emit('new_message', msg_data, room=f"ticket_{ticket_id}")

# Flask-Login: user loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Enhanced session management
@app.teardown_appcontext
def close_db(error):
    """Close database connections after each request"""
    try:
        db.session.remove()
    except Exception as e:
        logger.error(f"Error closing database session: {str(e)}")

@app.teardown_request
def close_db_session(exception):
    """Ensure database session is properly closed"""
    try:
        if exception:
            db.session.rollback()
        db.session.close()
    except Exception as e:
        logger.error(f"Error in teardown_request: {str(e)}")

# Database health check function
def check_database_health():
    """Check if database is accessible and working"""
    try:
        db.session.execute(text('SELECT 1'))
        db.session.commit()
        return True, "Database connection healthy"
    except Exception as e:
        error_msg = f"Database health check failed: {str(e)}"
        logger.error(error_msg)
        return False, error_msg

# File upload configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Database Models
class User(UserMixin, db.Model):
    __tablename__ = 'Users'
    UserID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100), nullable=False)
    Email = db.Column(db.String(255), unique=True, nullable=False)
    PasswordHash = db.Column(db.String(255), nullable=False)
    OrganizationName = db.Column(db.String(200), nullable=False)
    Position = db.Column(db.String(100), nullable=True)
    PriorityLevel = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    Phone = db.Column(db.String(20), nullable=True)
    Department = db.Column(db.String(100), nullable=True)
    PreferredLanguage = db.Column(db.String(10), default='en')
    IsActive = db.Column(db.Boolean, default=True)
    IsAdmin = db.Column(db.Boolean, default=False)
    LastLogin = db.Column(db.DateTime, nullable=True)
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)

    def get_id(self):
        return str(self.UserID)
    
    def get_priority_weight(self):
        """Return numeric weight for priority sorting"""
        priority_weights = {
            'critical': 4,
            'high': 3,
            'medium': 2,
            'low': 1
        }
        return priority_weights.get(self.PriorityLevel, 2)

class Category(db.Model):
    __tablename__ = 'Categories'
    CategoryID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(50), nullable=False)
    Team = db.Column(db.String(50), nullable=False)
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)

class Ticket(db.Model):
    __tablename__ = 'Tickets'
    TicketID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'))
    CategoryID = db.Column(db.Integer, db.ForeignKey('Categories.CategoryID'))
    Subject = db.Column(db.String(255), nullable=False)
    Priority = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    Status = db.Column(db.String(20), default='open')
    OrganizationName = db.Column(db.String(200), nullable=True)  # Cached from user for easier admin viewing
    CreatedBy = db.Column(db.String(100), nullable=True)  # Cached user name for easier admin viewing
    AssignedTo = db.Column(db.Integer, db.ForeignKey('Users.UserID'), nullable=True)  # Admin who handles this
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)
    UpdatedAt = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[UserID], backref='tickets')
    assigned_admin = db.relationship('User', foreign_keys=[AssignedTo], backref='assigned_tickets')
    
    def get_priority_weight(self):
        """Return numeric weight for priority sorting"""
        priority_weights = {
            'critical': 4,
            'high': 3,
            'medium': 2,
            'low': 1
        }
        return priority_weights.get(self.Priority, 2)

class Message(db.Model):
    __tablename__ = 'Messages'
    MessageID = db.Column(db.Integer, primary_key=True)
    TicketID = db.Column(db.Integer, db.ForeignKey('Tickets.TicketID'))
    SenderID = db.Column(db.Integer, db.ForeignKey('Users.UserID'))
    Content = db.Column(db.Text, nullable=False)
    IsAdminReply = db.Column(db.Boolean, default=False)
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)

class CommonQuery(db.Model):
    __tablename__ = 'CommonQueries'
    QueryID = db.Column(db.Integer, primary_key=True)
    CategoryID = db.Column(db.Integer, db.ForeignKey('Categories.CategoryID'))
    Question = db.Column(db.String(255), nullable=False)
    Solution = db.Column(db.Text, nullable=False)
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)
    UpdatedAt = db.Column(db.DateTime, default=datetime.utcnow)

class Feedback(db.Model):
    __tablename__ = 'Feedback'
    FeedbackID = db.Column(db.Integer, primary_key=True)
    TicketID = db.Column(db.Integer, db.ForeignKey('Tickets.TicketID'))
    Rating = db.Column(db.Integer, nullable=False)
    Comment = db.Column(db.Text)
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)

class Attachment(db.Model):
    __tablename__ = 'Attachments'
    AttachmentID = db.Column(db.Integer, primary_key=True)
    MessageID = db.Column(db.Integer, db.ForeignKey('Messages.MessageID'))
    OriginalName = db.Column(db.String(255), nullable=False)
    StoredName = db.Column(db.String(255), nullable=False)
    FileSize = db.Column(db.Integer, nullable=False)
    MimeType = db.Column(db.String(100), nullable=False)
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)

# Register authentication blueprint after models are defined
from auth import auth_bp
app.register_blueprint(auth_bp)

# Admin authentication helper function
def admin_required(f):
    """Decorator to require admin authentication for API endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return jsonify({
                'error': 'Admin authentication required',
                'message': 'Please log in as an administrator to access this resource'
            }), 401
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/test')
def test():
    return jsonify({'status': 'Application is working!', 'message': 'Test route successful'})

@app.route('/template-test')
def template_test():
    try:
        return render_template('simple_test.html')
    except Exception as e:
        return f"Template error: {str(e)}"

@app.route('/')
def index():
    if current_user.is_authenticated:
        try:
            return render_template('index.html')
        except (UnicodeDecodeError, UnicodeError) as e:
            # Handle translation file encoding errors
            logger.error(f"Translation encoding error: {str(e)}")
            # Force fallback to Spanish locale and retry
            try:
                from flask import session
                session['language'] = 'es'
                return redirect(url_for('index', lang='es'))
            except:
                return f"Translation error occurred. Please try refreshing the page."
        except Exception as e:
            logger.error(f"Template rendering error: {str(e)}")
            return f"Error loading page: {str(e)}"
    else:
        return redirect(url_for('auth.login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('index.html')

@app.route('/faq')
@login_required
def faq():
    return render_template('faq.html')

def optimize_image(image_path, max_size=(800, 800), quality=85):
    """Optimize uploaded image to reduce file size"""
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # Resize if larger than max_size
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save optimized version
            img.save(image_path, 'JPEG', quality=quality, optimize=True)
            return True
    except Exception as e:
        logger.error(f"Error optimizing image: {e}")
        return False

def save_file(file):
    """Save uploaded file and return file info"""
    if not file or not allowed_file(file.filename):
        return None
    
    try:
        # Generate unique filename
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{file_ext}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Save file
        file.save(file_path)
        
        # Optimize if it's an image
        if file_ext in {'jpg', 'jpeg', 'png'}:
            optimize_image(file_path)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        return {
            'original_name': filename,
            'stored_name': unique_filename,
            'file_size': file_size,
            'mime_type': file.mimetype or f'image/{file_ext}',
            'url': url_for('uploaded_file', filename=unique_filename, _external=False)
        }
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        return None

@app.route('/api/categories', methods=['GET'])
def get_categories():
    try:
        print("Getting categories...")
        
        # First, ensure the database has categories
        count = Category.query.count()
        print(f"Current category count: {count}")
        
        if count == 0:
            print("No categories found, creating default categories...")
            # Insert default categories if none exist
            default_categories = [
                Category(Name='Payments', Team='Billing'),
                Category(Name='Product Issues', Team='Product'),
                Category(Name='Technical Glitches', Team='Tech'),
                Category(Name='General Inquiries', Team='General')
            ]
            
            for cat in default_categories:
                db.session.add(cat)
            
            try:
                db.session.commit()
                print("Default categories created successfully")
                
                # Add some common queries
                setup_common_queries()
                print("Common queries setup completed")
            except Exception as e:
                print(f"Error creating categories: {e}")
                db.session.rollback()
                return jsonify({"error": "Failed to create categories"}), 500
        
        categories = Category.query.all()
        print(f"Found {len(categories)} categories")
        
        result = [{'id': c.CategoryID, 'name': c.Name} for c in categories]
        print("Categories result:", result)
        
        return jsonify(result)
        
    except Exception as e:
        print("Error in get_categories:", str(e))
        db.session.rollback()
        
        # Return default categories as fallback
        default_result = [
            {'id': 1, 'name': 'Payments'},
            {'id': 2, 'name': 'Product Issues'},
            {'id': 3, 'name': 'Technical Glitches'},
            {'id': 4, 'name': 'General Inquiries'}
        ]
        print("Returning fallback categories")
        return jsonify(default_result)

def setup_common_queries():
    """Setup default common queries for each category"""
    try:
        categories = Category.query.all()
        
        common_queries_data = {
            'Payments': [
                {
                    'question': 'How do I update my payment method?',
                    'solution': 'You can update your payment method by going to Account Settings > Billing > Payment Methods. Click "Add New Method" or "Edit" next to your existing method.'
                },
                {
                    'question': 'Why was my payment declined?',
                    'solution': 'Payment declines can happen due to insufficient funds, expired cards, or bank security measures. Please check with your bank or try a different payment method.'
                },
                {
                    'question': 'How do I get a refund?',
                    'solution': 'Refunds can be requested within 30 days of purchase. Please contact our billing team with your order number and reason for refund.'
                }
            ],
            'Product Issues': [
                {
                    'question': 'The product is not working as expected',
                    'solution': 'Please try refreshing the page or clearing your browser cache. If the issue persists, try using a different browser or device.'
                },
                {
                    'question': 'I can\'t find a specific feature',
                    'solution': 'Our features are organized in the main navigation menu. You can also use the search function or check our help documentation for detailed guides.'
                },
                {
                    'question': 'How do I report a bug?',
                    'solution': 'You can report bugs by clicking the "Report Issue" button in the app or by sending us a detailed description of the problem including steps to reproduce it.'
                }
            ],
            'Technical Glitches': [
                {
                    'question': 'The page won\'t load properly',
                    'solution': 'Try refreshing the page (Ctrl+F5), clearing your browser cache, or disabling browser extensions. If the problem continues, try a different browser.'
                },
                {
                    'question': 'I\'m getting error messages',
                    'solution': 'Please note down the exact error message and try refreshing the page. If it persists, clear your browser cache and cookies, then try again.'
                },
                {
                    'question': 'The app is running slowly',
                    'solution': 'Slow performance can be due to network issues, browser cache, or high server load. Try closing other browser tabs and refreshing the page.'
                }
            ],
            'General Inquiries': [
                {
                    'question': 'How do I contact customer support?',
                    'solution': 'You can reach our support team through this chat, email us at support@company.com, or call our hotline during business hours.'
                },
                {
                    'question': 'What are your business hours?',
                    'solution': 'Our support team is available Monday to Friday, 9 AM to 6 PM EST. Emergency support is available 24/7 for critical issues.'
                },
                {
                    'question': 'How do I create an account?',
                    'solution': 'Click the "Sign Up" button on our homepage, fill in your details, verify your email address, and you\'re ready to get started!'
                }
            ]
        }
        
        for category in categories:
            if category.Name in common_queries_data:
                for query_data in common_queries_data[category.Name]:
                    # Check if query already exists
                    existing = CommonQuery.query.filter_by(
                        CategoryID=category.CategoryID, 
                        Question=query_data['question']
                    ).first()
                    
                    if not existing:
                        query = CommonQuery(
                            CategoryID=category.CategoryID,
                            Question=query_data['question'],
                            Solution=query_data['solution']
                        )
                        db.session.add(query)
        
        db.session.commit()
        print("Common queries setup completed")
        
    except Exception as e:
        print(f"Error setting up common queries: {str(e)}")
        db.session.rollback()

@app.route('/api/common-queries/<int:category_id>', methods=['GET'])
def get_common_queries(category_id):
    queries = CommonQuery.query.filter_by(CategoryID=category_id).all()
    return jsonify([{
        'id': q.QueryID,
        'question': q.Question,
        'solution': q.Solution
    } for q in queries])

@app.route('/api/tickets', methods=['POST'])
def create_ticket():
    try:
        logger.info("Creating new ticket...")
        data = request.json
        logger.info(f"Received data: {data}")
        
        if not data:
            logger.error("No data received")
            return jsonify({
                'status': 'error',
                'message': 'No data provided'
            }), 400
        
        # Validate required fields
        if not data.get('message'):
            logger.error("Message is required")
            return jsonify({
                'status': 'error',
                'message': 'Message is required'
            }), 400
        
        # Handle authenticated user vs guest user
        user = None
        if current_user.is_authenticated:
            # Use authenticated user
            user = current_user
            logger.info(f"Using authenticated user: {user.Name} from {user.OrganizationName}")
        else:
            # Create or get guest user (backward compatibility)
            if data.get('name') or data.get('email'):
                try:
                    # Check if user already exists
                    email = data.get('email')
                    if email:
                        user = User.query.filter_by(Email=email).first()
                    
                    if not user:
                        user = User(
                            Name=data.get('name', 'Anonymous'),
                            Email=data.get('email', ''),
                            OrganizationName=data.get('organization', 'Guest Organization'),
                            PriorityLevel=data.get('priority', 'medium')
                        )
                        db.session.add(user)
                        db.session.flush()  # Get the ID without committing
                    logger.info(f"Created/found guest user with ID: {user.UserID}")
                except Exception as e:
                    logger.error(f"Error creating user: {str(e)}")
                    db.session.rollback()
                    return jsonify({
                        'status': 'error',
                        'message': 'Error creating user'
                    }), 500
        
        # Get category ID - default to 1 if not provided
        category_id = data.get('category_id', 1)
        logger.info(f"Using category_id: {category_id}")
        
        # Determine ticket priority (use user's priority level by default)
        ticket_priority = data.get('priority', user.PriorityLevel if user else 'medium')
        
        # Create ticket with enhanced information
        try:
            ticket = Ticket(
                UserID=user.UserID if user else None,
                CategoryID=category_id,
                Subject=data.get('subject', 'Support Request'),
                Priority=ticket_priority,
                Status='open',
                OrganizationName=user.OrganizationName if user else data.get('organization', 'Unknown'),
                CreatedBy=user.Name if user else data.get('name', 'Anonymous')
            )
            db.session.add(ticket)
            db.session.flush()  # Get the ID without committing
            logger.info(f"Created ticket with ID: {ticket.TicketID}, Priority: {ticket_priority}, Organization: {ticket.OrganizationName}")
        except Exception as e:
            logger.error(f"Error creating ticket: {str(e)}")
            db.session.rollback()
            return jsonify({
                'status': 'error',
                'message': 'Error creating ticket'
            }), 500
          # Create initial message
        try:
            message = Message(
                TicketID=ticket.TicketID,
                SenderID=user.UserID if user else None,
                Content=data['message'],
                IsAdminReply=False
            )
            db.session.add(message)
            db.session.commit()
            logger.info(f"Created message with ID: {message.MessageID}")
        except Exception as e:
            logger.error(f"Error creating message: {str(e)}")
            db.session.rollback()
            return jsonify({
                'status': 'error',
                'message': 'Error creating message'
            }), 500
        
        logger.info(f"Successfully created ticket {ticket.TicketID} for organization {ticket.OrganizationName}")
        return jsonify({
            'ticket_id': ticket.TicketID,
            'user_id': user.UserID if user else None,
            'priority': ticket.Priority,
            'organization': ticket.OrganizationName,
            'status': 'success',
            'message': 'Ticket created successfully'
        })
        
    except Exception as e:
        logger.error(f"Unexpected error in create_ticket: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500

@app.route('/api/tickets/<int:ticket_id>/messages', methods=['GET', 'POST'])
def handle_messages(ticket_id):
    if request.method == 'GET':
        messages = Message.query.filter_by(TicketID=ticket_id).order_by(Message.CreatedAt).all()
        message_list = []
        
        for m in messages:
            # Get attachments for this message
            attachments = Attachment.query.filter_by(MessageID=m.MessageID).all()
            
            message_data = {
                'id': m.MessageID,
                'content': m.Content,
                'is_admin': m.IsAdminReply,
                'created_at': m.CreatedAt.isoformat(),
                'attachments': [{
                    'id': att.AttachmentID,
                    'original_name': att.OriginalName,
                    'url': f'/static/uploads/{att.StoredName}',
                    'file_size': att.FileSize,
                    'mime_type': att.MimeType
                } for att in attachments]
            }
            message_list.append(message_data)
        
        return jsonify(message_list)
    
    # POST new message
    data = request.json
    message = Message(
        TicketID=ticket_id,
        SenderID=data.get('user_id'),
        Content=data['content'],
        IsAdminReply=data.get('is_admin', False)
    )
    db.session.add(message)
      # Update ticket timestamp
    ticket = Ticket.query.get(ticket_id)
    if ticket:
        ticket.UpdatedAt = datetime.utcnow()
        if data.get('is_admin', False) and ticket.Status == 'open':
            ticket.Status = 'in_progress'
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message_id': message.MessageID
    })

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Save file
        file_info = save_file(file)
        if not file_info:
            return jsonify({'error': 'Failed to save file'}), 500
        
        return jsonify({
            'status': 'success',
            'file_info': file_info
        })
        
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        return jsonify({'error': 'Upload failed'}), 500

@app.route('/api/tickets/with-attachment', methods=['POST'])
def create_ticket_with_attachment():
    """Create ticket with file attachment"""
    try:
        # Get form data
        data = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'category_id': request.form.get('category_id'),
            'subject': request.form.get('subject'),
            'message': request.form.get('message')
        }
        
        # Validate required fields
        if not all([data['name'], data['email'], data['category_id'], data['message']]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Create or get user
        user = User.query.filter_by(Email=data['email']).first()
        if not user:
            user = User(Name=data['name'], Email=data['email'])
            db.session.add(user)
            db.session.flush()
        
        # Create ticket
        ticket = Ticket(
            UserID=user.UserID,
            CategoryID=int(data['category_id']),
            Subject=data.get('subject', 'Support Request'),
            Status='open'
        )
        db.session.add(ticket)
        db.session.flush()
        
        # Create message
        message = Message(
            TicketID=ticket.TicketID,
            SenderID=user.UserID,
            Content=data['message'],
            IsAdminReply=False
        )
        db.session.add(message)
        db.session.flush()
        
        # Handle file attachment if present
        if 'file' in request.files and request.files['file'].filename != '':
            file = request.files['file']
            if allowed_file(file.filename):
                file_info = save_file(file)
                if file_info:
                    attachment = Attachment(
                        MessageID=message.MessageID,
                        OriginalName=file_info['original_name'],
                        StoredName=file_info['stored_name'],
                        FileSize=file_info['file_size'],
                        MimeType=file_info['mime_type']                    )
                    db.session.add(attachment)
        
        db.session.commit()
        
        return jsonify({
            'ticket_id': ticket.TicketID,
            'user_id': user.UserID if user else None,
            'status': 'success',
            'message': 'Ticket created successfully'
        })
        
    except Exception as e:
        logger.error(f"Error creating ticket with attachment: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to create ticket'}), 500

@app.route('/api/tickets/<int:ticket_id>/messages/with-attachment', methods=['POST'])
def add_message_with_attachment(ticket_id):
    """Add message to existing ticket with optional attachment"""
    try:
        # Get form data
        content = request.form.get('content')
        user_id = request.form.get('user_id')
        is_admin = request.form.get('is_admin', 'false').lower() == 'true'
        
        if not content:
            return jsonify({'error': 'Message content required'}), 400
        
        # Create message
        message = Message(
            TicketID=ticket_id,
            SenderID=int(user_id) if user_id else None,
            Content=content,
            IsAdminReply=is_admin
        )
        db.session.add(message)
        db.session.flush()
        
        # Handle file attachment if present
        if 'file' in request.files and request.files['file'].filename != '':
            file = request.files['file']
            if allowed_file(file.filename):
                file_info = save_file(file)
                if file_info:
                    attachment = Attachment(
                        MessageID=message.MessageID,
                        OriginalName=file_info['original_name'],
                        StoredName=file_info['stored_name'],
                        FileSize=file_info['file_size'],
                        MimeType=file_info['mime_type']
                    )
                    db.session.add(attachment)
        
        # Update ticket timestamp
        ticket = Ticket.query.get(ticket_id)
        if ticket:
            ticket.UpdatedAt = datetime.utcnow()
            if is_admin and ticket.Status == 'open':
                ticket.Status = 'in_progress'
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message_id': message.MessageID
        })
        
    except Exception as e:
        logger.error(f"Error adding message with attachment: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to add message'}), 500

@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/admin')
def admin_dashboard():
    # Check if admin is authenticated
    from flask import session, redirect, url_for, flash
    
    if not session.get('admin_logged_in'):
        flash('Admin authentication required to access the dashboard.', 'error')
        return redirect(url_for('auth.admin_login'))
    
    return render_template('admin.html')

@app.route('/debug-admin')
def debug_admin():
    """Debug admin panel"""
    return render_template('debug_admin.html')

@app.route('/api/admin/dashboard-stats', methods=['GET'])
@admin_required
def get_dashboard_stats():
    try:
        logger.info("Loading dashboard stats...")
        
        # Test database connection first
        try:
            db.session.execute(text('SELECT 1'))
            logger.info("Database connection successful")
        except Exception as db_error:
            logger.error(f"Database connection failed: {str(db_error)}")
            return jsonify({
                "error": "Database connection failed",
                "details": str(db_error)
            }), 500
        
        # Get stats with detailed logging
        total_tickets = Ticket.query.count()
        logger.info(f"Total tickets: {total_tickets}")
        
        pending_tickets = Ticket.query.filter(Ticket.Status.in_(['open', 'in_progress'])).count()
        logger.info(f"Pending tickets: {pending_tickets}")
        
        resolved_tickets = Ticket.query.filter_by(Status='resolved').count()
        logger.info(f"Resolved tickets: {resolved_tickets}")
        
        active_chats = Ticket.query.filter(Ticket.Status.in_(['open', 'in_progress'])).count()
        logger.info(f"Active chats: {active_chats}")
        
        # Also get some sample tickets for debugging
        sample_tickets = Ticket.query.limit(5).all()
        logger.info(f"Sample tickets found: {len(sample_tickets)}")
        for ticket in sample_tickets:
            logger.info(f"Ticket {ticket.TicketID}: {ticket.Subject} - Status: {ticket.Status}")
        
        result = {
            'totalTickets': total_tickets,
            'pendingTickets': pending_tickets,
            'resolvedTickets': resolved_tickets,
            'activeChats': active_chats
        }
        
        logger.info(f"Dashboard stats result: {result}")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in get_dashboard_stats: {str(e)}", exc_info=True)
        return jsonify({
            "error": str(e),
            "message": "Failed to load dashboard statistics"
        }), 500

@app.route('/api/admin/recent-activity', methods=['GET'])
@admin_required
def get_recent_activity():
    try:
        # Get recent tickets and messages
        recent_tickets = db.session.query(Ticket, User, Category).join(
            User, Ticket.UserID == User.UserID, isouter=True
        ).join(
            Category, Ticket.CategoryID == Category.CategoryID
        ).order_by(Ticket.CreatedAt.desc()).limit(10).all()
        
        activities = []
        for ticket, user, category in recent_tickets:
            activities.append({
                'icon': 'fas fa-ticket-alt',
                'title': f'New ticket #{ticket.TicketID}',
                'description': f'{category.Name} - {user.Name if user else "Anonymous"}',
                'created_at': ticket.CreatedAt.isoformat()
            })
        
        return jsonify(activities)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/tickets', methods=['GET'])
@admin_required
def get_admin_tickets():
    try:
        logger.info("Loading admin tickets...")
        
        # Ensure tables exist first
        try:
            db.create_all()
            logger.info("Database tables created/verified")
        except Exception as table_error:
            logger.error(f"Error creating tables: {str(table_error)}")
        
        # Test database connection
        try:
            db.session.execute(text('SELECT 1'))
            logger.info("Database connection successful for tickets")
        except Exception as db_error:
            logger.error(f"Database connection failed in tickets: {str(db_error)}")
            return jsonify({
                "error": "Database connection failed",
                "details": str(db_error)
            }), 500
        
        # Try simple query first to check if Ticket table exists
        try:
            ticket_count = db.session.query(Ticket).count()
            logger.info(f"Found {ticket_count} tickets in database")
            
            if ticket_count == 0:
                logger.info("No tickets found, returning empty array")
                return jsonify([])
            
        except Exception as count_error:
            logger.error(f"Error counting tickets: {str(count_error)}")
            # Table might not exist, try to create sample data
            return jsonify([])
        
        # Try to get tickets with detailed logging and priority sorting
        try:
            tickets = db.session.query(Ticket, User, Category).join(
                User, Ticket.UserID == User.UserID, isouter=True
            ).join(
                Category, Ticket.CategoryID == Category.CategoryID, isouter=True
            ).order_by(
                # Sort by priority first (critical -> high -> medium -> low), then by created date
                case(
                    (Ticket.Priority == 'critical', 4),
                    (Ticket.Priority == 'high', 3),
                    (Ticket.Priority == 'medium', 2),
                    (Ticket.Priority == 'low', 1),
                    else_=2
                ).desc(),
                Ticket.CreatedAt.desc()
            ).all()
            
            logger.info(f"Found {len(tickets)} tickets in database")
            
            result = []
            for ticket, user, category in tickets:
                ticket_data = {
                    'id': ticket.TicketID,
                    'subject': ticket.Subject,
                    'category': category.Name if category else 'Unknown',
                    'user_name': user.Name if user else ticket.CreatedBy or 'Anonymous',
                    'user_email': user.Email if user else 'No email',
                    'organization': user.OrganizationName if user else ticket.OrganizationName or 'Unknown Organization',
                    'priority': ticket.Priority or 'medium',
                    'status': ticket.Status,
                    'created_at': ticket.CreatedAt.isoformat(),
                    'updated_at': ticket.UpdatedAt.isoformat() if ticket.UpdatedAt else ticket.CreatedAt.isoformat()
                }
                result.append(ticket_data)
                logger.info(f"Processed ticket {ticket.TicketID}: {ticket.Subject} - Priority: {ticket.Priority}, Org: {ticket_data['organization']}")
            
            logger.info(f"Returning {len(result)} tickets to admin panel sorted by priority")
            return jsonify(result)
            
        except Exception as query_error:
            logger.error(f"Error querying tickets with joins: {str(query_error)}", exc_info=True)
            
            # Try a simpler query as fallback
            try:
                simple_tickets = Ticket.query.all()
                logger.info(f"Fallback: Found {len(simple_tickets)} tickets with simple query")
                
                result = []
                for ticket in simple_tickets:
                    result.append({
                        'id': ticket.TicketID,
                        'subject': ticket.Subject,
                        'category': 'Unknown',
                        'user_name': ticket.CreatedBy or 'Unknown',
                        'user_email': 'Unknown',
                        'organization': ticket.OrganizationName or 'Unknown Organization',
                        'priority': ticket.Priority or 'medium',
                        'status': ticket.Status,
                        'created_at': ticket.CreatedAt.isoformat(),
                        'updated_at': ticket.UpdatedAt.isoformat() if ticket.UpdatedAt else ticket.CreatedAt.isoformat()
                    })
                
                return jsonify(result)
                
            except Exception as simple_error:
                logger.error(f"Even simple query failed: {str(simple_error)}")
                return jsonify([])  # Return empty array instead of error
        
    except Exception as e:
        logger.error(f"Unexpected error in get_admin_tickets: {str(e)}", exc_info=True)
        return jsonify([])  # Return empty array instead of error

@app.route('/api/admin/tickets/<int:ticket_id>', methods=['GET'])
@admin_required
def get_admin_ticket_details(ticket_id):
    try:
        logger.info(f"Loading admin ticket details for ticket ID: {ticket_id}")
        
        ticket = db.session.query(Ticket, User, Category).join(
            User, Ticket.UserID == User.UserID, isouter=True
        ).join(
            Category, Ticket.CategoryID == Category.CategoryID
        ).filter(Ticket.TicketID == ticket_id).first()
        
        if not ticket:
            logger.error(f"Ticket {ticket_id} not found")
            return jsonify({"error": "Ticket not found"}), 404
        
        ticket_obj, user, category = ticket
        logger.info(f"Found ticket {ticket_id}: {ticket_obj.Subject}")
        
        # Get messages with attachments
        messages = Message.query.filter_by(TicketID=ticket_id).order_by(Message.CreatedAt).all()
        logger.info(f"Found {len(messages)} messages for ticket {ticket_id}")
        
        # Build message list with attachment information
        message_list = []
        for msg in messages:
            # Get attachments for this message
            attachments = Attachment.query.filter_by(MessageID=msg.MessageID).all()
            logger.info(f"Message {msg.MessageID} has {len(attachments)} attachments")
            
            message_data = {
                'content': msg.Content,
                'is_admin': msg.IsAdminReply,
                'created_at': msg.CreatedAt.isoformat(),
                'attachments': [{
                    'id': att.AttachmentID,
                    'original_name': att.OriginalName,
                    'url': f'/static/uploads/{att.StoredName}',
                    'file_path': f'/static/uploads/{att.StoredName}',
                    'filename': att.StoredName,
                    'file_size': att.FileSize,
                    'mime_type': att.MimeType
                } for att in attachments]
            }
            
            # Add attachment_url for backward compatibility
            if attachments:
                message_data['attachment_url'] = f'/static/uploads/{attachments[0].StoredName}'
                logger.info(f"Added attachment URL: {message_data['attachment_url']}")
            
            message_list.append(message_data)
        
        result = {
            'id': ticket_obj.TicketID,
            'subject': ticket_obj.Subject,
            'category': category.Name,
            'user_name': user.Name if user else None,
            'user_email': user.Email if user else None,
            'status': ticket_obj.Status,
            'created_at': ticket_obj.CreatedAt.isoformat(),
            'messages': message_list
        }
        
        logger.info(f"Returning ticket details for {ticket_id} with {len(message_list)} messages")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error getting admin ticket details for {ticket_id}: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/active-conversations', methods=['GET'])
@admin_required
def get_active_conversations():
    try:
        # Get tickets with recent activity
        conversations = db.session.query(Ticket, User, Category).join(
            User, Ticket.UserID == User.UserID, isouter=True
        ).join(
            Category, Ticket.CategoryID == Category.CategoryID
        ).filter(Ticket.Status.in_(['open', 'in_progress'])).order_by(Ticket.UpdatedAt.desc()).all()
        
        result = []
        for ticket, user, category in conversations:
            # Get last message time
            last_message = Message.query.filter_by(TicketID=ticket.TicketID).order_by(Message.CreatedAt.desc()).first()
            
            # Count unread admin messages (assuming we track this)
            unread_count = Message.query.filter_by(TicketID=ticket.TicketID, IsAdminReply=False).count()
            
            result.append({
                'id': ticket.TicketID,
                'subject': ticket.Subject,
                'user_name': user.Name if user else None,
                'category': category.Name,
                'status': ticket.Status,
                'last_message_at': last_message.CreatedAt.isoformat() if last_message else ticket.CreatedAt.isoformat(),
                'unread_count': min(unread_count, 5)  # Cap at 5 for display
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/tickets/<int:ticket_id>/status', methods=['PUT'])
@admin_required
def update_ticket_status(ticket_id):
    try:
        data = request.json
        new_status = data.get('status')
        admin_message = data.get('message', '')  # Optional message from admin
        
        if new_status not in ['open', 'in_progress', 'resolved', 'closed']:
            return jsonify({"error": "Invalid status"}), 400
        
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            return jsonify({"error": "Ticket not found"}), 404
        
        # Update ticket status
        old_status = ticket.Status
        ticket.Status = new_status
        ticket.UpdatedAt = datetime.utcnow()
        
        # If ticket is being resolved or closed, send notification to user
        if new_status in ['resolved', 'closed'] and old_status not in ['resolved', 'closed']:
            # Create a system message to notify the user
            notification_content = admin_message if admin_message else (
                "Your issue has been resolved. Thank you for contacting support! "
                "If you need further assistance, please feel free to create a new ticket."
            )
            
            # Add the notification as an admin message
            notification_message = Message(
                TicketID=ticket_id,
                SenderID=None,  # System message
                Content=notification_content,
                IsAdminReply=True,
                CreatedAt=datetime.utcnow()
            )
            db.session.add(notification_message)
            
            # Also add a system closure message
            if new_status == 'closed':
                closure_message = Message(
                    TicketID=ticket_id,
                    SenderID=None,  # System message
                    Content="This chat session has been closed. Rating and feedback are appreciated.",
                    IsAdminReply=True,
                    CreatedAt=datetime.utcnow()
                )
                db.session.add(closure_message)
        
        db.session.commit()
        
        response_data = {
            "status": "success", 
            "message": "Ticket status updated",
            "new_status": new_status,
            "notification_sent": new_status in ['resolved', 'closed'] and old_status not in ['resolved', 'closed']
        }
        
        return jsonify(response_data)
    except Exception as e:
        logger.error(f"Error updating ticket status: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/analytics', methods=['GET'])
@admin_required
def get_analytics():
    try:
        # Category distribution
        category_stats = db.session.query(Category.Name, db.func.count(Ticket.TicketID)).join(
            Ticket, Category.CategoryID == Ticket.CategoryID
        ).group_by(Category.Name).all()
        
        category_data = {
            'labels': [stat[0] for stat in category_stats],
            'values': [stat[1] for stat in category_stats]
        }
        
        # Resolution time (mock data for now)
        resolution_data = {
            'labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            'values': [2.5, 3.2, 2.8, 4.1, 3.5, 2.1, 1.8]
        }
        
        return jsonify({
            'categoryData': category_data,
            'resolutionData': resolution_data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """Submit user feedback for a ticket"""
    try:
        data = request.json
        ticket_id = data.get('ticket_id')
        rating = data.get('rating', 0)
        feedback_text = data.get('feedback', '')
        
        if not ticket_id:
            return jsonify({"error": "Ticket ID is required"}), 400
        
        # Verify ticket exists
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            return jsonify({"error": "Ticket not found"}), 404
        
        # Create feedback message
        feedback_message = Message(
            TicketID=ticket_id,
            SenderID=None,  # System message
            Content=f"User Feedback - Rating: {rating}/5 stars" + 
                   (f"\nFeedback: {feedback_text}" if feedback_text else ""),
            IsAdminReply=False,
            CreatedAt=datetime.utcnow()
        )
        
        db.session.add(feedback_message)
        db.session.commit()
        
        logger.info(f"Feedback submitted for ticket {ticket_id}: Rating={rating}")
        
        return jsonify({
            "status": "success",
            "message": "Thank you for your feedback!"
        })
        
    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Enhanced health check endpoint"""
    try:
        health_status, health_message = check_database_health()
        
        if health_status:
            return jsonify({
                "status": "healthy",
                "database": "connected",
                "message": health_message,
                "timestamp": datetime.utcnow().isoformat()
            }), 200
        else:
            return jsonify({
                "status": "unhealthy",
                "database": "disconnected",
                "error": health_message,
                "timestamp": datetime.utcnow().isoformat()
            }), 503
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@app.route('/api/database/test', methods=['GET'])
def test_database():
    """Test database operations"""
    try:
        # Test basic connection
        health_status, health_message = check_database_health()
        if not health_status:
            return jsonify({"error": health_message}), 500
        
        # Test table access
        category_count = Category.query.count()
        ticket_count = Ticket.query.count()
        user_count = User.query.count()
        
        return jsonify({
            "status": "success",
            "database": "connected",
            "tables": {
                "categories": category_count,
                "tickets": ticket_count,
                "users": user_count
            },
            "message": "All database operations successful"
        })
        
    except Exception as e:
        logger.error(f"Database test failed: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@app.route('/api/tickets/<int:ticket_id>', methods=['GET'])
def get_ticket_details(ticket_id):
    """Get ticket details including status and messages for user interface"""
    try:
        # Get ticket with user and category info
        ticket_query = db.session.query(Ticket, User, Category).join(
            User, Ticket.UserID == User.UserID, isouter=True
        ).join(
            Category, Ticket.CategoryID == Category.CategoryID
        ).filter(Ticket.TicketID == ticket_id).first()
        
        if not ticket_query:
            return jsonify({"error": "Ticket not found"}), 404
        
        ticket, user, category = ticket_query
          # Get messages for this ticket
        messages = Message.query.filter_by(TicketID=ticket_id).order_by(Message.CreatedAt).all()
        
        # Build message list with attachments
        message_list = []
        for msg in messages:
            attachments = Attachment.query.filter_by(MessageID=msg.MessageID).all()
            message_data = {
                'content': msg.Content,
                'is_admin': msg.IsAdminReply,
                'created_at': msg.CreatedAt.isoformat(),
                'attachments': [{
                    'id': att.AttachmentID,
                    'original_name': att.OriginalName,
                    'url': f'/static/uploads/{att.StoredName}',
                    'file_size': att.FileSize,
                    'mime_type': att.MimeType
                } for att in attachments]
            }
            message_list.append(message_data)
        
        result = {
            'id': ticket.TicketID,
            'subject': ticket.Subject,
            'status': ticket.Status,
            'category': category.Name if category else 'Unknown',
            'user_name': user.Name if user else 'Anonymous',
            'user_email': user.Email if user else 'No email',
            'created_at': ticket.CreatedAt.isoformat(),
            'updated_at': ticket.UpdatedAt.isoformat(),
            'messages': message_list
        }
        
        logger.info(f"Returning ticket details for {ticket_id}: Status={ticket.Status}")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error getting ticket details: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

# User profile routes
@app.route('/profile')
def user_profile():
    """User profile page"""
    return render_template('profile.html')

@app.route('/api/user/stats', methods=['GET'])
@login_required
def get_user_stats():
    """Get user ticket statistics"""
    try:
        user_id = current_user.UserID
        
        # Get ticket counts
        total_tickets = Ticket.query.filter_by(UserID=user_id).count()
        open_tickets = Ticket.query.filter_by(UserID=user_id, Status='open').count()
        in_progress_tickets = Ticket.query.filter_by(UserID=user_id, Status='in_progress').count()
        resolved_tickets = Ticket.query.filter_by(UserID=user_id, Status='resolved').count()
        closed_tickets = Ticket.query.filter_by(UserID=user_id, Status='closed').count()
        
        # Calculate average resolution time (simplified)
        resolved_ticket_objects = Ticket.query.filter_by(UserID=user_id, Status='resolved').all()
        avg_resolution = None
        if resolved_ticket_objects:
            total_hours = sum([
                (ticket.UpdatedAt - ticket.CreatedAt).total_seconds() / 3600 
                for ticket in resolved_ticket_objects if ticket.UpdatedAt
            ])
            avg_resolution = f"{int(total_hours / len(resolved_ticket_objects))}h"
        
        return jsonify({
            'total': total_tickets,
            'open': open_tickets + in_progress_tickets,  # Combine open and in_progress
            'resolved': resolved_tickets + closed_tickets,  # Combine resolved and closed
            'avgResolution': avg_resolution
        })
        
    except Exception as e:
        logger.error(f"Error getting user stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/tickets', methods=['GET'])
@login_required
def get_user_tickets():
    """Get user's tickets"""
    try:
        user_id = current_user.UserID
        limit = request.args.get('limit', 20, type=int)
        
        tickets = db.session.query(Ticket, Category).join(
            Category, Ticket.CategoryID == Category.CategoryID
        ).filter(Ticket.UserID == user_id).order_by(Ticket.CreatedAt.desc()).limit(limit).all()
        
        result = []
        for ticket, category in tickets:
            ticket_data = {
                'id': ticket.TicketID,
                'subject': ticket.Subject,
                'category': category.Name,
                'priority': ticket.Priority,
                'status': ticket.Status,
                'created_at': ticket.CreatedAt.isoformat(),
                'updated_at': ticket.UpdatedAt.isoformat()
            }
            result.append(ticket_data)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error getting user tickets: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/profile', methods=['PUT'])
@login_required
def update_user_profile():
    """Update user profile"""
    try:
        data = request.json
        user = current_user
        
        # Update user fields
        if 'name' in data:
            user.Name = data['name']
        if 'position' in data:
            user.Position = data['position']
        if 'department' in data:
            user.Department = data['department']
        if 'phone' in data:
            user.Phone = data['phone']
        if 'priority' in data and data['priority'] in ['low', 'medium', 'high', 'critical']:
            user.PriorityLevel = data['priority']
        if 'language' in data:
            user.PreferredLanguage = data['language']
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Profile updated successfully'
        })
        
    except Exception as e:
        logger.error(f"Error updating user profile: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    import socket
    
    try:
        # Test database connection
        with app.app_context():
            db.create_all()
            print("Database connection successful!")
    except Exception as e:
        print("Error connecting to database:", str(e))
        print("Please check your database connection settings in .env file")
    
    # Try to find an available port
    def find_free_port():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            s.listen(1)
            port = s.getsockname()[1]
        return port
    
    # Use port 5001 or find an alternative
    try:
        port = 5001
        print(f"Starting application on port {port}...")
        print(f"Access the application at: http://127.0.0.1:{port}")
        print(f"Admin panel: http://127.0.0.1:{port}/admin")
        print(f"Admin login: admin@supportcenter.com / admin123")
        print("Press Ctrl+C to stop the server")
        
        # Run with SocketIO for real-time support
        socketio.run(app, debug=app.config['DEBUG'], port=port, host='127.0.0.1')
    except OSError as e:
        if "address already in use" in str(e).lower() or "10048" in str(e):
            print(f"Port {port} is already in use. Finding alternative port...")
            port = find_free_port()
            print(f"Using port {port} instead...")
            print(f"Access the application at: http://127.0.0.1:{port}")
            socketio.run(app, debug=app.config['DEBUG'], port=port, host='127.0.0.1')
        else:
            raise
