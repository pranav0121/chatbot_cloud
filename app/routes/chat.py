from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models.complaint import Complaint
from app.models.message import Message
from app.models.attachment import Attachment
from app.services.chatbot_service import ChatbotService
from app.services.file_service import FileService
from app.services.translation_service import TranslationService
from app import db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
bp = Blueprint('chat', __name__)

@bp.route('/new')
@login_required
def new_chat():
    """Start a new chat/complaint"""
    # Create a new complaint
    complaint = Complaint(
        user_id=current_user.id,
        title='New Support Request',
        description='',
        category='',
        status='open'
    )
    
    db.session.add(complaint)
    db.session.commit()
    
    # Generate initial bot greeting
    greeting = ChatbotService.generate_bot_response(
        "hello", current_user, complaint
    )
    
    ChatbotService.create_bot_message(
        greeting, complaint.id, current_user.language
    )
    
    # Send categories as follow-up message (ensure every user sees categories)
    categories_message = ChatbotService._initiate_complaint_flow(current_user)
    ChatbotService.create_bot_message(
        categories_message, complaint.id, current_user.language
    )
    
    return redirect(url_for('chat.conversation', complaint_id=complaint.id))

@bp.route('/<int:complaint_id>')
@login_required
def conversation(complaint_id):
    """Chat conversation view"""
    complaint = Complaint.query.get_or_404(complaint_id)
    
    # Check access permissions
    if not current_user.is_admin() and complaint.user_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Get messages for this conversation
    messages = Message.query.filter_by(complaint_id=complaint_id).order_by(
        Message.created_at.asc()
    ).all()
    
    # Translate messages if needed
    user_language = current_user.language
    for message in messages:
        message.display_content = TranslationService.translate_message_content(
            message, user_language
        )
    
    return render_template('chat/conversation.html', 
                         complaint=complaint, messages=messages)

@bp.route('/<int:complaint_id>/send', methods=['POST'])
@login_required
def send_message(complaint_id):
    """Send a message in chat"""
    complaint = Complaint.query.get_or_404(complaint_id)
    
    # Check access permissions
    if not current_user.is_admin() and complaint.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    content = request.form.get('content', '').strip()
    if not content:
        return jsonify({'error': 'Message content is required'}), 400
    
    try:
        # Detect message language
        detected_language = TranslationService.detect_language(content)
        
        # Create user message
        user_message = Message(
            complaint_id=complaint_id,
            user_id=current_user.id,
            content=content,
            message_type='admin' if current_user.is_admin() else 'user',
            language=detected_language
        )
        
        db.session.add(user_message)
        db.session.commit()
        
        # Generate bot response if user is not admin
        if not current_user.is_admin():
            bot_response = ChatbotService.generate_bot_response(
                content, current_user, complaint
            )
            
            if bot_response:
                ChatbotService.create_bot_message(
                    bot_response, complaint_id, current_user.language
                )
        
        # Update complaint status and metadata
        complaint.updated_at = datetime.utcnow()
        if not complaint.title or complaint.title == 'New Support Request':
            # Set title based on first user message
            complaint.title = content[:100] + ('...' if len(content) > 100 else '')
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': {
                'id': user_message.id,
                'content': user_message.content,
                'sender_name': user_message.get_sender_name(),
                'message_type': user_message.message_type,
                'created_at': user_message.created_at.isoformat(),
                'message_class': user_message.get_message_class()
            }
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to send message: {e}")
        return jsonify({'error': 'Failed to send message'}), 500

@bp.route('/<int:complaint_id>/upload', methods=['POST'])
@login_required
def upload_file(complaint_id):
    """Upload file attachment"""
    complaint = Complaint.query.get_or_404(complaint_id)
    
    # Check access permissions
    if not current_user.is_admin() and complaint.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file selected'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        # Validate file size
        FileService.validate_file_size(file)
        
        # Save the file
        file_info = FileService.save_uploaded_file(file, complaint_id, current_user.id)
        
        # Create attachment record
        attachment = Attachment(
            complaint_id=complaint_id,
            user_id=current_user.id,
            original_filename=file_info['original_filename'],
            stored_filename=file_info['stored_filename'],
            file_path=file_info['file_path'],
            file_size=file_info['file_size'],
            file_type=file_info['file_type'],
            mime_type=file_info['mime_type'],
            is_image=file_info['is_image'],
            thumbnail_path=file_info['thumbnail_path']
        )
        
        db.session.add(attachment)
        db.session.commit()
        
        # Create a message about the file upload
        upload_message = f"📎 Uploaded file: {file_info['original_filename']}"
        message = Message(
            complaint_id=complaint_id,
            user_id=current_user.id,
            content=upload_message,
            message_type='admin' if current_user.is_admin() else 'user',
            language=current_user.language
        )
        
        db.session.add(message)
        attachment.message_id = message.id
        db.session.commit()
        
        return jsonify({
            'success': True,
            'attachment': attachment.to_dict(),
            'message': message.to_dict()
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        logger.error(f"File upload failed: {e}")
        return jsonify({'error': 'File upload failed'}), 500

@bp.route('/<int:complaint_id>/messages')
@login_required
def get_messages(complaint_id):
    """Get messages for a conversation (AJAX endpoint)"""
    complaint = Complaint.query.get_or_404(complaint_id)
    
    # Check access permissions
    if not current_user.is_admin() and complaint.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Get messages since a specific timestamp
    since = request.args.get('since')
    query = Message.query.filter_by(complaint_id=complaint_id)
    
    if since:
        try:
            since_datetime = datetime.fromisoformat(since.replace('Z', '+00:00'))
            query = query.filter(Message.created_at > since_datetime)
        except ValueError:
            pass
    
    messages = query.order_by(Message.created_at.asc()).all()
    
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
        'messages': message_data,
        'complaint_status': complaint.status
    })

@bp.route('/<int:complaint_id>/close', methods=['POST'])
@login_required
def close_conversation(complaint_id):
    """Close a conversation/complaint"""
    complaint = Complaint.query.get_or_404(complaint_id)
    
    # Only admins or complaint owner can close
    if not current_user.is_admin() and complaint.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    resolution = request.form.get('resolution', '').strip()
    
    try:
        complaint.mark_resolved(resolution)
        db.session.commit()
        
        # Create a system message about closure
        close_message = "This conversation has been marked as resolved."
        if resolution:
            close_message += f"\n\nResolution: {resolution}"
        
        message = Message(
            complaint_id=complaint_id,
            user_id=current_user.id,
            content=close_message,
            message_type='admin' if current_user.is_admin() else 'user',
            language=current_user.language
        )
        
        db.session.add(message)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Conversation closed successfully'})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to close conversation: {e}")
        return jsonify({'error': 'Failed to close conversation'}), 500
