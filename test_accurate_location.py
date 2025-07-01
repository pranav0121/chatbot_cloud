#!/usr/bin/env python3
"""
Test the improved location service for accurate country detection
"""

from location_service_v2 import location_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_accurate_location():
    """Test the location service for accurate detection"""
    logger.info("🌍 TESTING ACCURATE LOCATION DETECTION")
    logger.info("=" * 50)
    
    # Test 1: Get current actual location
    logger.info("1. Testing current location detection:")
    current_location = location_service.get_current_location()
    if current_location:
        logger.info(f"   ✅ Current Location Detected:")
        logger.info(f"      Country: {current_location['country']}")
        logger.info(f"      Country Code: {current_location['country_code']}")
        logger.info(f"      City: {current_location['city']}")
        logger.info(f"      Region: {current_location['region']}")
        logger.info(f"      Your Public IP: {current_location['ip']}")
        logger.info(f"      Source: {current_location['source']}")
        logger.info(f"      Timezone: {current_location['timezone']}")
    else:
        logger.error("   ❌ Failed to detect current location")
    
    # Test 2: Test with a known Indian IP
    logger.info("\n2. Testing with a known Indian IP:")
    indian_ip = "103.21.58.132"  # Known Indian IP
    indian_location = location_service.detect_country_by_ip(indian_ip)
    if indian_location:
        logger.info(f"   ✅ Indian IP Location:")
        logger.info(f"      IP: {indian_ip}")
        logger.info(f"      Country: {indian_location['country']}")
        logger.info(f"      City: {indian_location['city']}")
        logger.info(f"      Source: {indian_location['source']}")
    
    # Test 3: Test with Google DNS (should show US)
    logger.info("\n3. Testing with Google DNS (should show US):")
    google_dns = "8.8.8.8"
    google_location = location_service.detect_country_by_ip(google_dns)
    if google_location:
        logger.info(f"   ✅ Google DNS Location:")
        logger.info(f"      IP: {google_dns}")
        logger.info(f"      Country: {google_location['country']}")
        logger.info(f"      Source: {google_location['source']}")
    
    # Test 4: Test private IP handling
    logger.info("\n4. Testing private IP handling:")
    private_ip = "192.168.1.1"
    private_location = location_service.detect_country_by_ip(private_ip)
    if private_location:
        logger.info(f"   ✅ Private IP Handling:")
        logger.info(f"      IP: {private_ip}")
        logger.info(f"      Country: {private_location['country']}")
        logger.info(f"      Source: {private_location['source']}")
    
    logger.info("\n" + "=" * 50)
    logger.info("🎯 LOCATION DETECTION TEST COMPLETE")
    
    if current_location and current_location['country'] == 'India':
        logger.info("✅ SUCCESS: Correctly detected India as your location!")
    elif current_location:
        logger.info(f"ℹ️  Detected: {current_location['country']} (if this is correct, the service is working)")
    else:
        logger.error("❌ FAILED: Could not detect location")

if __name__ == "__main__":
    test_accurate_location()
