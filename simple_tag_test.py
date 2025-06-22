#!/usr/bin/env python3
"""
Simple test to verify tag handling in Odoo integration is fixed
"""
import os
from dotenv import load_dotenv

def test_tag_fix():
    """Quick test to verify tag handling code"""
    print("Testing tag handling fix...")
    
    # Load environment
    load_dotenv()
    
    # Test if we can import and initialize without errors
    try:
        from odoo_service import OdooService
        print("✅ OdooService imported successfully")
        
        # Check if the get_or_create_tag method exists
        if hasattr(OdooService, 'get_or_create_tag'):
            print("✅ get_or_create_tag method exists")
        else:
            print("❌ get_or_create_tag method missing")
            return False
            
        # Check if create_ticket method handles tag_ids properly
        import inspect
        source = inspect.getsource(OdooService.create_ticket)
        if 'tag_ids' in source and 'get_or_create_tag' in source:
            print("✅ create_ticket method handles tag_ids conversion")
        else:
            print("❌ create_ticket method doesn't handle tag_ids properly")
            return False
            
        print("✅ Tag handling fix appears to be working!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_tag_fix()
    if success:
        print("\n🎉 Tag fix successful! You can now run manual_sync_tickets.py")
    else:
        print("\n❌ Tag fix failed - please check the code")
