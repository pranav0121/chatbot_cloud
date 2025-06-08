from app import db
from datetime import datetime

class FAQ(db.Model):
    __tablename__ = 'faqs'
    
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    language = db.Column(db.String(5), nullable=False, default='en')
    is_active = db.Column(db.Boolean, default=True)
    view_count = db.Column(db.Integer, default=0)
    helpful_count = db.Column(db.Integer, default=0)
    not_helpful_count = db.Column(db.Integer, default=0)
    priority = db.Column(db.Integer, default=0)  # Higher number = higher priority
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = db.relationship('User', backref='created_faqs')
    
    def increment_view(self):
        """Increment view count"""
        self.view_count += 1
        db.session.commit()
    
    def mark_helpful(self):
        """Mark FAQ as helpful"""
        self.helpful_count += 1
        db.session.commit()
    
    def mark_not_helpful(self):
        """Mark FAQ as not helpful"""
        self.not_helpful_count += 1
        db.session.commit()
    
    def get_helpfulness_ratio(self):
        """Get helpfulness ratio (0-1)"""
        total_votes = self.helpful_count + self.not_helpful_count
        if total_votes == 0:
            return 0.5
        return self.helpful_count / total_votes
    
    def get_category_display(self):
        """Get formatted category name"""
        return self.category.replace('_', ' ').title()
    
    @classmethod
    def get_categories(cls, language='en'):
        """Get all available categories for a language"""
        return db.session.query(cls.category).filter_by(
            language=language, 
            is_active=True
        ).distinct().all()
    
    @classmethod
    def search(cls, query, language='en', category=None):
        """Search FAQs by query"""
        search_filter = cls.query.filter(
            cls.is_active == True,
            cls.language == language
        )
        
        if category:
            search_filter = search_filter.filter(cls.category == category)
        
        if query:
            search_terms = f"%{query}%"
            search_filter = search_filter.filter(
                db.or_(
                    cls.question.ilike(search_terms),
                    cls.answer.ilike(search_terms)
                )
            )
        
        return search_filter.order_by(cls.priority.desc(), cls.view_count.desc()).all()
    
    def to_dict(self):
        """Convert FAQ to dictionary for JSON responses"""
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'category': self.category,
            'category_display': self.get_category_display(),
            'language': self.language,
            'is_active': self.is_active,
            'view_count': self.view_count,
            'helpful_count': self.helpful_count,
            'not_helpful_count': self.not_helpful_count,
            'helpfulness_ratio': self.get_helpfulness_ratio(),
            'priority': self.priority,
            'created_by': self.created_by,
            'creator_name': self.creator.name if self.creator else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<FAQ {self.id}: {self.question[:50]}...>'
