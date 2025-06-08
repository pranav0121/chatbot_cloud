from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify, session
from flask_login import login_required, current_user
from app.models.user import User
from app.models.complaint import Complaint
from app.models.faq import FAQ
from app.models.message import Message
from app.forms.complaints import CreateComplaintForm
from app.services.translation_service import TranslationService
from app.services.file_service import FileService
from app import db
from datetime import datetime
import os

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    if current_user.is_admin():
        return redirect(url_for('admin.dashboard'))
    
    # Get user's complaints
    complaints = Complaint.query.filter_by(user_id=current_user.id).order_by(
        Complaint.created_at.desc()
    ).limit(10).all()
    
    # Get complaint statistics
    stats = {
        'total_complaints': Complaint.query.filter_by(user_id=current_user.id).count(),
        'open_complaints': Complaint.query.filter_by(
            user_id=current_user.id, status='open'
        ).count(),
        'resolved_complaints': Complaint.query.filter_by(
            user_id=current_user.id, status='resolved'
        ).count()    }
    
    return render_template('dashboard/index.html', 
                         complaints=complaints, stats=stats)

@bp.route('/complaints')
@login_required
def complaints():
    """List user's complaints"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    category_filter = request.args.get('category', '')
    
    # Build query
    query = Complaint.query.filter_by(user_id=current_user.id)
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    if category_filter:
        query = query.filter_by(category=category_filter)
    
    # Paginate results
    complaints = query.order_by(Complaint.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('complaints/index.html', complaints=complaints)

@bp.route('/complaints/create', methods=['GET', 'POST'])
@login_required
def create_complaint():
    """Create a new complaint"""
    form = CreateComplaintForm()
    
    if form.validate_on_submit():
        try:
            # Create complaint
            complaint = Complaint(
                subject=form.subject.data,
                category=form.category.data,
                priority=form.priority.data,
                description=form.description.data,
                user_id=current_user.id,
                status='open'
            )
            
            db.session.add(complaint)
            db.session.flush()  # Get the complaint ID
            
            # Handle file attachment if provided
            if form.attachment.data:
                file_service = FileService()
                attachment = file_service.save_attachment(
                    form.attachment.data, 
                    complaint.id, 
                    current_user.id
                )
                if attachment:
                    complaint.attachments.append(attachment)
            
            db.session.commit()
            
            flash('Your complaint has been submitted successfully!', 'success')
            return redirect(url_for('main.view_complaint', complaint_id=complaint.id))
            
        except Exception as e:
            db.session.rollback()
            flash('Failed to create complaint. Please try again.', 'error')
    
    return render_template('complaints/create.html', form=form)

@bp.route('/complaint/<int:complaint_id>')
@login_required
def view_complaint(complaint_id):
    """View specific complaint"""
    complaint = Complaint.query.get_or_404(complaint_id)
    
    # Check if user can access this complaint
    if not current_user.is_admin() and complaint.user_id != current_user.id:
        return redirect(url_for('main.complaints'))
    
    # Get messages for this complaint
    messages = Message.query.filter_by(complaint_id=complaint_id).order_by(
        Message.created_at.asc()
    ).all()
    
    # Translate messages if needed
    user_language = current_user.language
    for message in messages:
        if message.language != user_language:
            message.display_content = TranslationService.translate_message_content(
                message, user_language        )
        else:
            message.display_content = message.content
    
    return render_template('complaints/detail.html', 
                         complaint=complaint, messages=messages)

@bp.route('/faq')
def faq():
    """FAQ page"""
    search_query = request.args.get('q', '')
    category_filter = request.args.get('category', '')
    language = session.get('language', 'en')
    
    # Get FAQs based on filters
    faqs = FAQ.search(search_query, language, category_filter)
      # Get available categories
    categories = FAQ.get_categories(language)
    
    return render_template('faq/index.html', 
                         faqs=faqs, 
                         categories=categories,
                         search_query=search_query,
                         category_filter=category_filter)

@bp.route('/faq/<int:faq_id>')
def view_faq(faq_id):
    """View specific FAQ"""
    faq = FAQ.query.get_or_404(faq_id)
    
    # Increment view count
    faq.increment_view()
    
    # Get related FAQs
    related_faqs = FAQ.query.filter(
        FAQ.category == faq.category,
        FAQ.id != faq.id,
        FAQ.is_active == True,
        FAQ.language == faq.language
    ).limit(5).all()
    
    return render_template('faq/view.html', faq=faq, related_faqs=related_faqs)

@bp.route('/set-language/<language>')
def set_language(language):
    """Set user's language preference"""
    supported_languages = ['en', 'hi', 'te', 'mr', 'kn', 'ta']
    
    if language in supported_languages:
        session['language'] = language
        
        # Update user's language preference if logged in
        if current_user.is_authenticated:
            current_user.language = language
            db.session.commit()
    
    # Redirect back to referring page
    return redirect(request.referrer or url_for('main.index'))

@bp.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@bp.route('/contact')
def contact():
    """Contact page"""
    return render_template('contact.html')

@bp.route('/privacy')
def privacy():
    """Privacy policy page"""
    return render_template('privacy.html')

@bp.route('/terms')
def terms():
    """Terms of service page"""
    return render_template('terms.html')

@bp.route('/help')
def help():
    """Help page"""
    return render_template('help.html')

@bp.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Check database connectivity
        db.session.execute('SELECT 1')
        
        # Check if admin user exists
        admin_exists = User.query.filter_by(role='admin').first() is not None
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'admin_user': 'exists' if admin_exists else 'missing',
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500
