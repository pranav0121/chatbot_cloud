import requests
from bs4 import BeautifulSoup

def test_quick_verification():
    """Quick verification of the main issues"""
    print("🔍 Quick Feature Verification")
    print("=" * 40)
    
    try:
        # Test main page
        response = requests.get('http://localhost:5000/')
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check for file upload elements
            file_upload_areas = soup.find_all('div', class_='file-upload-area')
            file_inputs = soup.find_all('input', {'type': 'file'})
            attach_btn = soup.find('button', {'id': 'attach-btn'})
            faq_link = soup.find('a', string=lambda text: text and 'FAQ' in text)
            
            print(f"✅ Main page loads: YES")
            print(f"📁 File upload areas found: {len(file_upload_areas)}")
            print(f"📄 File inputs found: {len(file_inputs)}")
            print(f"📎 Attach button found: {'YES' if attach_btn else 'NO'}")
            print(f"❓ FAQ link found: {'YES' if faq_link else 'NO'}")
            
            if len(file_upload_areas) >= 2 and len(file_inputs) >= 2 and attach_btn and faq_link:
                print("🎉 MAIN PAGE: ALL ELEMENTS FOUND!")
            else:
                print("❌ MAIN PAGE: Missing elements")
        else:
            print(f"❌ Main page failed to load: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Error testing main page: {e}")
    
    try:
        # Test FAQ page
        response = requests.get('http://localhost:5000/faq')
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check for FAQ content
            faq_title = soup.find('h1', string=lambda text: text and 'FAQ' in text)
            faq_categories = soup.find_all('div', class_='faq-category')
            search_box = soup.find('input', {'id': 'faqSearch'})
            
            print(f"\n✅ FAQ page loads: YES")
            print(f"📋 FAQ title found: {'YES' if faq_title else 'NO'}")
            print(f"📂 FAQ categories found: {len(faq_categories)}")
            print(f"🔍 Search box found: {'YES' if search_box else 'NO'}")
            
            if faq_title and len(faq_categories) >= 3 and search_box:
                print("🎉 FAQ PAGE: ALL ELEMENTS FOUND!")
            else:
                print("❌ FAQ PAGE: Missing elements")
        else:
            print(f"❌ FAQ page failed to load: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Error testing FAQ page: {e}")

if __name__ == "__main__":
    test_quick_verification()
