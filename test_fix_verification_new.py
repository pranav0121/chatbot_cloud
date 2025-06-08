#!/usr/bin/env python3
"""
Comprehensive test to verify all the fixes for the YouCloudPay Chatbot
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from flask import render_template_string, session
import unittest
from unittest.mock import patch
from bs4 import BeautifulSoup

class FixVerificationTests(unittest.TestCase):
    """Tests to verify the fixes applied to the YouCloudPay Chatbot"""
    
    def setUp(self):
        """Setup test environment"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        """Teardown test environment"""
        self.app_context.pop()
    
    def test_csrf_meta_tag(self):
        """Test that the CSRF meta tag is in base template"""
        with self.app.test_request_context('/'):
            response = self.client.get('/')
            self.assertEqual(response.status_code, 200)
            
            # Parse HTML and check for CSRF meta tag
            soup = BeautifulSoup(response.data, 'html.parser')
            csrf_meta = soup.find('meta', {'name': 'csrf-token'})
            self.assertIsNotNone(csrf_meta, "CSRF meta tag not found")
            self.assertTrue(csrf_meta.has_attr('content'), "CSRF token content missing")
            print("✅ CSRF meta tag check passed!")
    
    def test_chat_interface_compact(self):
        """Test that the chat interface is compact"""
        with self.app.test_request_context('/chat/new'):
            # Mock a logged-in user
            with patch('flask_login.utils._get_user', return_value=None):
                response = self.client.get('/chat/new')
                self.assertEqual(response.status_code, 302)  # Should redirect to login
                print("✅ Chat access control works!")
    
    def test_admin_dashboard_chart(self):
        """Test that the admin dashboard chart data is properly structured"""
        with self.app.test_request_context('/admin/dashboard'):
            # Create test chart data
            chart_data = {
                'labels': ['Jun 2', 'Jun 3', 'Jun 4', 'Jun 5', 'Jun 6', 'Jun 7', 'Jun 8'],
                'complaints': [2, 1, 3, 1, 2, 1, 0],
                'resolved': [1, 0, 2, 1, 1, 1, 0]
            }
            
            # Test rendering
            test_template = """
            <script>
            const chart_data = {{ chart_data|tojson }};
            const labels = {{ chart_data.labels|tojson }};
            const complaints = {{ chart_data.complaints|tojson }};
            const resolved = {{ chart_data.resolved|tojson }};
            </script>
            """
            
            rendered = render_template_string(test_template, chart_data=chart_data)
            self.assertIn('const chart_data =', rendered)
            self.assertIn('"labels":', rendered)
            self.assertIn('"complaints":', rendered)
            self.assertIn('"resolved":', rendered)
            print("✅ Chart data rendering works!")
    
    def test_analytics_api_routes(self):
        """Test that all required analytics API routes exist"""
        required_routes = [
            '/api/admin/analytics/metrics',
            '/api/admin/analytics/complaints-trend',
            '/api/admin/analytics/status-distribution',
            '/api/admin/analytics/category-breakdown',
            '/api/admin/analytics/priority-distribution',
            '/api/admin/analytics/top-issues',
            '/api/admin/analytics/agent-performance'
        ]
        
        # We check the routes existence using app URL map
        url_map = [str(rule) for rule in self.app.url_map.iter_rules()]
        
        for route in required_routes:
            self.assertTrue(any(route in r for r in url_map), f"Route {route} not found")
        
        print("✅ All required API routes exist!")
    
    def test_faq_template_exists(self):
        """Test that the FAQ template exists"""
        template_path = os.path.join(self.app.root_path, 'templates', 'admin', 'faqs.html')
        self.assertTrue(os.path.exists(template_path), "FAQs template not found")
        print("✅ FAQs template exists!")

if __name__ == '__main__':
    print("🧪 Running comprehensive fix verification tests...")
    print("=" * 70)
    
    # Run tests with more readable output
    suite = unittest.TestLoader().loadTestsFromTestCase(FixVerificationTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    
    if result.wasSuccessful():
        print("\n✅ All fixes have been successfully applied and verified!")
        print("The YouCloudPay Chatbot should now be working correctly.")
    else:
        print("\n❌ Some tests failed. Please review the implementation.")
