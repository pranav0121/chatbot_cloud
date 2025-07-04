#!/usr/bin/env python3
"""
Database initialization module to avoid circular imports
"""

from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy instance
db = SQLAlchemy()

def init_app(app):
    """Initialize the database with the Flask app"""
    db.init_app(app)
    return db
