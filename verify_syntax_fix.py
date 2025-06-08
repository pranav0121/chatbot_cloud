#!/usr/bin/env python3
"""
Quick Verification Script - Test that syntax errors are fixed and app works
"""

import sys
import traceback

def test_imports():
    """Test that all imports work correctly"""
    try:
        print("Testing imports...")
        import app
        print("✅ Flask app imports successfully")
        return True
    except Exception as e:
        print(f"❌ Import error: {str(e)}")
        traceback.print_exc()
        return False

def test_database_models():
    """Test that database models are defined correctly"""
    try:
        print("Testing database models...")
        import app
        
        # Test that all models exist
        models = ['User', 'Category', 'Ticket', 'Message', 'CommonQuery', 'Feedback', 'Attachment']
        for model_name in models:
            model = getattr(app, model_name, None)
            if model:
                print(f"✅ {model_name} model defined")
            else:
                print(f"❌ {model_name} model missing")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Model error: {str(e)}")
        traceback.print_exc()
        return False

def test_basic_functionality():
    """Test basic app functionality"""
    try:
        print("Testing basic functionality...")
        import requests
        
        # Test home page
        response = requests.get('http://localhost:5000/', timeout=5)
        if response.status_code == 200:
            print("✅ Home page accessible")
        else:
            print(f"❌ Home page error: {response.status_code}")
            return False
            
        # Test health endpoint
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint error: {response.status_code}")
            return False
            
        return True
    except Exception as e:
        print(f"❌ Functionality test error: {str(e)}")
        return False

def main():
    """Run all verification tests"""
    print("🔍 Running Quick Verification Tests...\n")
    
    tests = [
        ("Import Test", test_imports),
        ("Database Models Test", test_database_models),
        ("Basic Functionality Test", test_basic_functionality)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 40)
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The syntax errors are fixed and the app is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
