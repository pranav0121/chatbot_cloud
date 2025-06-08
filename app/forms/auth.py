# filepath: c:\Users\prana\Downloads\chatbot_cloud\app\forms\auth.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models.user import User
import re

class LoginForm(FlaskForm):
    """Login form"""
    email = StringField('Email', validators=[
        DataRequired(message='Email is required.'),
        Email(message='Please enter a valid email address.')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required.')
    ])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegisterForm(FlaskForm):
    """Registration form"""
    full_name = StringField('Full Name', validators=[
        DataRequired(message='Name is required.'),
        Length(min=2, max=100, message='Name must be between 2 and 100 characters.')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='Email is required.'),
        Email(message='Please enter a valid email address.')
    ])
    phone = StringField('Phone Number', validators=[
        Length(max=20, message='Phone number cannot exceed 20 characters.')
    ])
    language = SelectField('Preferred Language', choices=[
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
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required.'),
        Length(min=6, message='Password must be at least 6 characters long.')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password.'),
        EqualTo('password', message='Passwords must match.')
    ])
    submit = SubmitField('Create Account')
    
    def validate_email(self, email):
        """Check if email already exists"""
        user = User.query.filter_by(email=email.data.lower()).first()
        if user:
            raise ValidationError('An account with this email already exists.')

class ProfileForm(FlaskForm):
    """Profile update form"""
    full_name = StringField('Full Name', validators=[
        DataRequired(message='Name is required.'),
        Length(min=2, max=100, message='Name must be between 2 and 100 characters.')
    ])
    phone = StringField('Phone Number', validators=[
        Length(max=20, message='Phone number cannot exceed 20 characters.')
    ])
    language = SelectField('Preferred Language', choices=[
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
    current_password = PasswordField('Current Password')
    new_password = PasswordField('New Password', validators=[
        Length(min=6, message='Password must be at least 6 characters long.')
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        EqualTo('new_password', message='Passwords must match.')
    ])
    submit = SubmitField('Update Profile')
    
    def validate_new_password(self, new_password):
        """Validate new password requirements"""
        if new_password.data and not self.current_password.data:
            raise ValidationError('Current password is required to change password.')

class ForgotPasswordForm(FlaskForm):
    """Forgot password form"""
    email = StringField('Email', validators=[
        DataRequired(message='Email is required.'),
        Email(message='Please enter a valid email address.')
    ])
    submit = SubmitField('Send Reset Instructions')
