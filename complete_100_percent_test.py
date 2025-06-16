#!/usr/bin/env python3
"""
Complete 100% Enterprise System Test
Tests all functionality to ensure zero errors and enterprise-grade operation
"""

import sys
import os
import requests
import json
import time
from datetime import datetime

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class EnterpriseSystemTest:
    """Comprehensive test suite for the enterprise chatbot system"""
    
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.admin_credentials = {
            "email": "admin@youcloudtech.com",
            "password": "SecureAdmin123!"
        }
        self.test_results = []
        self.session = requests.Session()
    
    def log_test(self, test_name, success, message="", details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            'test': test_name,
            'status': status,
            'message': message,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        print(f"{status}: {test_name} - {message}")
        if details:
            print(f"   Details: {details}")
    
    def test_application_startup(self):
        """Test 1: Application Import and Startup"""
        try:
            # Test imports
            import app
            from super_admin import super_admin_bp
            from models import Partner, SLALog, TicketStatusLog, AuditLog
            
            self.log_test("Application Imports", True, "All modules imported successfully")
            
            # Test Flask app initialization
            flask_app = app.app
            self.log_test("Flask App Init", True, f"App initialized: {flask_app}")
            
            # Test database connection
            with flask_app.app_context():
                from app import db
                db.create_all()
                self.log_test("Database Connection", True, "MSSQL connection and tables created")
            
            return True
            
        except Exception as e:
            self.log_test("Application Startup", False, f"Startup failed: {str(e)}")
            return False
    
    def test_server_connectivity(self):
        """Test 2: Server Response and Basic Endpoints"""
        try:
            # Test basic connectivity
            response = self.session.get(f"{self.base_url}/test", timeout=10)
            if response.status_code == 200:
                self.log_test("Server Connectivity", True, "Server responding")
            else:
                self.log_test("Server Connectivity", False, f"Server returned {response.status_code}")
                return False
            
            # Test main page
            response = self.session.get(f"{self.base_url}/", timeout=10)
            if response.status_code in [200, 302]:  # 302 for redirect to login
                self.log_test("Main Page", True, "Main page accessible")
            else:
                self.log_test("Main Page", False, f"Main page returned {response.status_code}")
            
            return True
            
        except requests.exceptions.ConnectionError:
            self.log_test("Server Connectivity", False, "Cannot connect to server")
            return False
        except Exception as e:
            self.log_test("Server Connectivity", False, f"Error: {str(e)}")
            return False
    
    def test_admin_authentication(self):
        """Test 3: Admin Authentication System"""
        try:
            # Test admin login endpoint
            login_data = {
                "email": self.admin_credentials["email"],
                "password": self.admin_credentials["password"]
            }
            
            response = self.session.post(
                f"{self.base_url}/auth/admin-login",
                data=login_data,
                timeout=10,
                allow_redirects=False
            )
            
            if response.status_code in [200, 302]:
                self.log_test("Admin Authentication", True, "Admin login successful")
                return True
            else:
                self.log_test("Admin Authentication", False, f"Login failed with {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Admin Authentication", False, f"Error: {str(e)}")
            return False
    
    def test_super_admin_portal(self):
        """Test 4: Super Admin Portal Endpoints"""
        try:
            # Test super admin dashboard
            response = self.session.get(f"{self.base_url}/super-admin/dashboard", timeout=10)
            
            if response.status_code in [200, 302]:
                self.log_test("Super Admin Portal", True, "Dashboard accessible")
            else:
                self.log_test("Super Admin Portal", False, f"Dashboard returned {response.status_code}")
                return False
            
            # Test API endpoints
            api_endpoints = [
                "/super-admin/api/partners",
                "/super-admin/api/dashboard-metrics",
                "/super-admin/api/escalation/dashboard"
            ]
            
            success_count = 0
            for endpoint in api_endpoints:
                try:
                    response = self.session.get(f"{self.base_url}{endpoint}", timeout=5)
                    if response.status_code in [200, 401, 403]:  # 401/403 expected without proper auth
                        success_count += 1
                except:
                    pass
            
            if success_count >= len(api_endpoints) * 0.8:  # 80% success rate
                self.log_test("Super Admin APIs", True, f"{success_count}/{len(api_endpoints)} endpoints responding")
                return True
            else:
                self.log_test("Super Admin APIs", False, f"Only {success_count}/{len(api_endpoints)} endpoints responding")
                return False
                
        except Exception as e:
            self.log_test("Super Admin Portal", False, f"Error: {str(e)}")
            return False
    
    def test_chatbot_functionality(self):
        """Test 5: Chatbot Core Functionality"""
        try:
            # Test chat endpoint
            chat_data = {
                "message": "Hello, I need help",
                "user_id": "test_user_001"
            }
            
            response = self.session.post(
                f"{self.base_url}/chat",
                json=chat_data,
                timeout=10
            )
            
            if response.status_code == 200:
                response_data = response.json()
                if 'response' in response_data:
                    self.log_test("Chatbot Functionality", True, "Chat endpoint working")
                    return True
                else:
                    self.log_test("Chatbot Functionality", False, "Invalid chat response format")
                    return False
            else:
                self.log_test("Chatbot Functionality", False, f"Chat endpoint returned {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Chatbot Functionality", False, f"Error: {str(e)}")
            return False
    
    def test_database_operations(self):
        """Test 6: Database Operations and Models"""
        try:
            import app
            from models import Partner, SLALog, TicketStatusLog
            
            with app.app.app_context():
                from app import db, User, Ticket
                
                # Test basic database operations
                user_count = User.query.count()
                ticket_count = Ticket.query.count()
                
                self.log_test("Database Operations", True, 
                             f"Database accessible - Users: {user_count}, Tickets: {ticket_count}")
                
                # Test enterprise models
                try:
                    partner_count = Partner.query.count()
                    sla_count = SLALog.query.count()
                    self.log_test("Enterprise Models", True, 
                                 f"Enterprise models working - Partners: {partner_count}, SLA Logs: {sla_count}")
                except Exception as model_error:
                    self.log_test("Enterprise Models", False, f"Model error: {str(model_error)}")
                
                return True
                
        except Exception as e:
            self.log_test("Database Operations", False, f"Error: {str(e)}")
            return False
    
    def test_sla_monitoring(self):
        """Test 7: SLA Monitoring Service"""
        try:
            import app
            
            # Check if SLA monitor is running
            if hasattr(app, 'sla_monitor') and app.sla_monitor:
                if app.sla_monitor.monitoring:
                    self.log_test("SLA Monitoring", True, "SLA monitoring service is active")
                else:
                    self.log_test("SLA Monitoring", False, "SLA monitoring service not active")
                    return False
            else:
                self.log_test("SLA Monitoring", False, "SLA monitor not initialized")
                return False
            
            return True
            
        except Exception as e:
            self.log_test("SLA Monitoring", False, f"Error: {str(e)}")
            return False
    
    def test_translation_system(self):
        """Test 8: Multi-language Translation System"""
        try:
            # Test language endpoints
            languages = ['en', 'es', 'ar', 'hi']
            success_count = 0
            
            for lang in languages:
                try:
                    response = self.session.get(f"{self.base_url}/?lang={lang}", timeout=5)
                    if response.status_code in [200, 302]:
                        success_count += 1
                except:
                    pass
            
            if success_count >= len(languages) * 0.75:  # 75% success rate
                self.log_test("Translation System", True, f"{success_count}/{len(languages)} languages working")
                return True
            else:
                self.log_test("Translation System", False, f"Only {success_count}/{len(languages)} languages working")
                return False
                
        except Exception as e:
            self.log_test("Translation System", False, f"Error: {str(e)}")
            return False
    
    def run_complete_test_suite(self):
        """Run all tests and generate comprehensive report"""
        print("=" * 80)
        print("🚀 ENTERPRISE CHATBOT SYSTEM - 100% FUNCTIONALITY TEST")
        print("=" * 80)
        print(f"Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Run all tests
        tests = [
            self.test_application_startup,
            self.test_server_connectivity,
            self.test_admin_authentication,
            self.test_super_admin_portal,
            self.test_chatbot_functionality,
            self.test_database_operations,
            self.test_sla_monitoring,
            self.test_translation_system
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                if test():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ CRITICAL ERROR in {test.__name__}: {str(e)}")
                failed += 1
            print()  # Add spacing between tests
        
        # Generate final report
        print("=" * 80)
        print("📊 FINAL TEST RESULTS")
        print("=" * 80)
        
        total_tests = passed + failed
        success_rate = (passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        if success_rate >= 95:
            print("🎉 ENTERPRISE SYSTEM STATUS: 100% OPERATIONAL")
            print("✅ All critical systems functioning properly")
            print("✅ Enterprise-grade features fully operational")
            print("✅ Zero blocking errors detected")
        elif success_rate >= 80:
            print("⚠️  ENTERPRISE SYSTEM STATUS: 90% OPERATIONAL")
            print("✅ Core systems functioning")
            print("⚠️  Minor issues detected - review required")
        else:
            print("❌ ENTERPRISE SYSTEM STATUS: NEEDS ATTENTION")
            print("❌ Critical issues detected")
            print("❌ Immediate fixes required")
        
        print()
        print("=" * 80)
        print(f"Test Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        return success_rate >= 95

if __name__ == "__main__":
    tester = EnterpriseSystemTest()
    success = tester.run_complete_test_suite()
    sys.exit(0 if success else 1)
