#!/usr/bin/env python3
"""
Debug login process to see what's happening
"""

import requests
import json
import sys
from bs4 import BeautifulSoup

def debug_login():
    base_url = "http://127.0.0.1:5000"
    
    print("=== DEBUGGING LOGIN PROCESS ===")
    
    session = requests.Session()
    
    # Get login page first
    print("\n1. Getting login page...")
    login_page = session.get(f"{base_url}/auth/admin/login")
    print(f"Login page status: {login_page.status_code}")
    
    if 'form' in login_page.text.lower():
        print("Found login form on page")
    else:
        print("No login form found")
    
    # Check for any error messages or specific form fields
    soup = BeautifulSoup(login_page.text, 'html.parser')
    forms = soup.find_all('form')
    print(f"Found {len(forms)} forms on page")
    
    for i, form in enumerate(forms):
        print(f"Form {i+1}:")
        inputs = form.find_all('input')
        for inp in inputs:
            print(f"  Input: name='{inp.get('name')}', type='{inp.get('type')}'")
    
    # Try login with various credential combinations
    print("\n2. Testing login with various credentials...")
    
    credentials_to_try = [
        {'email': 'superadmin@youcloudpay.com', 'password': 'SuperSecure2024!'},
        {'email': 'admin@youcloudtech.com', 'password': 'AdminYCT2024!'},
        {'username': 'superadmin@youcloudpay.com', 'password': 'SuperSecure2024!'},
        {'email': 'superadmin@youcloudpay.com', 'password': 'SuperSecure2024!', 'login': '1'},
    ]
    
    for i, creds in enumerate(credentials_to_try):
        print(f"\nTrying credentials set {i+1}: {creds}")
        login_response = session.post(f"{base_url}/auth/admin/login", data=creds, allow_redirects=False)
        print(f"Response status: {login_response.status_code}")
        print(f"Response headers: {dict(login_response.headers)}")
        
        if login_response.status_code == 302:
            print(f"Redirect to: {login_response.headers.get('Location')}")
            # Follow redirect
            redirect_response = session.get(login_response.headers.get('Location'))
            print(f"Redirect response status: {redirect_response.status_code}")
            print(f"Final URL: {redirect_response.url}")
            
            # Test if we can access super admin API now
            api_test = session.get(f"{base_url}/super-admin/api/dashboard-metrics")
            print(f"API test status: {api_test.status_code}")
            
            if api_test.status_code == 200:
                print("SUCCESS! Login worked with these credentials")
                return session, creds
            else:
                print("Login redirect worked but API access still denied")
        else:
            # Check response content for error messages
            if 'error' in login_response.text.lower() or 'invalid' in login_response.text.lower():
                print("Login failed - error detected in response")
            else:
                print("Login status unclear")
            
            # Show a snippet of the response
            print(f"Response snippet: {login_response.text[:300]}")
    
    print("\nAll login attempts failed")
    return None, None

if __name__ == "__main__":
    debug_login()
