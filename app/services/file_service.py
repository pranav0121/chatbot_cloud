import os
import uuid
import mimetypes
from werkzeug.utils import secure_filename
from PIL import Image
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class FileService:
    """Service for handling file uploads and management"""
    
    @staticmethod
    def allowed_file(filename):
        """Check if file extension is allowed"""
        if '.' not in filename:
            return False
        ext = filename.rsplit('.', 1)[1].lower()
        return ext in current_app.config['ALLOWED_EXTENSIONS']
    
    @staticmethod
    def get_file_type(filename):
        """Get file type category"""
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        
        image_exts = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
        document_exts = {'pdf', 'doc', 'docx', 'txt', 'rtf'}
        archive_exts = {'zip', 'rar', '7z'}
        
        if ext in image_exts:
            return 'image'
        elif ext in document_exts:
            return 'document'
        elif ext in archive_exts:
            return 'archive'
        else:
            return 'other'
    
    @staticmethod
    def generate_unique_filename(original_filename):
        """Generate a unique filename while preserving extension"""
        name, ext = os.path.splitext(secure_filename(original_filename))
        unique_name = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
        return unique_name
    
    @staticmethod
    def save_uploaded_file(file, complaint_id, user_id):
        """Save uploaded file and return file info"""
        try:
            if not file or not file.filename:
                raise ValueError("No file provided")
            
            if not FileService.allowed_file(file.filename):
                raise ValueError(f"File type not allowed: {file.filename}")
            
            # Generate unique filename
            unique_filename = FileService.generate_unique_filename(file.filename)
            
            # Create upload directory structure
            upload_dir = os.path.join(current_app.instance_path, current_app.config['UPLOAD_FOLDER'])
            complaint_dir = os.path.join(upload_dir, str(complaint_id))
            os.makedirs(complaint_dir, exist_ok=True)
            
            # Save file
            file_path = os.path.join(complaint_dir, unique_filename)
            file.save(file_path)
            
            # Get file info
            file_size = os.path.getsize(file_path)
            file_type = FileService.get_file_type(file.filename)
              # Try to get MIME type
            mime_type = None
            try:
                mime_type, _ = mimetypes.guess_type(file_path)
            except:
                pass
            
            # Create thumbnail for images
            thumbnail_path = None
            is_image = file_type == 'image'
            if is_image:
                thumbnail_path = FileService.create_thumbnail(file_path, complaint_dir)
            
            file_info = {
                'original_filename': file.filename,
                'stored_filename': unique_filename,
                'file_path': file_path,
                'file_size': file_size,
                'file_type': file_type,
                'mime_type': mime_type,
                'is_image': is_image,
                'thumbnail_path': thumbnail_path
            }
            
            return file_info
            
        except Exception as e:
            logger.error(f"File upload failed: {e}")
            raise
    
    @staticmethod
    def create_thumbnail(image_path, output_dir, size=(150, 150)):
        """Create thumbnail for image"""
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Create thumbnail
                img.thumbnail(size, Image.Resampling.LANCZOS)
                
                # Generate thumbnail filename
                base_name = os.path.splitext(os.path.basename(image_path))[0]
                thumbnail_name = f"{base_name}_thumb.jpg"
                thumbnail_path = os.path.join(output_dir, thumbnail_name)
                
                # Save thumbnail
                img.save(thumbnail_path, 'JPEG', quality=85)
                
                return thumbnail_path
                
        except Exception as e:
            logger.error(f"Thumbnail creation failed: {e}")
            return None
    
    @staticmethod
    def delete_file(file_path):
        """Delete file from filesystem"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
        except Exception as e:
            logger.error(f"File deletion failed: {e}")
        return False
    
    @staticmethod
    def get_file_size_readable(size_bytes):
        """Convert bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    @staticmethod
    def validate_file_size(file):
        """Validate file size against maximum allowed"""
        max_size = current_app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)  # 16MB default
        
        # Get file size
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)  # Reset file pointer
        
        if size > max_size:
            max_size_readable = FileService.get_file_size_readable(max_size)
            raise ValueError(f"File too large. Maximum size allowed: {max_size_readable}")
        
        return True
