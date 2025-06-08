from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models.user import User
from app.models.complaint import Complaint
from app.models.message import Message
from app.models.faq import FAQ
from app.models.attachment import Attachment
from app.services.translation_service import TranslationService
from app import db
from datetime import datetime, timedelta
from functools import wraps
import logging

logger = logging.getLogger(__name__)
bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard"""    # Get key statistics
    total_complaints = Complaint.query.count()
    resolved_complaints = Complaint.query.filter_by(status='resolved').count()
    open_complaints = Complaint.query.filter_by(status='open').count()
    
    # Calculate resolution rate
    resolution_rate = round((resolved_complaints / total_complaints * 100) if total_complaints > 0 else 0)
    
    # Calculate new users today
    today = datetime.utcnow().date()
    new_users_today = User.query.filter(
        db.func.date(User.created_at) == today
    ).count()
    
    # Calculate average response time (simplified - using hours)
    avg_response_time = 2  # Default placeholder - you can implement actual calculation
    
    stats = {
        'total_users': User.query.count(),
        'total_complaints': total_complaints,
        'open_complaints': open_complaints,
        'resolved_complaints': resolved_complaints,
        'resolution_rate': resolution_rate,
        'avg_response_time': avg_response_time,
        'new_users_today': new_users_today,
        'total_faqs': FAQ.query.filter_by(is_active=True).count(),
        'total_messages': Message.query.count()
    }
    
    # Recent complaints
    recent_complaints = Complaint.query.order_by(
        Complaint.created_at.desc()
    ).limit(10).all()
    
    # Complaint statistics by category
    category_stats = db.session.query(
        Complaint.category,
        db.func.count(Complaint.id).label('count')
    ).group_by(Complaint.category).all()
      # Monthly complaint trends
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    daily_complaints = db.session.query(
        db.func.date(Complaint.created_at).label('date'),
        db.func.count(Complaint.id).label('count')
    ).filter(
        Complaint.created_at >= thirty_days_ago
    ).group_by(db.func.date(Complaint.created_at)).all()
    
    # Get resolved complaints for chart
    daily_resolved = db.session.query(
        db.func.date(Complaint.updated_at).label('date'),
        db.func.count(Complaint.id).label('count')
    ).filter(
        Complaint.updated_at >= thirty_days_ago,
        Complaint.status == 'resolved'
    ).group_by(db.func.date(Complaint.updated_at)).all()
    # Create chart data structure
    # Generate last 7 days
    chart_labels = []
    chart_complaints = []
    chart_resolved = []
    
    for i in range(6, -1, -1):
        current_date = datetime.utcnow().date() - timedelta(days=i)
        chart_labels.append(current_date.strftime('%b %d'))
        
        # Count complaints for this date
        complaint_count = 0
        for dc in daily_complaints:
            if dc.date and dc.date == current_date:
                complaint_count = dc.count
                break
        chart_complaints.append(complaint_count)
        
        # Count resolved for this date
        resolved_count = 0
        for dr in daily_resolved:
            if dr.date and dr.date == current_date:
                resolved_count = dr.count
                break
        chart_resolved.append(resolved_count)
    
    chart_data = {
        'labels': chart_labels,
        'complaints': chart_complaints,
        'resolved': chart_resolved
    }
    
    return render_template('admin/dashboard.html',
                         stats=stats,
                         recent_complaints=recent_complaints,
                         category_stats=category_stats,
                         daily_complaints=daily_complaints,
                         chart_data=chart_data)

@bp.route('/complaints')
@login_required
@admin_required
def complaints():
    """Manage complaints"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    category_filter = request.args.get('category', '')
    priority_filter = request.args.get('priority', '')
    search_query = request.args.get('q', '')
    
    # Build query
    query = Complaint.query
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    if category_filter:
        query = query.filter_by(category=category_filter)
    
    if priority_filter:
        query = query.filter_by(priority=priority_filter)
    
    if search_query:
        search_terms = f"%{search_query}%"
        query = query.filter(
            db.or_(
                Complaint.title.ilike(search_terms),
                Complaint.description.ilike(search_terms),
                User.name.ilike(search_terms),
                User.email.ilike(search_terms)
            )
        ).join(User)
    
    # Paginate results
    complaints = query.order_by(Complaint.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # Get filter options
    categories = db.session.query(Complaint.category).distinct().all()
    statuses = ['open', 'in_progress', 'resolved', 'closed']
    priorities = ['low', 'medium', 'high', 'urgent']
    
    return render_template('admin/complaints.html',
                         complaints=complaints,
                         categories=[c[0] for c in categories if c[0]],
                         statuses=statuses,
                         priorities=priorities,
                         filters={
                             'status': status_filter,
                             'category': category_filter,
                             'priority': priority_filter,
                             'search': search_query
                         })

@bp.route('/complaint/<int:complaint_id>')
@login_required
@admin_required
def view_complaint(complaint_id):
    """View and manage specific complaint"""
    complaint = Complaint.query.get_or_404(complaint_id)
    
    # Get all messages
    messages = Message.query.filter_by(complaint_id=complaint_id).order_by(
        Message.created_at.asc()
    ).all()
    
    # Get all attachments
    attachments = Attachment.query.filter_by(complaint_id=complaint_id).order_by(
        Attachment.uploaded_at.desc()
    ).all()
    
    return render_template('admin/complaint_detail.html',
                         complaint=complaint,
                         messages=messages,
                         attachments=attachments)

@bp.route('/complaint/<int:complaint_id>/update', methods=['POST'])
@login_required
@admin_required
def update_complaint(complaint_id):
    """Update complaint details"""
    complaint = Complaint.query.get_or_404(complaint_id)
    
    try:
        # Update complaint fields
        complaint.status = request.form.get('status', complaint.status)
        complaint.priority = request.form.get('priority', complaint.priority)
        complaint.category = request.form.get('category', complaint.category)
        
        assigned_to = request.form.get('assigned_to')
        if assigned_to:
            complaint.assigned_to = int(assigned_to) if assigned_to != 'none' else None
        
        resolution = request.form.get('resolution', '').strip()
        if resolution:
            complaint.resolution = resolution
        
        # Mark as resolved if status changed to resolved
        if complaint.status == 'resolved' and not complaint.resolved_at:
            complaint.resolved_at = datetime.utcnow()
        
        complaint.updated_at = datetime.utcnow()
        db.session.commit()
        
        flash('Complaint updated successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to update complaint: {e}")
        flash('Failed to update complaint.', 'error')
    
    return redirect(url_for('admin.view_complaint', complaint_id=complaint_id))

@bp.route('/users')
@login_required
@admin_required
def users():
    """Manage users"""
    page = request.args.get('page', 1, type=int)
    role_filter = request.args.get('role', '')
    search_query = request.args.get('q', '')
    
    # Build query
    query = User.query
    
    if role_filter:
        query = query.filter_by(role=role_filter)
    
    if search_query:
        search_terms = f"%{search_query}%"
        query = query.filter(
            db.or_(
                User.name.ilike(search_terms),
                User.email.ilike(search_terms)
            )
        )
    
    # Paginate results
    users = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/users.html',
                         users=users,
                         filters={
                             'role': role_filter,
                             'search': search_query
                         })

@bp.route('/user/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    """Toggle user active status"""
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        return jsonify({'error': 'Cannot deactivate your own account'}), 400
    
    try:
        user.is_active = not user.is_active
        db.session.commit()
        
        status = 'activated' if user.is_active else 'deactivated'
        return jsonify({
            'success': True,
            'message': f'User {status} successfully',
            'is_active': user.is_active
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to toggle user status: {e}")
        return jsonify({'error': 'Failed to update user status'}), 500

@bp.route('/faqs')
@login_required
@admin_required
def faqs():
    """Manage FAQs"""
    page = request.args.get('page', 1, type=int)
    category_filter = request.args.get('category', '')
    language_filter = request.args.get('language', '')
    search_query = request.args.get('q', '')
    
    # Build query
    query = FAQ.query
    
    if category_filter:
        query = query.filter_by(category=category_filter)
    
    if language_filter:
        query = query.filter_by(language=language_filter)
    
    if search_query:
        search_terms = f"%{search_query}%"
        query = query.filter(
            db.or_(
                FAQ.question.ilike(search_terms),
                FAQ.answer.ilike(search_terms)
            )
        )
    
    # Paginate results
    faqs = query.order_by(FAQ.priority.desc(), FAQ.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # Get filter options
    categories = db.session.query(FAQ.category).distinct().all()
    languages = TranslationService.get_supported_languages()
    
    return render_template('admin/faqs.html',
                         faqs=faqs,
                         categories=[c[0] for c in categories if c[0]],
                         languages=languages,
                         filters={
                             'category': category_filter,
                             'language': language_filter,
                             'search': search_query
                         })

@bp.route('/faq/new', methods=['GET', 'POST'])
@login_required
@admin_required
def create_faq():
    """Create new FAQ"""
    if request.method == 'POST':
        question = request.form.get('question', '').strip()
        answer = request.form.get('answer', '').strip()
        category = request.form.get('category', '').strip()
        language = request.form.get('language', 'en')
        priority = request.form.get('priority', 0, type=int)
        
        if not question or not answer or not category:
            flash('Question, answer, and category are required.', 'error')
            return render_template('admin/faq_form.html', form_data=request.form)
        
        try:
            faq = FAQ(
                question=question,
                answer=answer,
                category=category,
                language=language,
                priority=priority,
                created_by=current_user.id
            )
            
            db.session.add(faq)
            db.session.commit()
            
            flash('FAQ created successfully!', 'success')
            return redirect(url_for('admin.faqs'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to create FAQ: {e}")
            flash('Failed to create FAQ.', 'error')
    
    languages = TranslationService.get_supported_languages()
    return render_template('admin/faq_form.html', languages=languages)

@bp.route('/faq/<int:faq_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_faq(faq_id):
    """Edit FAQ"""
    faq = FAQ.query.get_or_404(faq_id)
    
    if request.method == 'POST':
        question = request.form.get('question', '').strip()
        answer = request.form.get('answer', '').strip()
        category = request.form.get('category', '').strip()
        language = request.form.get('language', 'en')
        priority = request.form.get('priority', 0, type=int)
        is_active = bool(request.form.get('is_active'))
        
        if not question or not answer or not category:
            flash('Question, answer, and category are required.', 'error')
            return render_template('admin/faq_form.html', faq=faq, form_data=request.form)
        
        try:
            faq.question = question
            faq.answer = answer
            faq.category = category
            faq.language = language
            faq.priority = priority
            faq.is_active = is_active
            faq.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            flash('FAQ updated successfully!', 'success')
            return redirect(url_for('admin.faqs'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to update FAQ: {e}")
            flash('Failed to update FAQ.', 'error')
    
    languages = TranslationService.get_supported_languages()
    return render_template('admin/faq_form.html', faq=faq, languages=languages)

@bp.route('/faq/<int:faq_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_faq(faq_id):
    """Delete FAQ"""
    faq = FAQ.query.get_or_404(faq_id)
    
    try:
        db.session.delete(faq)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'FAQ deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to delete FAQ: {e}")
        return jsonify({'error': 'Failed to delete FAQ'}), 500

@bp.route('/analytics')
@login_required
@admin_required
def analytics():
    """Analytics and reports"""
    # Date range filters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Default to last 30 days
    if not start_date:
        start_date = (datetime.utcnow() - timedelta(days=30)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = datetime.utcnow().strftime('%Y-%m-%d')
    
    # Convert to datetime objects
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
    
    # Complaint analytics
    complaint_stats = {
        'total': Complaint.query.filter(
            Complaint.created_at.between(start_dt, end_dt)
        ).count(),
        'by_status': dict(db.session.query(
            Complaint.status,
            db.func.count(Complaint.id)
        ).filter(
            Complaint.created_at.between(start_dt, end_dt)
        ).group_by(Complaint.status).all()),
        'by_category': dict(db.session.query(
            Complaint.category,
            db.func.count(Complaint.id)
        ).filter(
            Complaint.created_at.between(start_dt, end_dt)
        ).group_by(Complaint.category).all())
    }
    
    # User analytics
    user_stats = {
        'new_users': User.query.filter(
            User.created_at.between(start_dt, end_dt)
        ).count(),
        'active_users': User.query.filter_by(is_active=True).count()
    }
    
    # FAQ analytics
    popular_faqs = db.session.query(FAQ).filter(
        FAQ.is_active == True
    ).order_by(FAQ.view_count.desc()).limit(10).all()
    
    return render_template('admin/analytics.html',
                         complaint_stats=complaint_stats,
                         user_stats=user_stats,
                         popular_faqs=popular_faqs,
                         start_date=start_date,
                         end_date=end_date)
