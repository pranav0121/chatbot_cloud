from app import db
from datetime import datetime

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaints.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    content_translated = db.Column(db.Text)  # Translated content
    message_type = db.Column(db.String(20), default='user')  # user, admin, bot    is_internal = db.Column(db.Boolean, default=False)  # Internal admin notes
    language = db.Column(db.String(5), default='en')
    message_metadata = db.Column(db.JSON)  # Store additional data like translation info
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def is_from_admin(self):
        """Check if message is from admin or bot"""
        return self.message_type in ['admin', 'bot']
    
    def is_from_user(self):
        """Check if message is from user"""
        return self.message_type == 'user'
    
    def get_display_content(self, target_language='en'):
        """Get content in specified language"""
        if target_language == self.language:
            return self.content
        return self.content_translated or self.content
    
    def get_sender_name(self):
        """Get sender name"""
        if self.message_type == 'bot':
            return 'YouCloudPay Assistant'
        elif self.user:
            return self.user.get_full_name()
        return 'Unknown'
    
    def get_message_class(self):
        """Get CSS class for message styling"""
        if self.message_type == 'user':
            return 'message-user'
        elif self.message_type == 'admin':
            return 'message-admin'
        else:
            return 'message-bot'
    
    def to_dict(self):
        """Convert message to dictionary for JSON responses"""
        return {
            'id': self.id,
            'complaint_id': self.complaint_id,
            'user_id': self.user_id,
            'sender_name': self.get_sender_name(),
            'content': self.content,
            'content_translated': self.content_translated,
            'message_type': self.message_type,            'is_internal': self.is_internal,
            'language': self.language,
            'metadata': self.message_metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'message_class': self.get_message_class()
        }
    
    def __repr__(self):
        return f'<Message {self.id}: {self.message_type} - {self.content[:50]}...>'
