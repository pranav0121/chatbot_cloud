# YouCloudPay Customer Support Chatbot

A comprehensive, multilingual customer support chatbot system built with Flask, featuring real-time chat, file attachments, FAQ management, admin dashboard, and WhatsApp-style UI.

## 🚀 Features

### Core Features
- **Real-time Chat Interface** - WhatsApp-style messaging with typing indicators
- **Multilingual Support** - 12+ languages with Google Translate integration
- **File Attachments** - Support for images, documents, and files
- **FAQ System** - Searchable knowledge base with categories
- **Smart Chatbot** - AI-powered responses with complaint flow
- **Admin Dashboard** - Complete management interface
- **User Authentication** - Role-based access control
- **Responsive Design** - Mobile-friendly TailwindCSS UI

### Advanced Features
- **Complaint Management** - Track and resolve customer issues
- **Analytics Dashboard** - Real-time statistics and insights
- **Message Translation** - Auto-translate conversations
- **File Management** - Secure upload and download system
- **Search & Filtering** - Advanced search capabilities
- **Email Notifications** - Automated email alerts
- **Export Functionality** - Data export capabilities

## 🛠️ Technology Stack

### Backend
- **Flask** - Python web framework
- **SQLAlchemy** - Database ORM
- **Flask-Login** - User authentication
- **Flask-WTF** - Form handling and CSRF protection
- **Flask-Babel** - Internationalization
- **Flask-Migrate** - Database migrations

### Frontend
- **TailwindCSS** - Utility-first CSS framework
- **Alpine.js** - Lightweight JavaScript framework
- **Chart.js** - Data visualization
- **DataTables** - Advanced table functionality
- **Font Awesome** - Icon library

### Database
- **SQLite** (Development)
- **PostgreSQL** (Production)
- **Redis** (Caching)

### Deployment
- **Docker** - Containerization
- **Nginx** - Reverse proxy and load balancer
- **Gunicorn** - WSGI HTTP Server

## 📁 Project Structure

```
chatbot_cloud/
├── app/
│   ├── __init__.py           # Flask app factory
│   ├── models/               # Database models
│   │   ├── user.py          # User model
│   │   ├── complaint.py     # Complaint model
│   │   ├── message.py       # Message model
│   │   ├── attachment.py    # Attachment model
│   │   └── faq.py           # FAQ model
│   ├── routes/               # Route blueprints
│   │   ├── auth.py          # Authentication routes
│   │   ├── main.py          # Main application routes
│   │   ├── chat.py          # Chat functionality
│   │   ├── admin.py         # Admin panel
│   │   └── api.py           # API endpoints
│   ├── services/             # Business logic
│   │   ├── translation_service.py
│   │   ├── file_service.py
│   │   └── chatbot_service.py
│   ├── forms/                # WTF Forms
│   │   ├── auth.py
│   │   ├── complaints.py
│   │   └── faq.py
│   ├── templates/            # Jinja2 templates
│   └── static/               # Static files (CSS, JS, images)
├── uploads/                  # File upload directory
├── logs/                     # Application logs
├── tests/                    # Test files
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose setup
├── nginx.conf               # Nginx configuration
└── deploy.sh                # Deployment script
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js (for development)
- Docker & Docker Compose (for production)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/youcloudpay/chatbot.git
   cd chatbot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.template .env
   # Edit .env with your configuration
   ```

5. **Initialize database**
   ```bash
   python -c "
   from app import create_app, db
   app = create_app()
   with app.app_context():
       db.create_all()
       print('Database initialized!')
   "
   ```

6. **Create admin user**
   ```bash
   python -c "
   from app import create_app, db
   from app.models.user import User
   
   app = create_app()
   with app.app_context():
       admin = User(
           name='Administrator',
           email='admin@youcloudpay.com',
           role='admin',
           language='en'
       )
       admin.set_password('admin123')
       db.session.add(admin)
       db.session.commit()
       print('Admin user created!')
   "
   ```

7. **Run the application**
   ```bash
   python app.py
   ```

8. **Access the application**
   - Open http://localhost:5000
   - Login with admin@youcloudpay.com / admin123

## 🐳 Production Deployment

### Docker Deployment

1. **Clone and configure**
   ```bash
   git clone https://github.com/youcloudpay/chatbot.git
   cd chatbot
   cp .env.production.template .env.production
   # Edit .env.production with your settings
   ```

2. **Deploy with Docker Compose**
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

3. **Access the application**
   - Application: http://your-domain.com
   - Admin Panel: http://your-domain.com/admin

### Manual Production Setup

1. **Set up PostgreSQL database**
2. **Configure Nginx reverse proxy**
3. **Set up SSL certificates**
4. **Configure monitoring and logging**

## 🔧 Configuration

### Environment Variables

```bash
# Application Settings
FLASK_ENV=production
SECRET_KEY=your-secret-key

# Database
DATABASE_URL=postgresql://user:pass@localhost/chatbot_db

# Translation APIs
GOOGLE_TRANSLATE_API_KEY=your-api-key

# Email Settings
MAIL_SERVER=smtp.gmail.com
MAIL_USERNAME=your-email@domain.com

# Admin Account
ADMIN_EMAIL=admin@yourdomain.com
ADMIN_PASSWORD=secure-password
```

### Supported Languages

- English (en)
- Hindi (hi)
- Telugu (te)
- Marathi (mr)
- Kannada (kn)
- Tamil (ta)
- Spanish (es)
- French (fr)
- German (de)
- Italian (it)
- Portuguese (pt)
- Chinese (zh)
- Japanese (ja)
- Korean (ko)
- Arabic (ar)
- Russian (ru)

## 📱 Usage

### For Customers
1. **Register/Login** - Create account or sign in
2. **Start Chat** - Begin conversation with AI chatbot
3. **Ask Questions** - Get instant answers from FAQ
4. **File Support** - Upload images, documents
5. **Submit Complaints** - Create detailed support tickets
6. **Track Status** - Monitor complaint resolution

### For Admins
1. **Dashboard** - View analytics and metrics
2. **User Management** - Manage customer accounts
3. **Complaint Management** - Handle support tickets
4. **FAQ Management** - Update knowledge base
5. **Chat Monitoring** - View all conversations
6. **Analytics** - Generate reports and insights

## 🧪 Testing

### Run Tests
```bash
# Install test dependencies
pip install pytest pytest-flask pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_auth.py
```

### Manual Testing
1. **Authentication Flow** - Register, login, logout
2. **Chat Functionality** - Send messages, upload files
3. **Admin Features** - Manage users, FAQs, complaints
4. **Mobile Responsiveness** - Test on various devices
5. **Translation** - Test multilingual features

## 🔒 Security Features

- **CSRF Protection** - Form security
- **SQL Injection Prevention** - Parameterized queries
- **XSS Protection** - Content sanitization
- **File Upload Security** - Type and size validation
- **Rate Limiting** - API and login protection
- **Session Security** - Secure cookie settings
- **Input Validation** - Server-side validation
- **Role-Based Access** - User permission system

## 📊 API Documentation

### Authentication Endpoints
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `GET /auth/logout` - User logout

### Chat Endpoints
- `GET /chat` - Chat interface
- `POST /chat/send` - Send message
- `POST /chat/upload` - Upload file
- `GET /chat/history` - Message history

### Admin Endpoints
- `GET /admin/dashboard` - Admin dashboard
- `GET /admin/users` - User management
- `GET /admin/complaints` - Complaint management
- `POST /admin/faq` - Create FAQ

### API Endpoints
- `POST /api/translate` - Translate text
- `GET /api/faq/search` - Search FAQs
- `GET /api/stats` - System statistics

## 🚀 Performance Optimization

- **Database Indexing** - Optimized queries
- **Caching** - Redis for session and data caching
- **CDN Integration** - Static file delivery
- **Image Optimization** - Automatic compression
- **Lazy Loading** - Progressive content loading
- **Minification** - CSS/JS compression
- **Gzip Compression** - Response compression

## 🔄 Monitoring & Maintenance

### Logging
- Application logs in `logs/chatbot.log`
- Error tracking and alerts
- Performance monitoring
- User activity tracking

### Backup Strategy
- Daily database backups
- File upload backups
- Configuration backups
- Recovery procedures

### Health Checks
- `/health` endpoint for monitoring
- Database connectivity checks
- External service validation
- Performance metrics

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- **Email**: support@youcloudpay.com
- **Documentation**: https://docs.youcloudpay.com
- **Issues**: https://github.com/youcloudpay/chatbot/issues

## 🎯 Roadmap

- [ ] Voice message support
- [ ] Video call integration
- [ ] Advanced AI responses
- [ ] Mobile app development
- [ ] Third-party integrations
- [ ] Advanced analytics
- [ ] Multi-tenant support

---

**YouCloudPay Chatbot** - Empowering customer support with intelligent automation 🚀
