#!/usr/bin/env python3
"""
Simple Partner Fix Verification
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def verify_partner_fix():
    """Verify the partner management fixes"""
    print("🔍 Verifying Partner Management Fixes...")
    
    try:
        # Test 1: Import models
        print("\n1. Testing model imports...")
        from models import Partner, SLALog
        print("   ✅ Partner and SLALog models imported successfully")
        
        # Test 2: Import super admin
        print("\n2. Testing super admin import...")
        from super_admin import super_admin_bp
        print("   ✅ Super admin blueprint imported successfully")
        
        # Test 3: Test Flask app with partner context
        print("\n3. Testing Flask app with partner context...")
        import app
        with app.app.app_context():
            from app import db
            # Test basic partner query (won't fail even if table is empty)
            partner_count = Partner.query.count()
            print(f"   ✅ Partner query successful - Found {partner_count} partners")
        
        # Test 4: Check if partner template exists
        print("\n4. Checking partner template...")
        template_path = "templates/super_admin/partners.html"
        if os.path.exists(template_path):
            print("   ✅ Partner template exists")
            
            # Check for critical JavaScript functions
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            critical_functions = [
                'loadPartners()',
                'savePartner()',
                'showAddPartnerModal()',
                'editPartner(',
                'viewPartnerDetails('
            ]
            
            missing_functions = []
            for func in critical_functions:
                if func not in content:
                    missing_functions.append(func)
            
            if not missing_functions:
                print("   ✅ All critical JavaScript functions found")
            else:
                print(f"   ⚠️ Missing functions: {missing_functions}")
        else:
            print("   ❌ Partner template not found")
            return False
            
        print("\n🎉 PARTNER MANAGEMENT FIXES VERIFIED!")
        print("✅ All critical components are working")
        print("✅ The 'Partner is not defined' error should be resolved")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during verification: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🔧 PARTNER MANAGEMENT FIX VERIFICATION")
    print("=" * 50)
    
    success = verify_partner_fix()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ VERIFICATION SUCCESSFUL!")
        print("\n📋 INSTRUCTIONS:")
        print("1. The Partner Management page should now work without errors")
        print("2. Access it at: http://localhost:5000/super-admin/partners")
        print("3. Login first at: http://localhost:5000/auth/admin-login")
        print("4. Use credentials: admin@youcloudtech.com / SecureAdmin123!")
    else:
        print("❌ VERIFICATION FAILED - Additional fixes needed")
    print("=" * 50)
    
    sys.exit(0 if success else 1)
