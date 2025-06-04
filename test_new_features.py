#!/usr/bin/env python3
"""
Test Script for New Features
Tests the FAQ page and file upload functionality
"""

import requests
import os
import json
from PIL import Image
import io

def test_faq_page():
    """Test that the FAQ page loads correctly"""
    try:
        print("🧪 Testing FAQ page...")
        response = requests.get('http://localhost:5000/faq')
        
        if response.status_code == 200:
            print("✅ FAQ page loads successfully")
            if 'FAQ' in response.text and 'frequently asked questions' in response.text.lower():
                print("✅ FAQ page contains expected content")
                return True
            else:
                print("❌ FAQ page missing expected content")
                return False
        else:
            print(f"❌ FAQ page failed to load. Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing FAQ page: {e}")
        return False

def test_file_upload_api():
    """Test file upload API endpoint"""
    try:
        print("🧪 Testing file upload API...")
        
        # Create a simple test image
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        # Test the upload endpoint
        files = {'file': ('test_image.png', img_bytes, 'image/png')}
        response = requests.post('http://localhost:5000/api/upload', files=files)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                print("✅ File upload API works correctly")
                file_info = result.get('file_info', {})
                print(f"   📁 Original name: {file_info.get('original_name')}")
                print(f"   💾 Stored name: {file_info.get('stored_name')}")
                print(f"   📏 File size: {file_info.get('file_size')} bytes")
                return True
            else:
                print(f"❌ File upload failed: {result}")
                return False
        else:
            print(f"❌ File upload API failed. Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing file upload: {e}")
        return False

def test_categories_api():
    """Test that categories API still works"""
    try:
        print("🧪 Testing categories API...")
        response = requests.get('http://localhost:5000/api/categories')
        
        if response.status_code == 200:
            categories = response.json()
            if isinstance(categories, list) and len(categories) > 0:
                print(f"✅ Categories API works. Found {len(categories)} categories")
                for cat in categories:
                    print(f"   📂 {cat.get('name', 'Unknown')}")
                return True
            else:
                print("❌ Categories API returned empty or invalid data")
                return False
        else:
            print(f"❌ Categories API failed. Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing categories API: {e}")
        return False

def test_main_page():
    """Test that main page loads with file upload UI"""
    try:
        print("🧪 Testing main page with file upload UI...")
        response = requests.get('http://localhost:5000/')
        
        if response.status_code == 200:
            content = response.text
            
            # Check for file upload elements
            upload_elements = [
                'file-upload-area',
                'file-input',
                'file-preview',
                'attach-btn',
                'drag and drop'
            ]
            
            found_elements = []
            for element in upload_elements:
                if element in content.lower():
                    found_elements.append(element)
            
            print(f"✅ Main page loads successfully")
            print(f"✅ Found {len(found_elements)}/{len(upload_elements)} file upload elements")
            
            # Check for FAQ link
            if 'faq' in content.lower():
                print("✅ FAQ link found on main page")
            else:
                print("❌ FAQ link not found on main page")
            
            return len(found_elements) >= 3  # At least 3 upload elements should be present
        else:
            print(f"❌ Main page failed to load. Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing main page: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting New Features Test Suite")
    print("=" * 50)
    
    tests = [
        ("Main Page with File Upload UI", test_main_page),
        ("FAQ Page", test_faq_page),
        ("Categories API", test_categories_api),
        ("File Upload API", test_file_upload_api),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"✅ PASSED: {test_name}")
            else:
                failed += 1
                print(f"❌ FAILED: {test_name}")
        except Exception as e:
            failed += 1
            print(f"💥 ERROR in {test_name}: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results:")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 All tests passed! The new features are working correctly.")
        print("✨ FAQ page and file upload functionality are fully operational.")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please check the errors above.")
    
    return failed == 0

if __name__ == '__main__':
    main()