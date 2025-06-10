#!/usr/bin/env python3
"""
Simple script to create missing translation directories
"""

import os
from pathlib import Path

# Missing languages that need to be created
MISSING_LANGUAGES = ['en', 'nl', 'sv', 'no', 'da', 'fi', 'pl', 'tr', 'th']

def create_simple_po_content(lang_code):
    """Create basic .po file content"""
    return f'''# Translation file for {lang_code}
msgid ""
msgstr ""
"Language: {lang_code}\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"

msgid "Support Center - We're Here to Help"
msgstr "Support Center - We're Here to Help"

msgid "We're Here to Help"
msgstr "We're Here to Help"

msgid "Choose Language"
msgstr "Choose Language"

msgid "Chat with us"
msgstr "Chat with us"

msgid "Start Chat"
msgstr "Start Chat"

msgid "Browse FAQ"
msgstr "Browse FAQ"

msgid "Instant Response"
msgstr "Instant Response"

msgid "Expert Support"
msgstr "Expert Support"

msgid "24/7 Available"
msgstr "24/7 Available"
'''

def main():
    base_dir = Path.cwd()
    translations_dir = base_dir / 'translations'
    
    print("Creating missing language directories...")
    
    for lang_code in MISSING_LANGUAGES:
        lang_dir = translations_dir / lang_code / 'LC_MESSAGES'
        lang_dir.mkdir(parents=True, exist_ok=True)
        
        # Create .po file
        po_file = lang_dir / 'messages.po'
        with open(po_file, 'w', encoding='utf-8') as f:
            f.write(create_simple_po_content(lang_code))
        
        # Create empty .mo file (we'll compile later)
        mo_file = lang_dir / 'messages.mo'
        mo_file.touch()
        
        print(f"  ✓ Created {lang_code}")
    
    print(f"\n✅ Created {len(MISSING_LANGUAGES)} missing language directories")

if __name__ == '__main__':
    main()
