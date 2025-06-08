from app import db
from datetime import datetime

class Complaint(db.Model):
    __tablename__ = 'complaints'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    status = db.Column(db.String(20), default='open')  # open, in_progress, resolved, closed
    order_id = db.Column(db.String(100))
    resolution = db.Column(db.Text)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    resolved_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    messages = db.relationship('Message', backref='complaint', lazy='dynamic', cascade='all, delete-orphan')
    attachments = db.relationship('Attachment', backref='complaint', lazy='dynamic', cascade='all, delete-orphan')
    assignee = db.relationship('User', foreign_keys=[assigned_to], backref='assigned_complaints')
    
    @property
    def complaint_number(self):
        """Generate a formatted complaint number"""
        return f"CP{self.id:06d}"
    
    def get_status_color(self):
        """Get status color for UI"""
        colors = {
            'open': 'red',
            'in_progress': 'yellow',
            'resolved': 'green',
            'closed': 'gray'
        }
        return colors.get(self.status, 'gray')
    
    def get_priority_color(self):
        """Get priority color for UI"""
        colors = {
            'low': 'green',
            'medium': 'yellow',
            'high': 'orange',
            'urgent': 'red'
        }
        return colors.get(self.priority, 'gray')
    
    def mark_resolved(self, resolution_text=None):
        """Mark complaint as resolved"""
        self.status = 'resolved'
        self.resolved_at = datetime.utcnow()
        if resolution_text:
            self.resolution = resolution_text
    
    def to_dict(self):
        """Convert complaint to dictionary for JSON responses"""
        return {
            'id': self.id,
            'complaint_number': self.complaint_number,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else None,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'priority': self.priority,
            'status': self.status,
            'order_id': self.order_id,
            'resolution': self.resolution,
            'assigned_to': self.assigned_to,
            'assignee_name': self.assignee.name if self.assignee else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'message_count': self.messages.count(),
            'attachment_count': self.attachments.count()
        }
    
    def __repr__(self):
        return f'<Complaint {self.complaint_number}: {self.title}>'
