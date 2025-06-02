from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pyodbc
import logging
from config import Config

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

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

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/categories', methods=['GET'])
def get_categories():
    try:
        # First, ensure the database has categories
        count = Category.query.count()
        if count == 0:
            # Insert default categories if none exist
            default_categories = [
                Category(Name='Payments', Team='Billing'),
                Category(Name='Product Issues', Team='Product'),
                Category(Name='Technical Glitches', Team='Tech'),
                Category(Name='General Inquiries', Team='General')
            ]
            db.session.bulk_save_objects(default_categories)
            db.session.commit()
            print("Inserted default categories")
        
        categories = Category.query.all()
        print(f"Found {len(categories)} categories")
        result = [{'id': c.CategoryID, 'name': c.Name} for c in categories]
        print("Categories:", result)
        return jsonify(result)
    except Exception as e:
        print("Error fetching categories:", str(e))
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

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
    data = request.json
    
    # Create or get user
    user = None
    if data.get('name') or data.get('email'):
        user = User(Name=data.get('name'), Email=data.get('email'))
        db.session.add(user)
        db.session.commit()
    
    # Create ticket
    ticket = Ticket(
        UserID=user.UserID if user else None,
        CategoryID=data['category_id'],
        Subject=data['subject']
    )
    db.session.add(ticket)
    
    # Create initial message
    message = Message(
        TicketID=ticket.TicketID,
        SenderID=user.UserID if user else None,
        Content=data['message']
    )
    db.session.add(message)
    db.session.commit()
    
    return jsonify({
        'ticket_id': ticket.TicketID,
        'status': 'success',
        'message': 'Ticket created successfully'
    })

@app.route('/api/tickets/<int:ticket_id>/messages', methods=['GET', 'POST'])
def handle_messages(ticket_id):
    if request.method == 'GET':
        messages = Message.query.filter_by(TicketID=ticket_id).order_by(Message.CreatedAt).all()
        return jsonify([{
            'id': m.MessageID,
            'content': m.Content,
            'is_admin': m.IsAdminReply,
            'created_at': m.CreatedAt.isoformat()
        } for m in messages])
    
    # POST new message
    data = request.json
    message = Message(
        TicketID=ticket_id,
        SenderID=data.get('user_id'),
        Content=data['content'],
        IsAdminReply=data.get('is_admin', False)
    )
    db.session.add(message)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message_id': message.MessageID
    })

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
