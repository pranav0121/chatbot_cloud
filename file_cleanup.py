#!/usr/bin/env python3
"""
File Cleanup Service - Automatically delete uploaded files after 3 days
"""

import os
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
import threading
import atexit

logger = logging.getLogger(__name__)

class FileCleanupService:
    def __init__(self, upload_folder, retention_days=3):
        self.upload_folder = Path(upload_folder)
        self.retention_days = retention_days
        self.cleanup_interval = 86400  # 24 hours in seconds
        self._timer = None
        self._is_running = False
        
        # Create imgsent folder if it doesn't exist
        self.imgsent_folder = self.upload_folder / 'imgsent'
        self.imgsent_folder.mkdir(exist_ok=True)
        
        logger.info(f"File cleanup service initialized for folder: {self.upload_folder}")
        logger.info(f"Files will be deleted after {self.retention_days} days")
    
    def start(self):
        """Start the cleanup service"""
        if not self._is_running:
            self._is_running = True
            self._schedule_cleanup()
            logger.info("File cleanup service started")
    
    def stop(self):
        """Stop the cleanup service"""
        if self._timer:
            self._timer.cancel()
        self._is_running = False
        logger.info("File cleanup service stopped")
    
    def _schedule_cleanup(self):
        """Schedule the next cleanup run"""
        if self._is_running:
            self._timer = threading.Timer(self.cleanup_interval, self._run_cleanup)
            self._timer.daemon = True
            self._timer.start()
    
    def _run_cleanup(self):
        """Run the cleanup process"""
        try:
            deleted_count = self.cleanup_old_files()
            logger.info(f"Cleanup completed. Deleted {deleted_count} files.")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
        finally:
            # Schedule next cleanup
            self._schedule_cleanup()
    
    def cleanup_old_files(self):
        """Delete files older than retention_days"""
        if not self.upload_folder.exists():
            return 0
        
        cutoff_time = datetime.now() - timedelta(days=self.retention_days)
        deleted_count = 0
        
        # Check both main upload folder and imgsent subfolder
        folders_to_check = [self.upload_folder, self.imgsent_folder]
        
        for folder in folders_to_check:
            if not folder.exists():
                continue
                
            for file_path in folder.iterdir():
                if file_path.is_file():
                    try:
                        # Get file creation time
                        file_time = datetime.fromtimestamp(file_path.stat().st_ctime)
                        
                        if file_time < cutoff_time:
                            file_path.unlink()
                            deleted_count += 1
                            logger.debug(f"Deleted old file: {file_path.name}")
                            
                    except Exception as e:
                        logger.error(f"Error deleting file {file_path}: {e}")
        
        return deleted_count
    
    def move_to_imgsent(self, file_path):
        """Move file to imgsent folder for cleanup tracking"""
        try:
            source_path = Path(file_path)
            if source_path.exists():
                dest_path = self.imgsent_folder / source_path.name
                source_path.rename(dest_path)
                logger.debug(f"Moved file to imgsent: {source_path.name}")
                return str(dest_path)
        except Exception as e:
            logger.error(f"Error moving file to imgsent: {e}")
        return file_path

# Global cleanup service instance
cleanup_service = None

def init_cleanup_service(upload_folder, retention_days=3):
    """Initialize and start the cleanup service"""
    global cleanup_service
    if cleanup_service is None:
        cleanup_service = FileCleanupService(upload_folder, retention_days)
        cleanup_service.start()
        
        # Register cleanup on exit
        atexit.register(lambda: cleanup_service.stop() if cleanup_service else None)
    
    return cleanup_service

def get_cleanup_service():
    """Get the global cleanup service instance"""
    return cleanup_service
