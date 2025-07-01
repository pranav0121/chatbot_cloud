#!/usr/bin/env python3
"""
Quick Device Test via curl-like request
"""

import urllib.request
import json

def test_endpoint():
    url = "http://127.0.0.1:5000/test-device-tracking"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            data = response.read().decode()
            print(f"Status: {response.status}")
            print(f"Response: {data}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_endpoint()
