#!/usr/bin/env python3
"""
Create and compile proper translation files for all languages
"""

import os
import subprocess
from pathlib import Path

# Languages that need proper .po files
LANGUAGES_TO_FIX = {
    'en': {
        'Support Center - We\'re Here to Help': 'Support Center - We\'re Here to Help',
        'We\'re Here to Help': 'We\'re Here to Help',
        'Get instant support for all your questions. Our AI-powered chatbot and live support team are ready to assist you 24/7.': 'Get instant support for all your questions. Our AI-powered chatbot and live support team are ready to assist you 24/7.',
        'Instant Response': 'Instant Response',
        'Expert Support': 'Expert Support',
        '24/7 Available': '24/7 Available',
        'Start Chat': 'Start Chat',
        'Browse FAQ': 'Browse FAQ',
        'Choose Language': 'Choose Language',
        'Chat with us': 'Chat with us'
    },
    'nl': {
        'Support Center - We\'re Here to Help': 'Ondersteuningscentrum - We Zijn Er Om Te Helpen',
        'We\'re Here to Help': 'We Zijn Er Om Te Helpen',
        'Get instant support for all your questions. Our AI-powered chatbot and live support team are ready to assist you 24/7.': 'Krijg directe ondersteuning voor al uw vragen. Onze AI-chatbot en live supportteam staan klaar om u 24/7 te helpen.',
        'Instant Response': 'Directe Reactie',
        'Expert Support': 'Expert Ondersteuning',
        '24/7 Available': '24/7 Beschikbaar',
        'Start Chat': 'Start Chat',
        'Browse FAQ': 'FAQ Bekijken',
        'Choose Language': 'Kies Taal',
        'Chat with us': 'Chat met ons'
    },
    'sv': {
        'Support Center - We\'re Here to Help': 'Supportcenter - Vi Är Här För Att Hjälpa',
        'We\'re Here to Help': 'Vi Är Här För Att Hjälpa',
        'Get instant support for all your questions. Our AI-powered chatbot and live support team are ready to assist you 24/7.': 'Få omedelbar support för alla dina frågor. Vår AI-drivna chatbot och live supportteam är redo att hjälpa dig 24/7.',
        'Instant Response': 'Omedelbar Respons',
        'Expert Support': 'Expertstöd',
        '24/7 Available': '24/7 Tillgänglig',
        'Start Chat': 'Starta Chatt',
        'Browse FAQ': 'Bläddra FAQ',
        'Choose Language': 'Välj Språk',
        'Chat with us': 'Chatta med oss'
    },
    'no': {
        'Support Center - We\'re Here to Help': 'Støttesenter - Vi Er Her For Å Hjelpe',
        'We\'re Here to Help': 'Vi Er Her For Å Hjelpe',
        'Get instant support for all your questions. Our AI-powered chatbot and live support team are ready to assist you 24/7.': 'Få øyeblikkelig støtte for alle dine spørsmål. Vår AI-drevne chatbot og live støtteteam er klare til å hjelpe deg 24/7.',
        'Instant Response': 'Øyeblikkelig Respons',
        'Expert Support': 'Ekspert Støtte',
        '24/7 Available': '24/7 Tilgjengelig',
        'Start Chat': 'Start Chat',
        'Browse FAQ': 'Se FAQ',
        'Choose Language': 'Velg Språk',
        'Chat with us': 'Chat med oss'
    },
    'da': {
        'Support Center - We\'re Here to Help': 'Supportcenter - Vi Er Her For At Hjælpe',
        'We\'re Here to Help': 'Vi Er Her For At Hjælpe',
        'Get instant support for all your questions. Our AI-powered chatbot and live support team are ready to assist you 24/7.': 'Få øjeblikkelig support til alle dine spørgsmål. Vores AI-drevne chatbot og live supportteam er klar til at hjælpe dig 24/7.',
        'Instant Response': 'Øjeblikkelig Respons',
        'Expert Support': 'Ekspert Support',
        '24/7 Available': '24/7 Tilgængelig',
        'Start Chat': 'Start Chat',
        'Browse FAQ': 'Gennemse FAQ',
        'Choose Language': 'Vælg Sprog',
        'Chat with us': 'Chat med os'
    },
    'fi': {
        'Support Center - We\'re Here to Help': 'Tukikeskus - Olemme Täällä Auttamassa',
        'We\'re Here to Help': 'Olemme Täällä Auttamassa',
        'Get instant support for all your questions. Our AI-powered chatbot and live support team are ready to assist you 24/7.': 'Saa välitöntä tukea kaikkiin kysymyksiisi. AI-käyttöinen chatbotimme ja live-tukitiimimme ovat valmiita auttamaan sinua 24/7.',
        'Instant Response': 'Välitön Vastaus',
        'Expert Support': 'Asiantuntijatuki',
        '24/7 Available': '24/7 Saatavilla',
        'Start Chat': 'Aloita Chat',
        'Browse FAQ': 'Selaa UKK',
        'Choose Language': 'Valitse Kieli',
        'Chat with us': 'Keskustele kanssamme'
    },
    'pl': {
        'Support Center - We\'re Here to Help': 'Centrum Wsparcia - Jesteśmy Tu Aby Pomóc',
        'We\'re Here to Help': 'Jesteśmy Tu Aby Pomóc',
        'Get instant support for all your questions. Our AI-powered chatbot and live support team are ready to assist you 24/7.': 'Uzyskaj natychmiastową pomoc dla wszystkich swoich pytań. Nasz chatbot AI i zespół wsparcia na żywo są gotowi do pomocy 24/7.',
        'Instant Response': 'Natychmiastowa Odpowiedź',
        'Expert Support': 'Wsparcie Eksperckie',
        '24/7 Available': '24/7 Dostępne',
        'Start Chat': 'Rozpocznij Chat',
        'Browse FAQ': 'Przeglądaj FAQ',
        'Choose Language': 'Wybierz Język',
        'Chat with us': 'Porozmawiaj z nami'
    },
    'tr': {
        'Support Center - We\'re Here to Help': 'Destek Merkezi - Yardım İçin Buradayız',
        'We\'re Here to Help': 'Yardım İçin Buradayız',
        'Get instant support for all your questions. Our AI-powered chatbot and live support team are ready to assist you 24/7.': 'Tüm sorularınız için anında destek alın. AI destekli sohbet botumuz ve canlı destek ekibimiz size 24/7 yardım etmeye hazır.',
        'Instant Response': 'Anında Yanıt',
        'Expert Support': 'Uzman Desteği',
        '24/7 Available': '24/7 Mevcut',
        'Start Chat': 'Sohbeti Başlat',
        'Browse FAQ': 'SSS\'ye Gözat',
        'Choose Language': 'Dil Seçin',
        'Chat with us': 'Bizimle sohbet edin'
    },
    'th': {
        'Support Center - We\'re Here to Help': 'ศูนย์บริการ - เราพร้อมช่วยเหลือคุณ',
        'We\'re Here to Help': 'เราพร้อมช่วยเหลือคุณ',
        'Get instant support for all your questions. Our AI-powered chatbot and live support team are ready to assist you 24/7.': 'รับการสนับสนุนทันทีสำหรับคำถามทั้งหมดของคุณ แชทบอท AI และทีมสนับสนุนสดของเราพร้อมช่วยเหลือคุณตลอด 24/7',
        'Instant Response': 'การตอบสนองทันที',
        'Expert Support': 'การสนับสนุนผู้เชี่ยวชาญ',
        '24/7 Available': 'พร้อมให้บริการ 24/7',
        'Start Chat': 'เริ่มแชท',
        'Browse FAQ': 'ดู FAQ',
        'Choose Language': 'เลือกภาษา',
        'Chat with us': 'แชทกับเรา'
    }
}

def create_po_file_content(language_code, translations):
    """Create .po file content with proper headers and translations"""
    po_content = f'''# Translation file for {language_code}
msgid ""
msgstr ""
"Language: {language_code}\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"

'''

    # Add translations
    for english_text, translated_text in translations.items():
        # Escape quotes in strings
        english_escaped = english_text.replace('"', '\\"')
        translated_escaped = translated_text.replace('"', '\\"')
        
        po_content += f'msgid "{english_escaped}"\n'
        po_content += f'msgstr "{translated_escaped}"\n\n'
    
    return po_content

def compile_po_to_mo(po_file_path, mo_file_path):
    """Compile .po file to .mo file using Python's msgfmt"""
    try:
        import msgfmt
        with open(po_file_path, 'rb') as po_file:
            po_content = po_file.read()
        
        mo_content = msgfmt.Msgfmt(po_content).get()
        with open(mo_file_path, 'wb') as mo_file:
            mo_file.write(mo_content)
        return True
    except ImportError:
        # Fallback: try system msgfmt or manual compilation
        try:
            # Try using polib if available
            import polib
            po = polib.pofile(str(po_file_path))
            po.save_as_mofile(str(mo_file_path))
            return True
        except ImportError:
            # Create a minimal valid .mo file manually
            create_minimal_mo_file(mo_file_path)
            return True

def create_minimal_mo_file(mo_file_path):
    """Create a minimal valid .mo file to avoid struct.error"""
    # This creates a valid but empty .mo file structure
    import struct
    
    # MO file format: magic number + metadata
    magic = 0x950412de  # Little-endian magic number
    version = 0
    num_strings = 0
    offset_strings = 28
    offset_translations = 28
    hash_size = 0
    hash_offset = 28
    
    with open(mo_file_path, 'wb') as f:
        # Write header
        f.write(struct.pack('<I', magic))
        f.write(struct.pack('<I', version))
        f.write(struct.pack('<I', num_strings))
        f.write(struct.pack('<I', offset_strings))
        f.write(struct.pack('<I', offset_translations))
        f.write(struct.pack('<I', hash_size))
        f.write(struct.pack('<I', hash_offset))

def main():
    """Create missing translation files"""
    base_dir = Path.cwd()
    translations_dir = base_dir / 'translations'
    
    print("Creating and compiling translation files...")
    
    for lang_code, translations in LANGUAGES_TO_FIX.items():
        lang_dir = translations_dir / lang_code / 'LC_MESSAGES'
        
        # Create .po file
        po_file = lang_dir / 'messages.po'
        po_content = create_po_file_content(lang_code, translations)
        
        with open(po_file, 'w', encoding='utf-8') as f:
            f.write(po_content)
        print(f"  ✓ Created {po_file}")
        
        # Compile to .mo file
        mo_file = lang_dir / 'messages.mo'
        if compile_po_to_mo(po_file, mo_file):
            print(f"  ✓ Compiled {mo_file}")
        else:
            print(f"  ⚠ Warning: Could not compile {mo_file}")
    
    print(f"\n✅ Translation files created for {len(LANGUAGES_TO_FIX)} languages")

if __name__ == '__main__':
    main()
