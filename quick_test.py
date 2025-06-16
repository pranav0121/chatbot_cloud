#!/usr/bin/env python3
"""
Quick test of database connectivity and admin fix
"""

import os
import sys

print("=== QUICK DATABASE TEST ===")
print(f"Python version: {sys.version}")
print(f"Working directory: {os.getcwd()}")

try:
    # Test imports
    print("\n1. Testing imports...")
    import pyodbc
    print(f"✅ pyodbc imported - version: {pyodbc.version}")
    
    from flask import Flask
    print("✅ Flask imported")
    
    from flask_sqlalchemy import SQLAlchemy
    print("✅ SQLAlchemy imported")
    
    from werkzeug.security import generate_password_hash
    print("✅ Werkzeug imported")
    
    # Test ODBC drivers
    print("\n2. Testing ODBC drivers...")
    drivers = pyodbc.drivers()
    sql_drivers = [d for d in drivers if 'SQL Server' in d]
    print(f"Available SQL Server drivers: {sql_drivers}")
    
    if not sql_drivers:
        print("❌ No SQL Server ODBC drivers found!")
        print("Please install SQL Server ODBC Driver")
        exit(1)
    
    # Test MSSQL connection
    print("\n3. Testing MSSQL connection...")
    server = 'PRANAV\\SQLEXPRESS'
    database = 'SupportChatbot'
    
    # Try to connect
    driver = sql_drivers[0]  # Use first available driver
    conn_string = f"DRIVER={{{driver}}};SERVER={server};DATABASE=master;Trusted_Connection=yes;"
    
    print(f"Using driver: {driver}")
    print(f"Connection string: {conn_string}")
    
    conn = pyodbc.connect(conn_string, timeout=10)
    print("✅ Connected to SQL Server!")
    
    cursor = conn.cursor()
    
    # Check if database exists
    cursor.execute("SELECT COUNT(*) FROM sys.databases WHERE name = ?", database)
    db_exists = cursor.fetchone()[0] > 0
    print(f"Database '{database}' exists: {db_exists}")
    
    # Create database if it doesn't exist
    if not db_exists:
        print(f"Creating database '{database}'...")
        cursor.execute(f"CREATE DATABASE [{database}]")
        conn.commit()
        print(f"✅ Database '{database}' created!")
    
    cursor.close()
    conn.close()
    
    # Now test Flask app with MSSQL
    print("\n4. Testing Flask app with MSSQL...")
    
    # Import app components
    from config import Config
    config = Config()
    
    print(f"Database URI: {config.SQLALCHEMY_DATABASE_URI}")
    
    if 'mssql' in config.SQLALCHEMY_DATABASE_URI.lower():
        print("✅ Configuration is set for MSSQL")
    else:
        print("❌ Configuration is NOT set for MSSQL")
        exit(1)
    
    # Create Flask app
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize SQLAlchemy
    db = SQLAlchemy(app)
    
    # Define User model
    class User(db.Model):
        __tablename__ = 'Users'
        UserID = db.Column(db.Integer, primary_key=True)
        Name = db.Column(db.String(100), nullable=False)
        Email = db.Column(db.String(255), unique=True, nullable=False)
        PasswordHash = db.Column(db.String(255), nullable=False)
        OrganizationName = db.Column(db.String(200))
        Position = db.Column(db.String(100))
        PriorityLevel = db.Column(db.String(20), default='medium')
        IsActive = db.Column(db.Boolean, default=True)
        IsAdmin = db.Column(db.Boolean, default=False)
        CreatedAt = db.Column(db.DateTime)
        LastLogin = db.Column(db.DateTime)
    
    with app.app_context():
        print("✅ Flask app context created")
        
        # Create tables
        print("Creating tables...")
        db.create_all()
        print("✅ Tables created successfully")
        
        # Check for admin user
        admin_email = 'admin@youcloudtech.com'
        admin = User.query.filter_by(Email=admin_email).first()
        
        if admin:
            print(f"Found admin user: {admin.Name} (Active: {admin.IsActive}, Admin: {admin.IsAdmin})")
            
            # Fix admin user
            admin.IsActive = True
            admin.IsAdmin = True
            admin.PasswordHash = generate_password_hash('admin123')
            db.session.commit()
            print("✅ Admin user updated")
            
        else:
            print("Creating new admin user...")
            from datetime import datetime
            
            new_admin = User(
                Name='System Administrator',
                Email=admin_email,
                PasswordHash=generate_password_hash('admin123'),
                OrganizationName='YouCloudTech',
                Position='Administrator',
                PriorityLevel='critical',
                IsActive=True,
                IsAdmin=True,
                CreatedAt=datetime.utcnow()
            )
            
            db.session.add(new_admin)
            db.session.commit()
            print("✅ New admin user created")
        
        # Verify admin user
        verified_admin = User.query.filter_by(Email=admin_email, IsAdmin=True, IsActive=True).first()
        
        if verified_admin:
            print(f"\n🎯 ADMIN USER VERIFIED:")
            print(f"   ID: {verified_admin.UserID}")
            print(f"   Email: {verified_admin.Email}")
            print(f"   Name: {verified_admin.Name}")
            print(f"   Active: {verified_admin.IsActive}")
            print(f"   Admin: {verified_admin.IsAdmin}")
            
            print(f"\n✅ SUCCESS! Admin credentials:")
            print(f"📧 Email: admin@youcloudtech.com")
            print(f"🔑 Password: admin123")
            print(f"🌐 Admin URL: http://localhost:5000/auth/admin/login")
            
        else:
            print("❌ Admin user verification failed")
            exit(1)

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please install missing dependencies:")
    print("pip install pyodbc flask flask-sqlalchemy werkzeug")
    
except pyodbc.Error as e:
    print(f"❌ Database error: {e}")
    print("Please check:")
    print("1. SQL Server is running")
    print("2. SQL Server instance name is correct")
    print("3. Windows Authentication is enabled")
    
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()

print("\n=== TEST COMPLETE ===")
