# filepath: c:\Users\prana\Downloads\chatbot_cloud\app\forms\complaints.py
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length

class CreateComplaintForm(FlaskForm):
    """Create complaint form"""
    subject = StringField('Subject', validators=[
        DataRequired(message='Subject is required.'),
        Length(min=5, max=200, message='Subject must be between 5 and 200 characters.')
    ])
    category = SelectField('Category', choices=[
        ('billing', 'Billing & Payments'),
        ('technical', 'Technical Support'),
        ('account', 'Account Issues'),
        ('feature', 'Feature Request'),
        ('bug', 'Bug Report'),
        ('general', 'General Inquiry'),
        ('other', 'Other')
    ], validators=[DataRequired(message='Please select a category.')])
    priority = SelectField('Priority', choices=[
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ], default='normal', validators=[DataRequired(message='Please select a priority.')])
    description = TextAreaField('Description', validators=[
        DataRequired(message='Description is required.'),
        Length(min=10, max=2000, message='Description must be between 10 and 2000 characters.')
    ])
    attachment = FileField('Attachment (Optional)', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx', 'txt'], 
                   'Only images, PDFs, Word documents, and text files are allowed.')
    ])
    submit = SubmitField('Submit Complaint')
