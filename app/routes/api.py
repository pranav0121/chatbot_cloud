from flask import Blueprint, request, jsonify, send_file, current_app
from flask_login import login_required, current_user
from app.models.complaint import Complaint
from app.models.message import Message
from app.models.attachment import Attachment
from app.models.faq import FAQ
from app.models.user import User
from app.services.translation_service import TranslationService
from app.services.file_service import FileService
from app import db
import os
import logging
from datetime import datetime, timedelta
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
bp = Blueprint('api', __name__)

@bp.route('/translate', methods=['POST'])
@login_required
def translate_text():
    """Translate text API endpoint"""
    data = request.get_json()
    
    if not data or 'text' not in data or 'target_language' not in data:
        return jsonify({'error': 'Text and target_language are required'}), 400
    
    text = data['text']
    target_language = data['target_language']
    source_language = data.get('source_language')
    
    try:
        translated_text = TranslationService.translate_text(
            text, target_language, source_language
        )
        
        return jsonify({
            'success': True,
            'translated_text': translated_text,
            'source_language': source_language,
            'target_language': target_language
        })
        
    except Exception as e:
        logger.error(f"Translation API error: {e}")
        return jsonify({'error': 'Translation failed'}), 500

@bp.route('/detect-language', methods=['POST'])
@login_required
def detect_language():
    """Detect language API endpoint"""
    data = request.get_json()
    
    if not data or 'text' not in data:
        return jsonify({'error': 'Text is required'}), 400
    
    try:
        detected_language = TranslationService.detect_language(data['text'])
        
        return jsonify({
            'success': True,
            'detected_language': detected_language
        })
        
    except Exception as e:
        logger.error(f"Language detection API error: {e}")
        return jsonify({'error': 'Language detection failed'}), 500

@bp.route('/faq/search', methods=['GET'])
def search_faqs():
    """Search FAQs API endpoint"""
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    language = request.args.get('language', 'en')
    limit = request.args.get('limit', 10, type=int)
    
    try:
        faqs = FAQ.search(query, language, category)
        
        # Limit results
        if limit > 0:
            faqs = faqs[:limit]
        
        return jsonify({
            'success': True,
            'faqs': [faq.to_dict() for faq in faqs]
        })
        
    except Exception as e:
        logger.error(f"FAQ search API error: {e}")
        return jsonify({'error': 'FAQ search failed'}), 500

@bp.route('/faq/<int:faq_id>/helpful', methods=['POST'])
@login_required
def mark_faq_helpful(faq_id):
    """Mark FAQ as helpful"""
    faq = FAQ.query.get_or_404(faq_id)
    
    try:
        faq.mark_helpful()
        
        return jsonify({
            'success': True,
            'helpful_count': faq.helpful_count,
            'helpfulness_ratio': faq.get_helpfulness_ratio()
        })
        
    except Exception as e:
        logger.error(f"FAQ helpful API error: {e}")
        return jsonify({'error': 'Failed to mark as helpful'}), 500

@bp.route('/faq/<int:faq_id>/not-helpful', methods=['POST'])
@login_required
def mark_faq_not_helpful(faq_id):
    """Mark FAQ as not helpful"""
    faq = FAQ.query.get_or_404(faq_id)
    
    try:
        faq.mark_not_helpful()
        
        return jsonify({
            'success': True,
            'not_helpful_count': faq.not_helpful_count,
            'helpfulness_ratio': faq.get_helpfulness_ratio()
        })
        
    except Exception as e:
        logger.error(f"FAQ not helpful API error: {e}")
        return jsonify({'error': 'Failed to mark as not helpful'}), 500

@bp.route('/complaints/<int:complaint_id>/messages', methods=['GET'])
@login_required
def get_complaint_messages(complaint_id):
    """Get messages for a complaint"""
    complaint = Complaint.query.get_or_404(complaint_id)
    
    # Check access permissions
    if not current_user.is_admin() and complaint.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        messages = Message.query.filter_by(complaint_id=complaint_id).order_by(
            Message.created_at.asc()
        ).all()
        
        # Translate messages if needed
        user_language = current_user.language
        message_data = []
        for message in messages:
            message_dict = message.to_dict()
            message_dict['display_content'] = TranslationService.translate_message_content(
                message, user_language
            )
            message_data.append(message_dict)
        
        return jsonify({
            'success': True,
            'messages': message_data
        })
        
    except Exception as e:
        logger.error(f"Get messages API error: {e}")
        return jsonify({'error': 'Failed to get messages'}), 500

@bp.route('/complaints/stats', methods=['GET'])
@login_required
def get_complaint_stats():
    """Get complaint statistics"""
    try:
        if current_user.is_admin():
            # Admin sees all complaints
            stats = {
                'total': Complaint.query.count(),
                'open': Complaint.query.filter_by(status='open').count(),
                'in_progress': Complaint.query.filter_by(status='in_progress').count(),
                'resolved': Complaint.query.filter_by(status='resolved').count(),
                'closed': Complaint.query.filter_by(status='closed').count()
            }
        else:
            # User sees only their complaints
            stats = {
                'total': Complaint.query.filter_by(user_id=current_user.id).count(),
                'open': Complaint.query.filter_by(user_id=current_user.id, status='open').count(),
                'in_progress': Complaint.query.filter_by(user_id=current_user.id, status='in_progress').count(),
                'resolved': Complaint.query.filter_by(user_id=current_user.id, status='resolved').count(),
                'closed': Complaint.query.filter_by(user_id=current_user.id, status='closed').count()
            }
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Get complaint stats API error: {e}")
        return jsonify({'error': 'Failed to get statistics'}), 500

@bp.route('/attachments/<int:attachment_id>/download')
@login_required
def download_attachment(attachment_id):
    """Download attachment file"""
    attachment = Attachment.query.get_or_404(attachment_id)
    
    # Check access permissions
    complaint = attachment.complaint
    if not current_user.is_admin() and complaint.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        if not os.path.exists(attachment.file_path):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(
            attachment.file_path,
            as_attachment=True,
            download_name=attachment.original_filename
        )
        
    except Exception as e:
        logger.error(f"Download attachment error: {e}")
        return jsonify({'error': 'Download failed'}), 500

@bp.route('/attachments/<int:attachment_id>/preview')
@login_required
def preview_attachment(attachment_id):
    """Preview attachment file (for images and PDFs)"""
    attachment = Attachment.query.get_or_404(attachment_id)
    
    # Check access permissions
    complaint = attachment.complaint
    if not current_user.is_admin() and complaint.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        if not attachment.can_preview():
            return jsonify({'error': 'File cannot be previewed'}), 400
        
        if not os.path.exists(attachment.file_path):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(attachment.file_path)
        
    except Exception as e:
        logger.error(f"Preview attachment error: {e}")
        return jsonify({'error': 'Preview failed'}), 500

@bp.route('/attachments/<int:attachment_id>/thumbnail')
@login_required
def get_thumbnail(attachment_id):
    """Get thumbnail for image attachment"""
    attachment = Attachment.query.get_or_404(attachment_id)
    
    # Check access permissions
    complaint = attachment.complaint
    if not current_user.is_admin() and complaint.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        if not attachment.is_image or not attachment.thumbnail_path:
            return jsonify({'error': 'Thumbnail not available'}), 404
        
        if not os.path.exists(attachment.thumbnail_path):
            return jsonify({'error': 'Thumbnail not found'}), 404
        
        return send_file(attachment.thumbnail_path)
        
    except Exception as e:
        logger.error(f"Get thumbnail error: {e}")
        return jsonify({'error': 'Thumbnail failed'}), 500

@bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': db.func.now(),
        'version': '1.0.0'
    })

# Admin Analytics API endpoints
@bp.route('/admin/analytics/metrics', methods=['GET'])
@login_required
def admin_analytics_metrics():
    """Get key metrics for admin analytics dashboard"""
    if not current_user.is_admin():
        return jsonify({'error': 'Access denied'}), 403
        
    try:
        # Get time range filters
        days = request.args.get('days', 30, type=int)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Calculate metrics
        total_complaints = Complaint.query.filter(
            Complaint.created_at.between(start_date, end_date)
        ).count()
        
        resolved_complaints = Complaint.query.filter(
            Complaint.created_at.between(start_date, end_date),
            Complaint.status == 'resolved'
        ).count()
        
        resolution_rate = round((resolved_complaints / total_complaints * 100) if total_complaints > 0 else 0)
        
        avg_response_time = 2  # Placeholder - implement actual calculation
        
        metrics = {
            'total_complaints': total_complaints,
            'resolved_complaints': resolved_complaints,
            'resolution_rate': resolution_rate,
            'avg_response_time': avg_response_time,
            'new_users': User.query.filter(
                User.created_at.between(start_date, end_date)
            ).count()
        }
        
        return jsonify({
            'success': True,
            'metrics': metrics
        })
        
    except Exception as e:
        logger.error(f"Admin metrics API error: {e}")
        return jsonify({'error': 'Failed to get metrics'}), 500

@bp.route('/admin/analytics/complaints-trend', methods=['GET'])
@login_required
def admin_complaints_trend():
    """Get complaints trend data for admin analytics"""
    if not current_user.is_admin():
        return jsonify({'error': 'Access denied'}), 403
        
    try:
        # Get time range filters
        days = request.args.get('days', 30, type=int)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get daily complaints
        daily_complaints = db.session.query(
            db.func.date(Complaint.created_at).label('date'),
            db.func.count(Complaint.id).label('count')
        ).filter(
            Complaint.created_at.between(start_date, end_date)
        ).group_by(db.func.date(Complaint.created_at)).all()
        
        # Get daily resolved
        daily_resolved = db.session.query(
            db.func.date(Complaint.updated_at).label('date'),
            db.func.count(Complaint.id).label('count')
        ).filter(
            Complaint.updated_at.between(start_date, end_date),
            Complaint.status == 'resolved'
        ).group_by(db.func.date(Complaint.updated_at)).all()
        
        # Format data
        trend_data = []
        for i in range(days):
            current_date = end_date.date() - timedelta(days=days-i-1)
            complaints = sum(1 for dc in daily_complaints if dc.date == current_date)
            resolved = sum(1 for dr in daily_resolved if dr.date == current_date)
            
            trend_data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'display_date': current_date.strftime('%b %d'),
                'complaints': complaints,
                'resolved': resolved
            })
        
        return jsonify({
            'success': True,
            'trend_data': trend_data
        })
        
    except Exception as e:
        logger.error(f"Complaints trend API error: {e}")
        return jsonify({'error': 'Failed to get trend data'}), 500

@bp.route('/admin/analytics/status-distribution', methods=['GET'])
@login_required
def admin_status_distribution():
    """Get complaint status distribution for admin analytics"""
    if not current_user.is_admin():
        return jsonify({'error': 'Access denied'}), 403
        
    try:
        status_counts = db.session.query(
            Complaint.status,
            db.func.count(Complaint.id).label('count')
        ).group_by(Complaint.status).all()
        
        distribution = {}
        for status, count in status_counts:
            distribution[status] = count
        
        return jsonify({
            'success': True,
            'distribution': distribution
        })
        
    except Exception as e:
        logger.error(f"Status distribution API error: {e}")
        return jsonify({'error': 'Failed to get status distribution'}), 500

@bp.route('/admin/analytics/category-breakdown', methods=['GET'])
@login_required
def admin_category_breakdown():
    """Get complaint category breakdown for admin analytics"""
    if not current_user.is_admin():
        return jsonify({'error': 'Access denied'}), 403
        
    try:
        category_counts = db.session.query(
            Complaint.category,
            db.func.count(Complaint.id).label('count')
        ).group_by(Complaint.category).all()
        
        breakdown = []
        for category, count in category_counts:
            if category:  # Skip empty categories
                breakdown.append({
                    'category': category,
                    'count': count
                })
        
        return jsonify({
            'success': True,
            'breakdown': breakdown
        })
        
    except Exception as e:
        logger.error(f"Category breakdown API error: {e}")
        return jsonify({'error': 'Failed to get category breakdown'}), 500

@bp.route('/admin/analytics/priority-distribution', methods=['GET'])
@login_required
def admin_priority_distribution():
    """Get complaint priority distribution for admin analytics"""
    if not current_user.is_admin():
        return jsonify({'error': 'Access denied'}), 403
        
    try:
        priority_counts = db.session.query(
            Complaint.priority,
            db.func.count(Complaint.id).label('count')
        ).group_by(Complaint.priority).all()
        
        distribution = {}
        for priority, count in priority_counts:
            distribution[priority] = count
        
        return jsonify({
            'success': True,
            'distribution': distribution
        })
        
    except Exception as e:
        logger.error(f"Priority distribution API error: {e}")
        return jsonify({'error': 'Failed to get priority distribution'}), 500

@bp.route('/admin/analytics/top-issues', methods=['GET'])
@login_required
def admin_top_issues():
    """Get top reported issues for admin analytics"""
    if not current_user.is_admin():
        return jsonify({'error': 'Access denied'}), 403
        
    try:
        # Simplified implementation - in production, you would use more 
        # sophisticated text analysis or categorization
        issues = db.session.query(
            Complaint.title,
            db.func.count(Complaint.id).label('count')
        ).group_by(Complaint.title).order_by(
            db.func.count(Complaint.id).desc()
        ).limit(10).all()
        
        top_issues = [{'issue': title, 'count': count} for title, count in issues]
        
        return jsonify({
            'success': True,
            'top_issues': top_issues
        })
        
    except Exception as e:
        logger.error(f"Top issues API error: {e}")
        return jsonify({'error': 'Failed to get top issues'}), 500

@bp.route('/admin/analytics/agent-performance', methods=['GET'])
@login_required
def admin_agent_performance():
    """Get agent performance metrics for admin analytics"""
    if not current_user.is_admin():
        return jsonify({'error': 'Access denied'}), 403
        
    try:
        # Get all admin users
        admin_users = User.query.filter_by(role='admin').all()
        
        performance = []
        for admin in admin_users:
            # Count complaints assigned to this admin
            assigned_count = Complaint.query.filter_by(assigned_to=admin.id).count()
            
            # Count resolved complaints
            resolved_count = Complaint.query.filter_by(
                assigned_to=admin.id, 
                status='resolved'
            ).count()
            
            # Calculate resolution rate
            resolution_rate = round((resolved_count / assigned_count * 100) 
                                    if assigned_count > 0 else 0)
            
            performance.append({
                'agent_id': admin.id,
                'agent_name': admin.name,
                'assigned_count': assigned_count,
                'resolved_count': resolved_count,
                'resolution_rate': resolution_rate,
                'avg_response_time': 2  # Placeholder
            })
        
        return jsonify({
            'success': True,
            'performance': performance
        })
        
    except Exception as e:
        logger.error(f"Agent performance API error: {e}")
        return jsonify({'error': 'Failed to get agent performance'}), 500

@bp.errorhandler(404)
def api_not_found(error):
    return jsonify({'error': 'API endpoint not found'}), 404

@bp.errorhandler(500)
def api_internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500
