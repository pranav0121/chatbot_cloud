from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

# Define auth blueprint
auth_bp = Blueprint('auth', __name__)

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

# Define auth blueprint
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Import here to avoid circular imports
    from app import db, User
    from datetime import datetime
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(Email=email).first()
        
        if not user:
            flash('Email not found. Please check your email or register first.', 'error')
            return redirect(url_for('auth.login'))
        
        if not check_password_hash(user.PasswordHash, password):
            flash('Invalid password. Please try again.', 'error')
            return redirect(url_for('auth.login'))
        
        if not user.IsActive:
            flash('Your account has been deactivated. Please contact support.', 'error')
            return redirect(url_for('auth.login'))
        
        # Update last login time
        user.LastLogin = datetime.utcnow()
        try:
            db.session.commit()
        except:
            db.session.rollback()
        
        login_user(user)
        flash(f'Welcome back, {user.Name}!', 'success')
        return redirect(url_for('index'))
    
    try:
        return render_template('login_simple.html')
    except Exception as e:
        return f"Error rendering login template: {str(e)}"

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # Import here to avoid circular imports
    from app import db, User
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        organization = request.form.get('organization')
        position = request.form.get('position')
        department = request.form.get('department')
        phone = request.form.get('phone')
        priority = request.form.get('priority')
        
        # Validate required fields
        if not all([name, email, password, organization, priority]):
            flash('Please fill in all required fields', 'error')
            return redirect(url_for('auth.register'))
        
        # Validate priority level
        valid_priorities = ['low', 'medium', 'high', 'critical']
        if priority not in valid_priorities:
            flash('Invalid priority level selected', 'error')
            return redirect(url_for('auth.register'))
        
        # Check if user already exists
        user = User.query.filter_by(Email=email).first()
        if user:
            flash('Email address already registered', 'warning')
            return redirect(url_for('auth.register'))
        
        # Create new user with organization and priority information
        new_user = User(
            Name=name,
            Email=email,
            PasswordHash=generate_password_hash(password),
            OrganizationName=organization,
            Position=position,
            Department=department,
            Phone=phone,
            PriorityLevel=priority
        )
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! You can now log in with your credentials.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'error')
            return redirect(url_for('auth.register'))
    
    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
