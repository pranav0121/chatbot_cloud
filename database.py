#!/usr/bin/env python3
"""
Database initialization module to avoid circular imports
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import text

# Initialize SQLAlchemy instance
db = SQLAlchemy()


def init_app(app):
    """Initialize the database with the Flask app"""
    db.init_app(app)
    return db

# Database Models (moved from app.py to avoid circular imports)


class User(UserMixin, db.Model):
    __tablename__ = 'Users'

    # Primary key and core fields that actually exist in the database
    UserID = db.Column(db.Integer, primary_key=True)
    # Made nullable to match actual schema
    username = db.Column(db.String(80), nullable=True)

    # Actual database columns (matching the real schema)
    Name = db.Column(db.String(100), nullable=True)
    Email = db.Column(db.String(255), nullable=True)
    PasswordHash = db.Column(db.String(255), nullable=True, default='')
    OrganizationName = db.Column(db.String(200), nullable=True)
    Position = db.Column(db.String(100), nullable=True)
    PriorityLevel = db.Column(db.String(20), default='medium')
    Phone = db.Column(db.String(20), nullable=True)
    Department = db.Column(db.String(100), nullable=True)
    PreferredLanguage = db.Column(db.String(10), default='en')
    Country = db.Column(db.String(100), nullable=True)
    IsActive = db.Column(db.Boolean, default=True)
    IsAdmin = db.Column(db.Boolean, default=False)
    LastLogin = db.Column(db.DateTime, nullable=True)
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)
    organization_id = db.Column(db.Integer, db.ForeignKey('Organizations.id'))

    # Device tracking fields that exist in the actual database
    device_type = db.Column(db.String(50), nullable=True)
    operating_system = db.Column(db.String(100), nullable=True)
    browser = db.Column(db.String(100), nullable=True)
    browser_version = db.Column(db.String(50), nullable=True)
    os_version = db.Column(db.String(50), nullable=True)
    device_brand = db.Column(db.String(100), nullable=True)
    device_model = db.Column(db.String(100), nullable=True)
    device_fingerprint = db.Column(db.String(255), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    last_device_type = db.Column(db.String(50), nullable=True)

    def get_id(self):
        return str(self.UserID)

    # Properties for backward compatibility with code expecting lowercase fields
    @property
    def email(self):
        """Provide lowercase email property for compatibility"""
        return self.Email

    @property
    def password_hash(self):
        """Provide lowercase password_hash property for compatibility"""
        return self.PasswordHash

    @property
    def is_admin(self):
        """Provide lowercase is_admin property for compatibility"""
        return self.IsAdmin

    @property
    def is_active(self):
        """Provide lowercase is_active property for compatibility"""
        return self.IsActive

    @property
    def created_at(self):
        """Provide lowercase created_at property for compatibility"""
        return self.CreatedAt

    @property
    def last_login(self):
        """Provide lowercase last_login property for compatibility"""
        return self.LastLogin


class Ticket(db.Model):
    __tablename__ = 'Tickets'

    # Primary columns that match the actual database schema
    TicketID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'))
    CategoryID = db.Column(db.Integer, db.ForeignKey('Categories.CategoryID'))
    Subject = db.Column(db.String(255), nullable=False)
    Status = db.Column(db.String(20), default='open')
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)
    UpdatedAt = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    Priority = db.Column(db.String(20), default='medium')
    OrganizationName = db.Column(db.String(200), nullable=True)
    CreatedBy = db.Column(db.String(100), nullable=True)
    AssignedTo = db.Column(db.String(100), nullable=True)

    # SLA and escalation fields
    escalation_level = db.Column(db.Integer, default=0)
    current_sla_target = db.Column(db.DateTime, nullable=True)
    resolution_method = db.Column(db.String(50), nullable=True)
    bot_attempted = db.Column(db.Boolean, default=False)
    partner_id = db.Column(db.Integer, nullable=True)

    # Odoo integration fields
    odoo_customer_id = db.Column(db.Integer, nullable=True)
    odoo_ticket_id = db.Column(db.Integer, nullable=True)

    # SLA timing fields
    sla_time = db.Column(db.Integer, default=24)
    raise_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=True)

    # Location and device tracking
    country = db.Column(db.String(100), default='Unknown')
    source_device = db.Column(db.String(50), default='web')

    # Enhanced escalation fields
    EndDate = db.Column(db.DateTime, nullable=True)
    EscalationLevel = db.Column(db.String(20), default='normal')
    EscalationReason = db.Column(db.String(500), nullable=True)
    EscalationTimestamp = db.Column(db.DateTime, nullable=True)
    EscalatedTo = db.Column(db.String(100), nullable=True)
    SLABreachStatus = db.Column(db.String(50), default='Within SLA')
    AutoEscalated = db.Column(db.Boolean, default=False)
    EscalationHistory = db.Column(db.Text, nullable=True)
    CurrentAssignedRole = db.Column(db.String(50), default='bot')
    SLATarget = db.Column(db.DateTime, nullable=True)
    OriginalSLATarget = db.Column(db.DateTime, nullable=True)

    # Device information fields
    device_type = db.Column(db.String(50), nullable=True)
    operating_system = db.Column(db.String(100), nullable=True)
    browser = db.Column(db.String(100), nullable=True)
    browser_version = db.Column(db.String(50), nullable=True)
    os_version = db.Column(db.String(50), nullable=True)
    device_brand = db.Column(db.String(100), nullable=True)
    device_model = db.Column(db.String(100), nullable=True)
    device_fingerprint = db.Column(db.String(255), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)


class Organization(db.Model):
    __tablename__ = 'Organizations'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    domain = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('Users.UserID'))
    is_active = db.Column(db.Boolean, default=True)


class FAQ(db.Model):
    __tablename__ = 'FAQ'

    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100))
    language = db.Column(db.String(10), default='en')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Partner(db.Model):
    __tablename__ = 'partners'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    partner_type = db.Column(db.String(50), nullable=False)  # ICP, YCP
    email = db.Column(db.String(255), nullable=False, unique=True)
    contact_person = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(20), default='active')  # active, suspended
    api_key = db.Column(db.String(255), nullable=True)
    webhook_url = db.Column(db.String(500), nullable=True)
    escalation_settings = db.Column(db.Text, nullable=True)  # JSON
    sla_settings = db.Column(db.Text, nullable=True)  # JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Statistics
    total_tickets_handled = db.Column(db.Integer, default=0)
    avg_resolution_time = db.Column(db.Float, default=0.0)  # in hours
    satisfaction_rating = db.Column(db.Float, default=0.0)


class EscalationLevel(db.Model):
    __tablename__ = 'EscalationLevels'

    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    threshold_hours = db.Column(db.Integer, nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('Users.id'))
    is_active = db.Column(db.Boolean, default=True)


class SLARule(db.Model):
    __tablename__ = 'SLARules'

    id = db.Column(db.Integer, primary_key=True)
    priority = db.Column(db.String(20), nullable=False)
    response_time_hours = db.Column(db.Integer, nullable=False)
    resolution_time_hours = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, default=True)

# Additional models needed by app.py


class Category(db.Model):
    __tablename__ = 'Categories'
    CategoryID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(50), nullable=False)
    Team = db.Column(db.String(50), nullable=False)
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)


class Message(db.Model):
    __tablename__ = 'Messages'
    MessageID = db.Column(db.Integer, primary_key=True)
    TicketID = db.Column(db.Integer, db.ForeignKey('Tickets.TicketID'))
    SenderID = db.Column(db.Integer, db.ForeignKey('Users.UserID'))
    Content = db.Column(db.Text, nullable=False)
    IsAdminReply = db.Column(db.Boolean, default=False)
    IsBotResponse = db.Column(db.Boolean, default=False)
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)


class CommonQuery(db.Model):
    __tablename__ = 'CommonQueries'
    QueryID = db.Column(db.Integer, primary_key=True)
    CategoryID = db.Column(db.Integer, db.ForeignKey('Categories.CategoryID'))
    Question = db.Column(db.String(255), nullable=False)
    Solution = db.Column(db.Text, nullable=False)
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)
    UpdatedAt = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


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


class FAQCategory(db.Model):
    __tablename__ = 'faq_categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    icon = db.Column(db.String(50), default='question-circle')
    color = db.Column(db.String(20), default='#007bff')
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Workflow(db.Model):
    __tablename__ = 'workflows'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    config = db.Column(db.Text, nullable=False)  # JSON configuration
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class WorkflowStep(db.Model):
    __tablename__ = 'workflow_steps'
    id = db.Column(db.Integer, primary_key=True)
    workflow_id = db.Column(db.Integer, db.ForeignKey(
        'workflows.id'), nullable=False)
    # condition, action, response
    step_type = db.Column(db.String(50), nullable=False)
    config = db.Column(db.Text, nullable=False)  # JSON configuration
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    workflow = db.relationship(
        'Workflow', backref=db.backref('steps', lazy=True))


class SLALog(db.Model):
    """SLA Tracking and Monitoring"""
    __tablename__ = 'sla_logs'

    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey(
        'Tickets.TicketID'), nullable=False)
    # 0=Bot, 1=ICP, 2=YouCloud
    escalation_level = db.Column(db.Integer, nullable=False)
    level_name = db.Column(db.String(50), nullable=False)  # Bot, ICP, YouCloud
    sla_target_hours = db.Column(db.Float, nullable=False)
    # on_time, at_risk, breached
    status = db.Column(db.String(20), default='on_time')
    logged_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    escalated_at = db.Column(db.DateTime, nullable=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
    is_breached = db.Column(db.Boolean, default=False)
    breach_time = db.Column(db.DateTime, nullable=True)
    resolution_method = db.Column(
        db.String(50), nullable=True)  # Bot, ICP, YouCloud
    assigned_partner_id = db.Column(
        db.Integer, db.ForeignKey('partners.id'), nullable=True)

    # Relationships
    ticket = db.relationship(
        'Ticket', backref=db.backref('sla_logs', lazy=True))
    assigned_partner = db.relationship(
        'Partner', backref=db.backref('sla_logs', lazy=True))


class TicketStatusLog(db.Model):
    """Workflow Logs / Timeline View"""
    __tablename__ = 'ticket_status_logs'

    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey(
        'Tickets.TicketID'), nullable=False)
    old_status = db.Column(db.String(50), nullable=True)
    new_status = db.Column(db.String(50), nullable=False)
    # Name of who changed it
    changed_by = db.Column(db.String(255), nullable=True)
    changed_by_id = db.Column(
        db.Integer, db.ForeignKey('Users.UserID'), nullable=True)
    # user, admin, system, bot
    changed_by_type = db.Column(db.String(20), nullable=False)
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)
    escalation_level = db.Column(db.Integer, nullable=True)
    # on_time, at_risk, breached
    sla_status = db.Column(db.String(20), default='on_time')
    notes = db.Column(db.Text, nullable=True)
    comment = db.Column(db.Text, nullable=True)
    # JSON for additional data
    metadata_json = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    ticket = db.relationship(
        'Ticket', backref=db.backref('status_logs', lazy=True))
    changed_by_user = db.relationship(
        'User', backref=db.backref('status_changes', lazy=True))


class AuditLog(db.Model):
    """Comprehensive Audit Logging"""
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(100), nullable=False)
    # ticket, user, partner, etc.
    resource_type = db.Column(db.String(50), nullable=False)
    resource_id = db.Column(db.Integer, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'Users.UserID'), nullable=True)
    # admin, user, system, api
    user_type = db.Column(db.String(20), nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    details = db.Column(db.Text, nullable=True)  # JSON with action details
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('audit_logs', lazy=True))


class EscalationRule(db.Model):
    """Automated Escalation Rules"""
    __tablename__ = 'escalation_rules'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    # critical, high, medium, low
    priority = db.Column(db.String(20), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey(
        'Categories.CategoryID'), nullable=True)
    level_0_sla_hours = db.Column(db.Float, default=0.0)  # Bot response time
    level_1_sla_hours = db.Column(db.Float, default=4.0)  # ICP response time
    level_2_sla_hours = db.Column(
        db.Float, default=24.0)  # YouCloud response time
    auto_escalate = db.Column(db.Boolean, default=True)
    notification_enabled = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BotConfiguration(db.Model):
    """Bot Integration Configuration"""
    __tablename__ = 'bot_configurations'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    # dialogflow, rasa, custom
    bot_type = db.Column(db.String(50), nullable=False)
    api_endpoint = db.Column(db.String(500), nullable=True)
    api_key = db.Column(db.String(255), nullable=True)
    config_data = db.Column(db.Text, nullable=True)  # JSON configuration
    is_active = db.Column(db.Boolean, default=True)
    fallback_to_human = db.Column(db.Boolean, default=True)
    confidence_threshold = db.Column(db.Float, default=0.7)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BotInteraction(db.Model):
    """Bot Interaction Logs"""
    __tablename__ = 'bot_interactions'

    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey(
        'Tickets.TicketID'), nullable=True)
    user_message = db.Column(db.Text, nullable=False)
    bot_response = db.Column(db.Text, nullable=False)
    confidence_score = db.Column(db.Float, nullable=True)
    intent_detected = db.Column(db.String(255), nullable=True)
    was_resolved = db.Column(db.Boolean, default=False)
    escalated_to_human = db.Column(db.Boolean, default=False)
    # Whether the interaction was successful
    success = db.Column(db.Boolean, default=True)
    # Response time in milliseconds
    response_time = db.Column(db.Float, nullable=True)
    session_id = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    ticket = db.relationship(
        'Ticket', backref=db.backref('bot_interactions', lazy=True))
