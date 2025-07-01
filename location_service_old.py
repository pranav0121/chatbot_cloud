#!/usr/bin/env python3
"""
Location Detection Service for Country Information
- Detects user's country based on IP address
- Provides fallback mechanisms for country detection
- Does NOT modify existing working code
"""

import requests
import logging
from flask import request
import json

logger = logging.getLogger(__name__)

class LocationService:
    """Service for detecting user location/country"""
    
    def __init__(self):
        self.fallback_country = "Unknown"
        self.ip_apis = [
            {
                'name': 'ipapi.co',
                'url': 'https://ipapi.co/{ip}/json/',
                'country_field': 'country_name'
            },
            {
                'name': 'ip-api.com', 
                'url': 'http://ip-api.com/json/{ip}',
                'country_field': 'country'
            }
        ]
    
    def get_client_ip(self):
        """Get client IP address from request"""
        try:
            # Check for forwarded IP first (for proxy/load balancer)
            if request.headers.get('X-Forwarded-For'):
                ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
            elif request.headers.get('X-Real-IP'):
                ip = request.headers.get('X-Real-IP')
            else:
                ip = request.remote_addr
            
            logger.info(f"Detected client IP: {ip}")
            return ip
        except Exception as e:
            logger.error(f"Error getting client IP: {e}")
            return None
    
    def detect_country_by_ip(self, ip_address=None):
        """Detect country based on IP address"""
        if not ip_address:
            ip_address = self.get_client_ip()
        
        if not ip_address or ip_address in ['127.0.0.1', 'localhost', '::1']:
            logger.info("Local IP detected, returning default country")
            return "Local/Unknown"
        
        for api in self.ip_apis:
            try:
                logger.info(f"Trying {api['name']} for IP geolocation...")
                url = api['url'].format(ip=ip_address)
                
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    country = data.get(api['country_field'])
                    
                    if country and country != 'Unknown':
                        logger.info(f"✅ Country detected via {api['name']}: {country}")
                        return country
                    
            except Exception as e:
                logger.warning(f"Failed to get location from {api['name']}: {e}")
                continue
        
        logger.warning("Could not detect country from any API")
        return self.fallback_country
    
    def get_country_list(self):
        """Get list of countries for dropdown selection"""
        countries = [
            "Afghanistan", "Albania", "Algeria", "Argentina", "Armenia", "Australia",
            "Austria", "Azerbaijan", "Bahrain", "Bangladesh", "Belarus", "Belgium", 
            "Bolivia", "Bosnia and Herzegovina", "Brazil", "Bulgaria", "Cambodia",
            "Canada", "Chile", "China", "Colombia", "Croatia", "Czech Republic",
            "Denmark", "Ecuador", "Egypt", "Estonia", "Finland", "France", "Georgia",
            "Germany", "Ghana", "Greece", "Hungary", "Iceland", "India", "Indonesia",
            "Iran", "Iraq", "Ireland", "Israel", "Italy", "Japan", "Jordan", "Kazakhstan",
            "Kenya", "South Korea", "Kuwait", "Latvia", "Lebanon", "Lithuania", "Luxembourg",
            "Malaysia", "Mexico", "Morocco", "Netherlands", "New Zealand", "Nigeria",
            "Norway", "Pakistan", "Peru", "Philippines", "Poland", "Portugal", "Qatar",
            "Romania", "Russia", "Saudi Arabia", "Singapore", "Slovakia", "Slovenia",
            "South Africa", "Spain", "Sri Lanka", "Sweden", "Switzerland", "Thailand",
            "Turkey", "Ukraine", "United Arab Emirates", "United Kingdom", "United States",
            "Uruguay", "Venezuela", "Vietnam", "Other"
        ]
        return sorted(countries)
    
    def get_country_with_detection(self, provided_country=None):
        """Get country with automatic detection as fallback"""
        if provided_country and provided_country != "Unknown":
            logger.info(f"Using provided country: {provided_country}")
            return provided_country
        
        # Auto-detect if not provided
        detected_country = self.detect_country_by_ip()
        logger.info(f"Auto-detected country: {detected_country}")
        return detected_country

# Global instance
location_service = LocationService()

# Helper functions for easy import
def detect_user_country(provided_country=None):
    """Detect or use provided country"""
    return location_service.get_country_with_detection(provided_country)

def get_client_country():
    """Get country from client IP"""
    return location_service.detect_country_by_ip()

def get_countries_list():
    """Get list of countries for UI"""
    return location_service.get_country_list()

if __name__ == "__main__":
    # Test the location service
    print("🌍 Testing Location Detection Service")
    print("=" * 40)
    
    service = LocationService()
    
    # Test country list
    countries = service.get_country_list()
    print(f"📋 Available countries: {len(countries)}")
    print(f"First 10: {countries[:10]}")
    
    # Test IP detection (this will fail without Flask context)
    print("\n🔍 IP Detection Test:")
    test_ip = "8.8.8.8"  # Google DNS
    country = service.detect_country_by_ip(test_ip)
    print(f"Country for {test_ip}: {country}")
    
    print("\n✅ Location Service Test Complete!")
