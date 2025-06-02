# Customer Support System 🎯

A comprehensive customer support solution with modern UI and powerful admin dashboard, built with Flask and featuring real-time chat functionality.

![System Overview](https://img.shields.io/badge/Status-Ready%20for%20Production-green)
![Python](https://img.shields.io/badge/Python-3.7+-blue)
![Flask](https://img.shields.io/badge/Flask-2.0+-blue)
![Database](https://img.shields.io/badge/Database-SQL%20Server-orange)

## ✨ Features

### 🎨 **Modern User Interface**
- Beautiful hero section with gradient backgrounds
- Interactive chat widget with multiple states
- Category-based support system
- Common issues quick selection
- Custom form for specific problems
- Real-time live chat with admin support
- Solution modal with feedback system
- Star rating system
- Mobile-responsive design

### ⚡ **Powerful Admin Dashboard**
- Real-time statistics and metrics
- Comprehensive ticket management
- Live chat interface for customer support
- Analytics with visual charts
- Ticket filtering and status updates
- User feedback monitoring
- Professional sidebar navigation

### 🔧 **Technical Features**
- RESTful API architecture
- SQLAlchemy ORM with SQL Server
- Auto-populated sample data
- Error handling and logging
- Responsive Bootstrap 5 design
- Chart.js integration for analytics
- Font Awesome icons throughout

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- SQL Server (LocalDB, Express, or Full)
- Modern web browser

### Installation

1. **Clone or Download the Project**
   ```bash
   # Navigate to the project directory
   cd chatbot_cloud
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Database**
   - Update `.env` file with your SQL Server details
   - Default configuration uses SQL Server Express

4. **Start the Application**
   
   **Option A: Use the startup script**
   ```bash
   # Windows Batch
   start.bat
   
   # Or PowerShell
   .\start.ps1
   ```
   
   **Option B: Run directly**
   ```bash
   python app.py
   ```

5. **Access the Application**
   - **User Interface**: http://localhost:5000
   - **Admin Dashboard**: http://localhost:5000/admin

## 📁 Project Structure

```
chatbot_cloud/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables
├── start.bat            # Windows startup script
├── start.ps1            # PowerShell startup script
├── test_app.py          # Application test script
├── TESTING_GUIDE.md     # Comprehensive testing guide
├── templates/
│   ├── index.html       # User interface template
│   └── admin.html       # Admin dashboard template
├── static/
│   ├── css/
│   │   ├── style.css    # User interface styles
│   │   └── admin.css    # Admin dashboard styles
│   └── js/
│       ├── chat.js      # User chat functionality
│       └── admin.js     # Admin dashboard scripts
└── database/
    ├── chatbot.sql      # Database schema
    ├── setup_user.sql   # User setup script
    └── verify_db.sql    # Database verification
```

## 🎯 User Journey

### **Customer Experience**
1. **Landing Page**: Modern hero section introduces the support system
2. **Category Selection**: Choose from Payments, Product Issues, Technical Glitches, or General Inquiries
3. **Quick Solutions**: Browse common issues for instant solutions
4. **Custom Support**: Submit detailed forms for specific problems
5. **Live Chat**: Real-time communication with support agents
6. **Feedback**: Rate solutions and provide comments

### **Admin Experience**
1. **Dashboard**: Overview of all support metrics and activity
2. **Ticket Management**: View, filter, and manage all support tickets
3. **Live Chat**: Engage in real-time conversations with customers
4. **Analytics**: Visual insights into support patterns and performance
5. **Status Updates**: Manage ticket lifecycle from open to resolved

## 🔗 API Endpoints

### **User Endpoints**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | User interface homepage |
| GET | `/api/categories` | Get support categories |
| GET | `/api/common-queries/<id>` | Get common questions for category |
| POST | `/api/tickets` | Create new support ticket |
| GET/POST | `/api/tickets/<id>/messages` | Handle chat messages |
| POST | `/api/feedback` | Submit user feedback |

### **Admin Endpoints**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin` | Admin dashboard |
| GET | `/api/admin/dashboard-stats` | Dashboard statistics |
| GET | `/api/admin/tickets` | All tickets with details |
| GET | `/api/admin/tickets/<id>` | Specific ticket details |
| GET | `/api/admin/active-conversations` | Active chat sessions |
| PUT | `/api/admin/tickets/<id>/status` | Update ticket status |
| GET | `/api/admin/analytics` | Analytics data for charts |

## 🗄️ Database Schema

### **Core Tables**
- **Users**: Customer information and contact details
- **Categories**: Support category organization
- **Tickets**: Support request tracking
- **Messages**: Chat conversation history
- **CommonQueries**: Pre-defined solutions for frequent issues
- **Feedback**: User ratings and comments

### **Auto-Generated Data**
The system automatically creates:
- 4 default support categories
- 3-4 common questions per category
- Sample solutions for quick resolution

## 🎨 UI Components

### **User Interface**
- **Hero Section**: Gradient background with floating cards animation
- **Category Cards**: Interactive selection with hover effects
- **Chat Widget**: Multi-state flow with smooth transitions
- **Solution Modal**: Bootstrap modal with integrated feedback
- **Rating System**: Interactive star rating component

### **Admin Dashboard**
- **Statistics Cards**: Real-time metrics with color coding
- **Data Tables**: Sortable and filterable ticket management
- **Charts**: Category distribution and resolution time analytics
- **Live Chat**: Real-time conversation interface

## 🔧 Configuration

### **Environment Variables (.env)**
```env
DB_SERVER=.\SQLEXPRESS
DB_DATABASE=SupportChatbot
DB_USERNAME=chatbot_user
DB_PASSWORD=YourSecurePassword
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here
```

### **Application Settings**
- **Port**: Default 5000 (configurable in app.py)
- **Debug Mode**: Enabled for development
- **Database**: SQL Server with auto-table creation
- **Session**: Filesystem-based session storage

## 🧪 Testing

Run the comprehensive test script:
```bash
python test_app.py
```

For detailed testing scenarios, see [TESTING_GUIDE.md](TESTING_GUIDE.md)

## 🔮 Future Enhancements

### **Planned Features**
- [ ] WebSocket integration for real-time updates
- [ ] Email notifications for new tickets
- [ ] File upload support for attachments
- [ ] User authentication system
- [ ] Advanced analytics and reporting
- [ ] Multi-language support
- [ ] AI-powered response suggestions
- [ ] Mobile app companion

### **Technical Improvements**
- [ ] Redis caching for better performance
- [ ] Docker containerization
- [ ] Cloud deployment guides
- [ ] API rate limiting
- [ ] Automated testing suite

## 🛡️ Security Features

- Environment variable configuration
- SQL injection prevention via SQLAlchemy ORM
- Input validation and sanitization
- Secure session management
- Error logging without sensitive data exposure

## 📊 Performance

### **Optimizations**
- Efficient database queries with proper indexing
- Minimal JavaScript for fast loading
- Responsive design for all devices
- Compressed CSS and optimized images
- Auto-refresh intervals for live data

### **Scalability**
- RESTful API design for horizontal scaling
- Database connection pooling
- Stateless session management
- Modular component architecture

## 🐛 Troubleshooting

### **Common Issues**

1. **Database Connection Errors**
   - Verify SQL Server is running
   - Check connection string in .env
   - Ensure database user has proper permissions

2. **Port Already in Use**
   - Change port in app.py: `app.run(port=5001)`
   - Or stop conflicting services

3. **Import Errors**
   - Run: `pip install -r requirements.txt`
   - Check Python version compatibility

### **Debugging**
- Enable debug mode: Set `FLASK_DEBUG=True` in .env
- Check browser console for JavaScript errors
- Review Flask logs for server-side issues

## 📞 Support

For questions or issues:
1. Check the [TESTING_GUIDE.md](TESTING_GUIDE.md)
2. Review error logs in the console
3. Verify all dependencies are installed
4. Ensure database connectivity

## 📝 License

This project is designed for educational and commercial use. Feel free to modify and adapt for your specific needs.

---

**Built with ❤️ using Flask, Bootstrap, and modern web technologies**

Ready to provide exceptional customer support! 🚀
