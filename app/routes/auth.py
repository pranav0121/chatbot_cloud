from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app.models.user import User
from app.forms.auth import LoginForm, RegisterForm, ProfileForm, ForgotPasswordForm
from app import db
import re

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        email = form.email.data.lower()
        password = form.password.data
        remember = form.remember.data
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact support.', 'error')
                return render_template('auth/login.html', form=form)
            
            login_user(user, remember=remember)
            
            # Set user's language preference in session
            session['language'] = user.language
            
            flash(f'Welcome back, {user.get_full_name()}!', 'success')
            
            # Redirect to next page or dashboard based on role
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            elif user.is_admin():
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('auth/login.html', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegisterForm()
    
    if form.validate_on_submit():
        # Create new user
        user = User(
            name=form.full_name.data,
            email=form.email.data.lower(),
            phone=form.phone.data,
            language=form.language.data,
            role='user'
        )
        user.set_password(form.password.data)
        
        try:
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'error')
    
    return render_template('auth/register.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    session.pop('language', None)
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile management"""
    form = ProfileForm()
      # Pre-populate form with current user data
    if request.method == 'GET':
        form.full_name.data = current_user.name
        form.phone.data = current_user.phone
        form.language.data = current_user.language
    
    if form.validate_on_submit():
        # Validate current password if changing password
        if form.new_password.data and not current_user.check_password(form.current_password.data):
            flash('Current password is incorrect.', 'error')
            return render_template('auth/profile.html', form=form)
          # Update user profile
        try:
            current_user.name = form.full_name.data
            current_user.phone = form.phone.data
            current_user.language = form.language.data
            
            if form.new_password.data:
                current_user.set_password(form.new_password.data)
            
            # Update session language
            session['language'] = form.language.data
            
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash('Failed to update profile. Please try again.', 'error')
    
    return render_template('auth/profile.html', form=form)

@bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Forgot password - placeholder for future implementation"""
    form = ForgotPasswordForm()
    
    if form.validate_on_submit():
        email = form.email.data.lower()
        
        # In a real implementation, you would:
        # 1. Generate a password reset token
        # 2. Send reset email
        # 3. Store token with expiration
        
        flash('If an account with this email exists, you will receive password reset instructions.', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html', form=form)
