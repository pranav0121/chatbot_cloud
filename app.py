from flask import Flask, render_template, request, jsonify, send_from_directory
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

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
config_obj = Config()
app.config.from_object(config_obj)

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

db = SQLAlchemy(app)

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
class User(db.Model):
    __tablename__ = 'Users'
    UserID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100))
    Email = db.Column(db.String(255))
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)

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
    Status = db.Column(db.String(20), default='open')
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)
    UpdatedAt = db.Column(db.DateTime, default=datetime.utcnow)

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

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/faq')
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
            'mime_type': file.mimetype or f'image/{file_ext}'
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
        
        # Create or get user
        user = None
        if data.get('name') or data.get('email'):
            try:
                user = User(Name=data.get('name'), Email=data.get('email'))
                db.session.add(user)
                db.session.flush()  # Get the ID without committing
                logger.info(f"Created user with ID: {user.UserID}")
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
        
        # Create ticket
        try:
            ticket = Ticket(
                UserID=user.UserID if user else None,
                CategoryID=category_id,
                Subject=data.get('subject', 'Support Request'),
                Status='open'
            )
            db.session.add(ticket)
            db.session.flush()  # Get the ID without committing
            logger.info(f"Created ticket with ID: {ticket.TicketID}")
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
        
        logger.info(f"Successfully created ticket {ticket.TicketID}")
        return jsonify({
            'ticket_id': ticket.TicketID,
            'user_id': user.UserID if user else None,
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
    return render_template('admin.html')

@app.route('/api/admin/dashboard-stats', methods=['GET'])
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
def get_admin_tickets():
    try:
        logger.info("Loading admin tickets...")
        
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
        
        # Try to get tickets with detailed logging
        try:
            tickets = db.session.query(Ticket, User, Category).join(
                User, Ticket.UserID == User.UserID, isouter=True
            ).join(
                Category, Ticket.CategoryID == Category.CategoryID
            ).order_by(Ticket.CreatedAt.desc()).all()
            
            logger.info(f"Found {len(tickets)} tickets in database")
            
            result = []
            for ticket, user, category in tickets:
                ticket_data = {
                    'id': ticket.TicketID,
                    'subject': ticket.Subject,
                    'category': category.Name if category else 'Unknown',
                    'user_name': user.Name if user else 'Anonymous',
                    'user_email': user.Email if user else 'No email',
                    'status': ticket.Status,
                    'created_at': ticket.CreatedAt.isoformat()
                }
                result.append(ticket_data)
                logger.info(f"Processed ticket {ticket.TicketID}: {ticket.Subject}")
            
            logger.info(f"Returning {len(result)} tickets to admin panel")
            return jsonify(result)
            
        except Exception as query_error:
            logger.error(f"Error querying tickets: {str(query_error)}", exc_info=True)
            
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
                        'user_name': 'Unknown',
                        'user_email': 'Unknown',
                        'status': ticket.Status,
                        'created_at': ticket.CreatedAt.isoformat()
                    })
                
                return jsonify(result)
                
            except Exception as simple_error:
                logger.error(f"Even simple query failed: {str(simple_error)}")
                return jsonify({
                    "error": "Failed to query tickets",
                    "details": str(simple_error)
                }), 500
        
    except Exception as e:
        logger.error(f"Unexpected error in get_admin_tickets: {str(e)}", exc_info=True)
        return jsonify({
            "error": str(e),
            "message": "Failed to load tickets"
        }), 500

@app.route('/api/admin/tickets/<int:ticket_id>', methods=['GET'])
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

if __name__ == '__main__':
    try:
        # Test database connection
        with app.app_context():
            db.create_all()
            # Try to fetch categories to test the connection
            categories = Category.query.all()
            print("Database connection successful!")
            print(f"Found {len(categories)} categories")
    except Exception as e:
        print("Error connecting to database:", str(e))
        print("Please check your database connection settings in .env file")
    
    app.run(debug=True, port=5000)
