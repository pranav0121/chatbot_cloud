#!/usr/bin/env python3
"""
Create basic translation files for additional languages
"""
import os
from babel.messages import Catalog
from babel.messages.pofile import write_po
from babel.messages.mofile import write_mo

# Basic translations for key phrases
basic_translations = {
    'it': {  # Italian
        'Support Center - We\'re Here to Help': 'Centro di Supporto - Siamo Qui per Aiutarti',
        'We\'re Here to Help': 'Siamo Qui per Aiutarti',
        'Start Support Chat': 'Inizia Chat di Supporto',
        'Choose Language': 'Scegli Lingua',
        'Hi there! 👋': 'Ciao! 👋',
        'How can we help you today?': 'Come possiamo aiutarti oggi?'
    },
    'pt': {  # Portuguese
        'Support Center - We\'re Here to Help': 'Centro de Suporte - Estamos Aqui para Ajudar',
        'We\'re Here to Help': 'Estamos Aqui para Ajudar',
        'Start Support Chat': 'Iniciar Chat de Suporte',
        'Choose Language': 'Escolher Idioma',
        'Hi there! 👋': 'Olá! 👋',
        'How can we help you today?': 'Como podemos ajudá-lo hoje?'
    },
    'ru': {  # Russian
        'Support Center - We\'re Here to Help': 'Центр Поддержки - Мы Здесь, Чтобы Помочь',
        'We\'re Here to Help': 'Мы Здесь, Чтобы Помочь',
        'Start Support Chat': 'Начать Чат Поддержки',
        'Choose Language': 'Выбрать Язык',
        'Hi there! 👋': 'Привет! 👋',
        'How can we help you today?': 'Как мы можем помочь вам сегодня?'
    },
    'zh': {  # Chinese
        'Support Center - We\'re Here to Help': '支持中心 - 我们在这里为您提供帮助',
        'We\'re Here to Help': '我们在这里为您提供帮助',
        'Start Support Chat': '开始支持聊天',
        'Choose Language': '选择语言',
        'Hi there! 👋': '您好！👋',
        'How can we help you today?': '今天我们如何为您提供帮助？'
    },
    'ja': {  # Japanese
        'Support Center - We\'re Here to Help': 'サポートセンター - お手伝いします',
        'We\'re Here to Help': 'お手伝いします',
        'Start Support Chat': 'サポートチャットを開始',
        'Choose Language': '言語を選択',
        'Hi there! 👋': 'こんにちは！👋',
        'How can we help you today?': '今日はどのようにお手伝いできますか？'
    },
    'ko': {  # Korean
        'Support Center - We\'re Here to Help': '지원 센터 - 저희가 도와드리겠습니다',
        'We\'re Here to Help': '저희가 도와드리겠습니다',
        'Start Support Chat': '지원 채팅 시작',
        'Choose Language': '언어 선택',
        'Hi there! 👋': '안녕하세요! 👋',
        'How can we help you today?': '오늘 어떻게 도와드릴까요?'
    }
}

for lang, translations in basic_translations.items():
    print(f"Creating {lang} translation files...")
    
    # Create catalog
    catalog = Catalog(locale=lang)
    
    # Add translations
    for msgid, msgstr in translations.items():
        catalog.add(msgid, string=msgstr)
    
    # Write PO file
    lang_dir = f'translations/{lang}/LC_MESSAGES'
    po_path = f'{lang_dir}/messages.po'
    with open(po_path, 'wb') as f:
        write_po(f, catalog)
    
    # Compile to MO file
    mo_path = f'{lang_dir}/messages.mo'
    with open(mo_path, 'wb') as f:
        write_mo(f, catalog)
    
    print(f"✓ Created {po_path} and {mo_path}")

print("✅ Additional language support created!")
