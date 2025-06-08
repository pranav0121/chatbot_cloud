#!/usr/bin/env python3
"""
Final verification of all fixes for the YouCloudPay Chatbot
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
import unittest

class FinalVerificationTests(unittest.TestCase):
    """Simple tests to verify the major fixes"""
    
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        self.app_context.pop()
    
    def test_all_templates_exist(self):
        """Test that all required templates exist"""
        # Check CSRF meta tag in base template
        with open(os.path.join(self.app.root_path, 'templates', 'base.html'), 'r') as f:
            base_content = f.read()
            self.assertIn('<meta name="csrf-token"', base_content)
            print("✅ CSRF meta tag exists in base.html")
        
        # Check FAQ template exists  
        faq_path = os.path.join(self.app.root_path, 'templates', 'admin', 'faqs.html')
        self.assertTrue(os.path.exists(faq_path), "FAQs template not found")
        print("✅ FAQs template exists")
        
        # Check chat conversation template has correct compact styling
        with open(os.path.join(self.app.root_path, 'templates', 'chat', 'conversation.html'), 'r') as f:
            chat_content = f.read()
            self.assertIn('space-y-2', chat_content)  # Reduced spacing
            self.assertIn('p-2', chat_content)  # Reduced padding
            self.assertIn('min-height: 36px', chat_content)  # Smaller input
            print("✅ Chat interface has compact styling")
    
    def test_api_routes_exist(self):
        """Test that all required API routes exist"""
        # Check the URL map for required routes
        url_map = [str(rule) for rule in self.app.url_map.iter_rules()]
        required_routes = [
            '/api/admin/analytics/metrics',
            '/api/admin/analytics/complaints-trend', 
            '/api/admin/analytics/status-distribution',
            '/api/admin/analytics/category-breakdown',
            '/api/admin/analytics/priority-distribution',
            '/api/admin/analytics/top-issues',
            '/api/admin/analytics/agent-performance'
        ]
        
        for route in required_routes:
            self.assertTrue(any(route in r for r in url_map), f"Route {route} not found")
        
        print("✅ All required API routes exist")

if __name__ == '__main__':
    print("🧪 Running final verification tests...")
    print("=" * 70)
    
    unittest.main(verbosity=2)
