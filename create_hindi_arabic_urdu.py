#!/usr/bin/env python3
"""
Create translation files for Hindi, Arabic, and Urdu
"""
import os
from babel.messages import Catalog
from babel.messages.pofile import write_po
from babel.messages.mofile import write_mo

# Translations for Hindi, Arabic, and Urdu
LANGUAGES = {
    'hi': {  # Hindi
        'name': 'हिन्दी',
        'translations': {
            'Support Center - We\'re Here to Help': 'सहायता केंद्र - हम यहाँ मदद के लिए हैं',
            'We\'re Here to Help': 'हम यहाँ मदद के लिए हैं',
            'Get instant support for all your questions. Our AI-powered chatbot and live support team are ready to assist you 24/7.': 'अपने सभी प्रश्नों के लिए तुरंत सहायता प्राप्त करें। हमारा AI-संचालित चैटबॉट और लाइव सपोर्ट टीम 24/7 आपकी सहायता के लिए तैयार है।',
            'Instant Response': 'तुरंत उत्तर',
            'Expert Support': 'विशेषज्ञ सहायता',
            '24/7 Available': '24/7 उपलब्ध',
            'Start Support Chat': 'सहायता चैट शुरू करें',
            'View FAQ': 'FAQ देखें',
            'Quick Help Categories': 'त्वरित सहायता श्रेणियां',
            'Choose a category to get started or describe your issue': 'शुरू करने के लिए एक श्रेणी चुनें या अपनी समस्या का वर्णन करें',
            'Support Chat': 'सहायता चैट',
            'Online': 'ऑनलाइन',
            'Hi there! 👋': 'नमस्ते! 👋',
            'How can we help you today?': 'आज हम आपकी कैसे मदद कर सकते हैं?',
            'Please select a category:': 'कृपया एक श्रेणी चुनें:',
            'Language selection': 'भाषा चयन',
            'Choose Language': 'भाषा चुनें',
            'Common Issues': 'सामान्य समस्याएं',
            'Does any of these match your issue?': 'क्या इनमें से कोई आपकी समस्या से मेल खाता है?',
            'Can\'t find your issue?': 'अपनी समस्या नहीं मिल रही?',
            'Describe Your Issue': 'अपनी समस्या का वर्णन करें',
            'Your Name (Optional)': 'आपका नाम (वैकल्पिक)',
            'Email (Optional)': 'ईमेल (वैकल्पिक)',
            'Enter your name': 'अपना नाम दर्ज करें',
            'Enter your email': 'अपना ईमेल दर्ज करें',
            'Type your question here...': 'यहाँ अपना प्रश्न टाइप करें...',
            'Connected with support': 'सहायता से जुड़े हुए',
            'Ticket': 'टिकट',
            'Close': 'बंद करें',
            'Submit': 'जमा करें',
            'Back': 'वापस'
        }
    },
    'ar': {  # Arabic
        'name': 'العربية',
        'translations': {
            'Support Center - We\'re Here to Help': 'مركز الدعم - نحن هنا للمساعدة',
            'We\'re Here to Help': 'نحن هنا للمساعدة',
            'Get instant support for all your questions. Our AI-powered chatbot and live support team are ready to assist you 24/7.': 'احصل على دعم فوري لجميع أسئلتك. روبوت الدردشة المدعوم بالذكاء الاصطناعي وفريق الدعم المباشر جاهزون لمساعدتك على مدار الساعة.',
            'Instant Response': 'استجابة فورية',
            'Expert Support': 'دعم خبير',
            '24/7 Available': 'متاح 24/7',
            'Start Support Chat': 'بدء دردشة الدعم',
            'View FAQ': 'عرض الأسئلة الشائعة',
            'Quick Help Categories': 'فئات المساعدة السريعة',
            'Choose a category to get started or describe your issue': 'اختر فئة للبدء أو وصف مشكلتك',
            'Support Chat': 'دردشة الدعم',
            'Online': 'متصل',
            'Hi there! 👋': 'مرحباً! 👋',
            'How can we help you today?': 'كيف يمكننا مساعدتك اليوم؟',
            'Please select a category:': 'يرجى اختيار فئة:',
            'Language selection': 'اختيار اللغة',
            'Choose Language': 'اختر اللغة',
            'Common Issues': 'المشاكل الشائعة',
            'Does any of these match your issue?': 'هل تتطابق أي من هذه مع مشكلتك؟',
            'Can\'t find your issue?': 'لا يمكنك العثور على مشكلتك؟',
            'Describe Your Issue': 'صف مشكلتك',
            'Your Name (Optional)': 'اسمك (اختياري)',
            'Email (Optional)': 'البريد الإلكتروني (اختياري)',
            'Enter your name': 'أدخل اسمك',
            'Enter your email': 'أدخل بريدك الإلكتروني',
            'Type your question here...': 'اكتب سؤالك هنا...',
            'Connected with support': 'متصل بالدعم',
            'Ticket': 'تذكرة',
            'Close': 'إغلاق',
            'Submit': 'إرسال',
            'Back': 'رجوع'
        }
    },
    'ur': {  # Urdu
        'name': 'اردو',
        'translations': {
            'Support Center - We\'re Here to Help': 'سپورٹ سینٹر - ہم یہاں مدد کے لیے ہیں',
            'We\'re Here to Help': 'ہم یہاں مدد کے لیے ہیں',
            'Get instant support for all your questions. Our AI-powered chatbot and live support team are ready to assist you 24/7.': 'اپنے تمام سوالات کے لیے فوری سپورٹ حاصل کریں۔ ہمارا AI-طاقت سے چلنے والا چیٹ بوٹ اور لائیو سپورٹ ٹیم 24/7 آپ کی مدد کے لیے تیار ہے۔',
            'Instant Response': 'فوری جواب',
            'Expert Support': 'ماہر سپورٹ',
            '24/7 Available': '24/7 دستیاب',
            'Start Support Chat': 'سپورٹ چیٹ شروع کریں',
            'View FAQ': 'FAQ دیکھیں',
            'Quick Help Categories': 'فوری مدد کی اقسام',
            'Choose a category to get started or describe your issue': 'شروع کرنے کے لیے ایک قسم منتخب کریں یا اپنے مسئلے کو بیان کریں',
            'Support Chat': 'سپورٹ چیٹ',
            'Online': 'آن لائن',
            'Hi there! 👋': 'السلام علیکم! 👋',
            'How can we help you today?': 'آج ہم آپ کی کیسے مدد کر سکتے ہیں؟',
            'Please select a category:': 'براہ کرم ایک قسم منتخب کریں:',
            'Language selection': 'زبان کا انتخاب',
            'Choose Language': 'زبان منتخب کریں',
            'Common Issues': 'عام مسائل',
            'Does any of these match your issue?': 'کیا ان میں سے کوئی آپ کے مسئلے سے میل کھاتا ہے؟',
            'Can\'t find your issue?': 'اپنا مسئلہ نہیں مل رہا؟',
            'Describe Your Issue': 'اپنے مسئلے کو بیان کریں',
            'Your Name (Optional)': 'آپ کا نام (اختیاری)',
            'Email (Optional)': 'ای میل (اختیاری)',
            'Enter your name': 'اپنا نام درج کریں',
            'Enter your email': 'اپنا ای میل درج کریں',
            'Type your question here...': 'یہاں اپنا سوال ٹائپ کریں...',
            'Connected with support': 'سپورٹ سے جڑے ہوئے',
            'Ticket': 'ٹکٹ',
            'Close': 'بند کریں',
            'Submit': 'جمع کریں',
            'Back': 'واپس'
        }
    }
}

def create_translation_files():
    """Create translation files for Hindi, Arabic, and Urdu"""
    for lang_code, lang_data in LANGUAGES.items():
        print(f"Creating translation files for {lang_data['name']} ({lang_code})...")
        
        # Create catalog
        catalog = Catalog(locale=lang_code)
        
        # Add translations to catalog
        for msgid, msgstr in lang_data['translations'].items():
            catalog.add(msgid, string=msgstr)
        
        # Write PO file
        lang_dir = f'translations/{lang_code}/LC_MESSAGES'
        po_path = f'{lang_dir}/messages.po'
        with open(po_path, 'wb') as f:
            write_po(f, catalog)
        
        # Compile to MO file
        mo_path = f'{lang_dir}/messages.mo'
        with open(mo_path, 'wb') as f:
            write_mo(f, catalog)
        
        print(f"✓ Created {po_path} and {mo_path}")

def main():
    print("Creating translation files for Hindi, Arabic, and Urdu...")
    
    create_translation_files()
    
    print("\n🎉 Translation files created successfully!")
    print("\nSupported languages:")
    for lang_code, lang_data in LANGUAGES.items():
        print(f"  • {lang_code}: {lang_data['name']}")

if __name__ == '__main__':
    main()
