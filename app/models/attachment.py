from app import db
from datetime import datetime
import os

class Attachment(db.Model):
    __tablename__ = 'attachments'
    
    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaints.id'), nullable=False)
    message_id = db.Column(db.Integer, db.ForeignKey('messages.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    file_type = db.Column(db.String(100), nullable=False)
    mime_type = db.Column(db.String(100))
    is_image = db.Column(db.Boolean, default=False)
    thumbnail_path = db.Column(db.String(500))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    message = db.relationship('Message', backref='attachments')
    
    @property
    def file_extension(self):
        """Get file extension"""
        return os.path.splitext(self.original_filename)[1].lower()
    
    def get_file_icon(self):
        """Get appropriate icon for file type"""
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        document_extensions = ['.pdf', '.doc', '.docx', '.txt', '.rtf']
        
        if self.file_extension in image_extensions:
            return 'fa-image'
        elif self.file_extension in document_extensions:
            return 'fa-file-text'
        elif self.file_extension == '.zip':
            return 'fa-file-archive'
        else:
            return 'fa-file'
    
    def get_file_size_formatted(self):
        """Get formatted file size"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def is_downloadable(self):
        """Check if file can be downloaded"""
        return os.path.exists(self.file_path)
    
    def can_preview(self):
        """Check if file can be previewed in browser"""
        previewable_types = ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.txt']
        return self.file_extension in previewable_types
    
    def to_dict(self):
        """Convert attachment to dictionary for JSON responses"""
        return {
            'id': self.id,
            'complaint_id': self.complaint_id,
            'message_id': self.message_id,
            'user_id': self.user_id,
            'original_filename': self.original_filename,
            'stored_filename': self.stored_filename,
            'file_size': self.file_size,
            'file_size_formatted': self.get_file_size_formatted(),
            'file_type': self.file_type,
            'mime_type': self.mime_type,
            'is_image': self.is_image,
            'file_icon': self.get_file_icon(),
            'can_preview': self.can_preview(),
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None
        }
    
    def __repr__(self):
        return f'<Attachment {self.id}: {self.original_filename}>'
