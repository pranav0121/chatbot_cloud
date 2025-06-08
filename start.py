#!/usr/bin/env python3
"""
YouCloudPay Chatbot - Startup and Testing Script
This script initializes the database, creates sample data, and starts the application.
"""

import os
import sys
from app import create_app, db
from app.models.user import User
from app.models.faq import FAQ
from app.models.complaint import Complaint

def create_admin_user(app):
    """Create admin user if not exists"""
    with app.app_context():
        admin_email = app.config.get('ADMIN_EMAIL', 'admin@youcloudpay.com')
        admin_password = app.config.get('ADMIN_PASSWORD', 'admin123')
        
        admin = User.query.filter_by(email=admin_email).first()
        if not admin:
            admin = User(
                name='Administrator',
                email=admin_email,
                role='admin',
                language='en',
                is_active=True
            )
            admin.set_password(admin_password)
            db.session.add(admin)
            db.session.commit()
            print(f"✅ Admin user created: {admin_email}")
        else:
            print(f"ℹ️  Admin user exists: {admin_email}")

def create_sample_users(app):
    """Create sample users for testing"""
    with app.app_context():
        sample_users = [
            {
                'name': 'John Doe',
                'email': 'john.doe@example.com',
                'role': 'user',
                'language': 'en'
            },
            {
                'name': 'Maria Garcia',
                'email': 'maria.garcia@example.com',
                'role': 'user',
                'language': 'es'
            },
            {
                'name': 'राज पटेल',
                'email': 'raj.patel@example.com',
                'role': 'user',
                'language': 'hi'
            }
        ]
        
        for user_data in sample_users:
            existing_user = User.query.filter_by(email=user_data['email']).first()
            if not existing_user:
                user = User(**user_data)
                user.set_password('password123')
                db.session.add(user)
        
        db.session.commit()
        print("✅ Sample users created")

def create_sample_faqs(app):
    """Create comprehensive FAQ database"""
    with app.app_context():
        faqs = [
            # English FAQs
            {
                'question': 'How do I reset my password?',
                'answer': 'To reset your password, click on the "Forgot Password" link on the login page. Enter your email address and follow the instructions sent to your email.',
                'category': 'account',
                'language': 'en',
                'priority': 10
            },
            {
                'question': 'What payment methods do you accept?',
                'answer': 'We accept all major credit cards (Visa, MasterCard, American Express), PayPal, bank transfers, and digital wallets like Google Pay and Apple Pay.',
                'category': 'billing',
                'language': 'en',
                'priority': 9
            },
            {
                'question': 'How do I contact customer support?',
                'answer': 'You can contact our 24/7 customer support through this chat system, email us at support@youcloudpay.com, or call +1-800-SUPPORT.',
                'category': 'general',
                'language': 'en',
                'priority': 8
            },
            {
                'question': 'Is my data secure with YouCloudPay?',
                'answer': 'Yes, we use bank-level encryption (AES-256) and comply with international security standards including ISO 27001 and SOC 2 Type II.',
                'category': 'security',
                'language': 'en',
                'priority': 9
            },
            {
                'question': 'How do I upgrade my account plan?',
                'answer': 'Go to Settings > Billing > Plans and select your desired plan. Changes take effect immediately and you\'ll only pay the prorated difference.',
                'category': 'account',
                'language': 'en',
                'priority': 7
            },
            {
                'question': 'Why is my transaction failing?',
                'answer': 'Transaction failures can occur due to insufficient funds, card restrictions, or network issues. Please check your payment method and try again.',
                'category': 'technical',
                'language': 'en',
                'priority': 8
            },
            {
                'question': 'How do I download my transaction history?',
                'answer': 'Go to Dashboard > Transactions > Export. You can download your transaction history in CSV or PDF format for any date range.',
                'category': 'features',
                'language': 'en',
                'priority': 6
            },
            # Hindi FAQs
            {
                'question': 'मैं अपना पासवर्ड कैसे रीसेट करूं?',
                'answer': 'अपना पासवर्ड रीसेट करने के लिए, लॉगिन पेज पर "पासवर्ड भूल गए" लिंक पर क्लिक करें। अपना ईमेल पता दर्ज करें और अपने ईमेल पर भेजे गए निर्देशों का पालन करें।',
                'category': 'account',
                'language': 'hi',
                'priority': 10
            },
            {
                'question': 'आप कौन से भुगतान तरीके स्वीकार करते हैं?',
                'answer': 'हम सभी प्रमुख क्रेडिट कार्ड (वीज़ा, मास्टरकार्ड, अमेरिकन एक्सप्रेस), पेपाल, बैंक ट्रांसफर, और डिजिटल वॉलेट जैसे Google Pay और PhonePe स्वीकार करते हैं।',
                'category': 'billing',
                'language': 'hi',
                'priority': 9
            },
            # Spanish FAQs
            {
                'question': '¿Cómo restablezco mi contraseña?',
                'answer': 'Para restablecer su contraseña, haga clic en el enlace "Olvidé mi contraseña" en la página de inicio de sesión. Ingrese su dirección de correo electrónico y siga las instrucciones enviadas a su correo.',
                'category': 'account',
                'language': 'es',
                'priority': 10
            },
            {
                'question': '¿Qué métodos de pago aceptan?',
                'answer': 'Aceptamos todas las principales tarjetas de crédito (Visa, MasterCard, American Express), PayPal, transferencias bancarias y billeteras digitales.',
                'category': 'billing',
                'language': 'es',
                'priority': 9
            }
        ]
        
        for faq_data in faqs:
            existing_faq = FAQ.query.filter_by(
                question=faq_data['question'],
                language=faq_data['language']
            ).first()
            
            if not existing_faq:
                faq = FAQ(**faq_data)
                db.session.add(faq)
        
        db.session.commit()
        print("✅ Sample FAQs created")

def create_sample_complaints(app):
    """Create sample complaints for testing"""
    with app.app_context():
        users = User.query.filter_by(role='user').all()
        if not users:
            return
        
        sample_complaints = [
            {
                'title': 'Payment Gateway Issue',
                'description': 'I am unable to complete my payment. The gateway shows an error message.',
                'category': 'technical',
                'priority': 'high',
                'status': 'open'
            },
            {
                'title': 'Account Access Problem',
                'description': 'I cannot access my account dashboard after the recent update.',
                'category': 'account',
                'priority': 'normal',
                'status': 'in_progress'
            },
            {
                'title': 'Billing Discrepancy',
                'description': 'There seems to be an extra charge on my monthly bill that I did not authorize.',
                'category': 'billing',
                'priority': 'high',
                'status': 'resolved'
            }
        ]
        
        for i, complaint_data in enumerate(sample_complaints):
            user = users[i % len(users)]
            complaint = Complaint(
                user_id=user.id,
                **complaint_data
            )
            db.session.add(complaint)
        
        db.session.commit()
        print("✅ Sample complaints created")

def test_application_health(app):
    """Test critical application functionality"""
    with app.app_context():
        try:
            # Test database connectivity
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
            print("✅ Database connection: OK")
            
            # Test user model
            user_count = User.query.count()
            print(f"✅ Users in database: {user_count}")
            
            # Test FAQ model
            faq_count = FAQ.query.count()
            print(f"✅ FAQs in database: {faq_count}")
            
            # Test complaint model
            complaint_count = Complaint.query.count()
            print(f"✅ Complaints in database: {complaint_count}")
            
            # Test admin user exists
            admin = User.query.filter_by(role='admin').first()
            if admin:
                print(f"✅ Admin user: {admin.email}")
            else:
                print("❌ No admin user found")
            
            return True
        except Exception as e:
            print(f"❌ Application health check failed: {e}")
            return False

def main():
    """Main startup function"""
    print("🚀 YouCloudPay Chatbot - Starting Up...")
    print("=" * 50)
    
    # Create Flask app
    app = create_app()
    
    with app.app_context():
        print("📦 Initializing database...")
        db.create_all()
        print("✅ Database tables created")
        
        print("\n👤 Setting up users...")
        create_admin_user(app)
        create_sample_users(app)
        
        print("\n❓ Setting up FAQs...")
        create_sample_faqs(app)
        
        print("\n📋 Setting up sample complaints...")
        create_sample_complaints(app)
        
        print("\n🔍 Running health checks...")
        if test_application_health(app):
            print("\n✅ All systems operational!")
        else:
            print("\n❌ Some issues detected. Please check the logs.")
            return False
    
    print("\n" + "=" * 50)
    print("🎉 YouCloudPay Chatbot is ready!")
    print("📱 Access at: http://localhost:5000")
    print("🔐 Admin Login: admin@youcloudpay.com / admin123")
    print("👤 Test User: john.doe@example.com / password123")
    print("=" * 50)
    
    # Start the application
    print("\n🌐 Starting Flask development server...")
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()
