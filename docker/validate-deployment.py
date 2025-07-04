#!/usr/bin/env python3
"""
Deployment Validation Script for Chatbot Application
Run this after deployment to verify everything is working correctly.
"""

import requests
import os
import sys
import time
from typing import Dict, List, Tuple

class DeploymentValidator:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.results: List[Tuple[str, bool, str]] = []
    
    def log_result(self, test_name: str, success: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.results.append((test_name, success, message))
        print(f"{status} {test_name}: {message}")
    
    def test_database_connection(self) -> bool:
        """Test database connectivity"""
        try:
            response = requests.get(f"{self.base_url}/api/database/test", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    self.log_result("Database Connection", True, "Connected successfully")
                    return True
                else:
                    self.log_result("Database Connection", False, f"Database error: {data.get('message')}")
                    return False
            else:
                self.log_result("Database Connection", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Database Connection", False, f"Connection failed: {str(e)}")
            return False
    
    def test_application_health(self) -> bool:
        """Test application health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            if response.status_code == 200:
                self.log_result("Application Health", True, "Application responding")
                return True
            else:
                self.log_result("Application Health", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Application Health", False, f"Health check failed: {str(e)}")
            return False
    
    def test_admin_panel(self) -> bool:
        """Test admin panel accessibility"""
        try:
            response = requests.get(f"{self.base_url}/admin", timeout=10)
            if response.status_code in [200, 302]:  # 302 is redirect to login
                self.log_result("Admin Panel", True, "Admin panel accessible")
                return True
            else:
                self.log_result("Admin Panel", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Admin Panel", False, f"Admin panel failed: {str(e)}")
            return False
    
    def test_api_endpoints(self) -> bool:
        """Test core API endpoints"""
        endpoints = [
            "/api/tickets",
            "/api/users", 
            "/api/escalations",
            "/api/faq"
        ]
        
        all_passed = True
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                if response.status_code in [200, 401]:  # 401 is expected for protected endpoints
                    self.log_result(f"API {endpoint}", True, "Endpoint responding")
                else:
                    self.log_result(f"API {endpoint}", False, f"HTTP {response.status_code}")
                    all_passed = False
            except Exception as e:
                self.log_result(f"API {endpoint}", False, f"Failed: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_static_files(self) -> bool:
        """Test static file serving"""
        try:
            response = requests.get(f"{self.base_url}/static/css/style.css", timeout=10)
            if response.status_code == 200:
                self.log_result("Static Files", True, "CSS files loading")
                return True
            else:
                self.log_result("Static Files", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Static Files", False, f"Static files failed: {str(e)}")
            return False
    
    def test_translations(self) -> bool:
        """Test translation files"""
        try:
            response = requests.get(f"{self.base_url}/api/chat/languages", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and len(data) > 0:
                    languages = list(data.keys())
                    self.log_result("Translations", True, f"Languages available: {', '.join(languages)}")
                    return True
                else:
                    self.log_result("Translations", False, "No languages found")
                    return False
            else:
                self.log_result("Translations", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Translations", False, f"Translation test failed: {str(e)}")
            return False
    
    def run_all_tests(self) -> Dict[str, any]:
        """Run all validation tests"""
        print("🔍 Starting Deployment Validation...\n")
        
        # Wait for application to start
        print("⏳ Waiting for application to start...")
        time.sleep(5)
        
        tests = [
            ("Application Health", self.test_application_health),
            ("Database Connection", self.test_database_connection), 
            ("Admin Panel", self.test_admin_panel),
            ("API Endpoints", self.test_api_endpoints),
            ("Static Files", self.test_static_files),
            ("Translations", self.test_translations)
        ]
        
        print("\n📊 Running Tests...\n")
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            if test_func():
                passed += 1
        
        success_rate = (passed / total) * 100
        
        print(f"\n📈 Results Summary:")
        print(f"Passed: {passed}/{total} ({success_rate:.1f}%)")
        
        if success_rate >= 85:
            print("🎉 Deployment Successful!")
            deployment_status = "SUCCESS"
        elif success_rate >= 70:
            print("⚠️  Deployment Partially Working (some issues)")
            deployment_status = "PARTIAL"
        else:
            print("❌ Deployment Failed (major issues)")
            deployment_status = "FAILED"
        
        return {
            "status": deployment_status,
            "success_rate": success_rate,
            "passed": passed,
            "total": total,
            "results": self.results
        }

def main():
    """Main validation function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate chatbot deployment")
    parser.add_argument("--url", default="http://localhost:5000", 
                       help="Application URL (default: http://localhost:5000)")
    
    args = parser.parse_args()
    
    validator = DeploymentValidator(args.url)
    results = validator.run_all_tests()
    
    if results["status"] == "FAILED":
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
