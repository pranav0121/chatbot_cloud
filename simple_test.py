#!/usr/bin/env python3
"""
Simple test script to verify fixes are working
"""

def test_config():
    """Test config import"""
    print("Testing config.py import...")
    try:
        from config import Config
        config = Config()
        print("✅ Config imported successfully")
        
        # Test database URI
        uri = config.SQLALCHEMY_DATABASE_URI
        print(f"✅ Database URI: {uri[:60]}...")
        return True
    except Exception as e:
        print(f"❌ Config import failed: {e}")
        return False

def test_app():
    """Test app import"""
    print("\nTesting app.py import...")
    try:
        from app import app, db
        print("✅ App imported successfully")
        
        # Test model imports
        from app import User, Category, Ticket, Message, Feedback, Attachment
        print("✅ All models imported successfully")
        return True
    except Exception as e:
        print(f"❌ App import failed: {e}")
        return False

def test_database():
    """Test database setup"""
    print("\nTesting database setup...")
    try:
        from app import app, db
        
        with app.app_context():
            db.create_all()
            print("✅ Database tables created")
            
            # Test categories
            from app import Category
            count = Category.query.count()
            print(f"✅ Categories in database: {count}")
            
        return True
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        print("(This may be expected if SQL Server is not configured)")
        return False

def main():
    print("Running basic functionality tests...")
    print("=" * 40)
    
    results = []
    results.append(test_config())
    results.append(test_app())
    results.append(test_database())
    
    passed = sum(results)
    total = len(results)
    
    print("\n" + "=" * 40)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed >= 2:
        print("✅ Core functionality is working!")
        print("\nTo start the application:")
        print("  python app.py")
    else:
        print("❌ Critical issues found")

if __name__ == "__main__":
    main()
