# Chatbot Cloud Support System

This project is a full-featured enterprise-grade support ticketing and escalation system built with Flask, SQLAlchemy, and Odoo integration. It provides advanced admin, partner, and bot management capabilities for modern customer support workflows.

## Features

- **User Support Portal**: Users can create, track, and manage support tickets.
- **Super Admin Dashboard**: Role-based access for super admins to manage partners, tickets, escalations, and audit logs.
- **Partner Management**: Add, update, and monitor support partners (ICP/YCP) with SLA compliance tracking.
- **Escalation Workflow**: Automated and manual ticket escalation with SLA monitoring and partner assignment.
- **Audit & Workflow Logs**: Complete audit trail and timeline view for all ticket actions and escalations.
- **Bot Integration**: Configurable bot for automated responses, fallback to human, and performance analytics.
- **Odoo Integration**: Sync tickets and customers with Odoo ERP for enterprise workflows.
- **File Uploads**: Attachments for tickets and messages.
- **Internationalization**: Multi-language support via Flask-Babel and translation files.
- **Security**: Role-based authentication, session management, and security alerts.

## Technology Stack

- Python 3.9+
- Flask
- Flask-SocketIO
- Flask-Login
- Flask-Babel
- Flask-SQLAlchemy
- MSSQL (SQL Server)
- Odoo XML-RPC
- Eventlet

## Project Structure

```
mgmg/
├── app.py                  # Main Flask application
├── config.py               # Configuration (DB, Odoo, etc.)
├── models.py               # SQLAlchemy models
├── auth.py                 # Authentication blueprint
├── super_admin.py          # Super admin dashboard & APIs
├── device_tracker_core.py  # Device tracking utilities
├── location_service.py     # Location detection service
├── odoo_service.py         # Odoo integration service
├── bot_service.py          # Bot integration and API
├── sla_monitor.py          # SLA monitoring service
├── requirements.txt        # Python dependencies
├── templates/              # HTML templates
├── static/                 # Static files (CSS, JS, uploads)
├── translations/           # Babel translation files
└── ...                     # Other supporting files
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone https://github.com/pranav0121/chatbot_cloud.git
   cd chatbot_cloud
   ```
2. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```
3. **Configure environment:**
   - Edit `.env` for database and Odoo credentials.
   - Ensure MSSQL and Odoo are accessible.
4. **Run the application:**
   ```
   python app.py
   ```
   - The app runs on port 5000 by default.

## Usage

- Access the user portal at `http://localhost:5000/`
- Super admin dashboard: `/super-admin/`
- API endpoints for partners, tickets, escalation, audit, bot, and Odoo are available under `/api/`

## Customization

- Update `config.py` for DB and Odoo settings.
- Add new templates in `templates/`.
- Extend models in `models.py` for new features.

## License

MIT

## Author

[pranav0121](https://github.com/pranav0121)

---

For detailed API documentation, see the code comments and endpoint docstrings in each module.
