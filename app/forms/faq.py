# filepath: c:\Users\prana\Downloads\chatbot_cloud\app\forms\faq.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length

class FAQForm(FlaskForm):
    """FAQ form for admin"""
    question = StringField('Question', validators=[
        DataRequired(message='Question is required.'),
        Length(min=10, max=500, message='Question must be between 10 and 500 characters.')
    ])
    answer = TextAreaField('Answer', validators=[
        DataRequired(message='Answer is required.'),
        Length(min=10, max=2000, message='Answer must be between 10 and 2000 characters.')
    ])
    category = SelectField('Category', choices=[
        ('billing', 'Billing & Payments'),
        ('technical', 'Technical Support'),
        ('account', 'Account Management'),
        ('features', 'Features & Services'),
        ('general', 'General Information'),
        ('troubleshooting', 'Troubleshooting'),
        ('security', 'Security & Privacy'),
        ('other', 'Other')
    ], validators=[DataRequired(message='Please select a category.')])
    language = SelectField('Language', choices=[
        ('en', 'English'),
        ('es', 'Español'),
        ('fr', 'Français'),
        ('de', 'Deutsch'),
        ('it', 'Italiano'),
        ('pt', 'Português'),
        ('zh', '中文'),
        ('ja', '日本語'),
        ('ko', '한국어'),
        ('ar', 'العربية'),
        ('hi', 'हिन्दी'),
        ('ru', 'Русский')
    ], default='en')
    submit = SubmitField('Save FAQ')
