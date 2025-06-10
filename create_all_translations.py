#!/usr/bin/env python3
"""
Comprehensive translation setup script for Flask-Babel with all major languages
"""
import os
from babel.messages import Catalog
from babel.messages.pofile import write_po
from babel.messages.mofile import write_mo

# All supported languages with their translations
LANGUAGES = {
    'es': {  # Spanish
        'name': 'Español',
        'translations': {
            'Support Center - We\'re Here to Help': 'Centro de Soporte - Estamos Aquí para Ayudar',
            'We\'re Here to Help': 'Estamos Aquí para Ayudar',
            'Get instant support for all your questions. Our AI-powered chatbot and live support team are ready to assist you 24/7.': 'Obtén soporte instantáneo para todas tus preguntas. Nuestro chatbot impulsado por IA y el equipo de soporte en vivo están listos para ayudarte 24/7.',
            'Instant Response': 'Respuesta Instantánea',
            'Expert Support': 'Soporte Experto',
            '24/7 Available': 'Disponible 24/7',
            'Start Support Chat': 'Iniciar Chat de Soporte',
            'View FAQ': 'Ver Preguntas Frecuentes',
            'Quick Help Categories': 'Categorías de Ayuda Rápida',
            'Choose a category to get started or describe your issue': 'Elige una categoría para comenzar o describe tu problema',
            'Support Chat': 'Chat de Soporte',
            'Online': 'En Línea',
            'Hi there! 👋': '¡Hola! 👋',
            'How can we help you today?': '¿Cómo podemos ayudarte hoy?',
            'Please select a category:': 'Por favor selecciona una categoría:',
            'Language selection': 'Selección de idioma',
            'Choose Language': 'Elegir Idioma'
        }
    },
    'fr': {  # French
        'name': 'Français',
        'translations': {
            'Support Center - We\'re Here to Help': 'Centre de Support - Nous Sommes Là pour Vous Aider',
            'We\'re Here to Help': 'Nous Sommes Là pour Vous Aider',
            'Get instant support for all your questions. Our AI-powered chatbot and live support team are ready to assist you 24/7.': 'Obtenez un support instantané pour toutes vos questions. Notre chatbot alimenté par IA et notre équipe de support en direct sont prêts à vous aider 24/7.',
            'Instant Response': 'Réponse Instantanée',
            'Expert Support': 'Support Expert',
            '24/7 Available': 'Disponible 24/7',
            'Start Support Chat': 'Démarrer le Chat de Support',
            'View FAQ': 'Voir FAQ',
            'Quick Help Categories': 'Catégories d\'Aide Rapide',
            'Choose a category to get started or describe your issue': 'Choisissez une catégorie pour commencer ou décrivez votre problème',
            'Support Chat': 'Chat de Support',
            'Online': 'En Ligne',
            'Hi there! 👋': 'Salut! 👋',
            'How can we help you today?': 'Comment pouvons-nous vous aider aujourd\'hui?',
            'Please select a category:': 'Veuillez sélectionner une catégorie:',
            'Language selection': 'Sélection de langue',
            'Choose Language': 'Choisir la Langue'
        }
    },
    'de': {  # German
        'name': 'Deutsch',
        'translations': {
            'Support Center - We\'re Here to Help': 'Support-Center - Wir Sind Hier um zu Helfen',
            'We\'re Here to Help': 'Wir Sind Hier um zu Helfen',
            'Get instant support for all your questions. Our AI-powered chatbot and live support team are ready to assist you 24/7.': 'Erhalten Sie sofortige Unterstützung für alle Ihre Fragen. Unser KI-gestützter Chatbot und das Live-Support-Team stehen Ihnen rund um die Uhr zur Verfügung.',
            'Instant Response': 'Sofortige Antwort',
            'Expert Support': 'Experten-Support',
            '24/7 Available': '24/7 Verfügbar',
            'Start Support Chat': 'Support-Chat Starten',
            'View FAQ': 'FAQ Anzeigen',
            'Quick Help Categories': 'Schnelle Hilfe Kategorien',
            'Choose a category to get started or describe your issue': 'Wählen Sie eine Kategorie zum Starten oder beschreiben Sie Ihr Problem',
            'Support Chat': 'Support-Chat',
            'Online': 'Online',
            'Hi there! 👋': 'Hallo! 👋',
            'How can we help you today?': 'Wie können wir Ihnen heute helfen?',
            'Please select a category:': 'Bitte wählen Sie eine Kategorie:',
            'Language selection': 'Sprachauswahl',
            'Choose Language': 'Sprache Wählen'
        }
    },
    'it': {  # Italian
        'name': 'Italiano',
        'translations': {
            'Support Center - We\'re Here to Help': 'Centro di Supporto - Siamo Qui per Aiutarti',
            'We\'re Here to Help': 'Siamo Qui per Aiutarti',
            'Get instant support for all your questions. Our AI-powered chatbot and live support team are ready to assist you 24/7.': 'Ottieni supporto istantaneo per tutte le tue domande. Il nostro chatbot alimentato da IA e il team di supporto dal vivo sono pronti ad assisterti 24/7.',
            'Instant Response': 'Risposta Istantanea',
            'Expert Support': 'Supporto Esperto',
            '24/7 Available': 'Disponibile 24/7',
            'Start Support Chat': 'Inizia Chat di Supporto',
            'View FAQ': 'Visualizza FAQ',
            'Quick Help Categories': 'Categorie di Aiuto Rapido',
            'Choose a category to get started or describe your issue': 'Scegli una categoria per iniziare o descrivi il tuo problema',
            'Support Chat': 'Chat di Supporto',
            'Online': 'Online',
            'Hi there! 👋': 'Ciao! 👋',
            'How can we help you today?': 'Come possiamo aiutarti oggi?',
            'Please select a category:': 'Seleziona una categoria:',
            'Language selection': 'Selezione lingua',
            'Choose Language': 'Scegli Lingua'
        }
    },
    'pt': {  # Portuguese
        'name': 'Português',
        'translations': {
            'Support Center - We\'re Here to Help': 'Centro de Suporte - Estamos Aqui para Ajudar',
            'We\'re Here to Help': 'Estamos Aqui para Ajudar',
            'Get instant support for all your questions. Our AI-powered chatbot and live support team are ready to assist you 24/7.': 'Obtenha suporte instantâneo para todas as suas perguntas. Nosso chatbot alimentado por IA e equipe de suporte ao vivo estão prontos para ajudá-lo 24/7.',
            'Instant Response': 'Resposta Instantânea',
            'Expert Support': 'Suporte Especializado',
            '24/7 Available': 'Disponível 24/7',
            'Start Support Chat': 'Iniciar Chat de Suporte',
            'View FAQ': 'Ver FAQ',
            'Quick Help Categories': 'Categorias de Ajuda Rápida',
            'Choose a category to get started or describe your issue': 'Escolha uma categoria para começar ou descreva seu problema',
            'Support Chat': 'Chat de Suporte',
            'Online': 'Online',
            'Hi there! 👋': 'Olá! 👋',
            'How can we help you today?': 'Como podemos ajudá-lo hoje?',
            'Please select a category:': 'Selecione uma categoria:',
            'Language selection': 'Seleção de idioma',
            'Choose Language': 'Escolher Idioma'
        }
    },
    'ru': {  # Russian
        'name': 'Русский',
        'translations': {
            'Support Center - We\'re Here to Help': 'Центр Поддержки - Мы Здесь, Чтобы Помочь',
            'We\'re Here to Help': 'Мы Здесь, Чтобы Помочь',
            'Get instant support for all your questions. Our AI-powered chatbot and live support team are ready to assist you 24/7.': 'Получите мгновенную поддержку для всех ваших вопросов. Наш чат-бот с ИИ и команда поддержки готовы помочь вам 24/7.',
            'Instant Response': 'Мгновенный Ответ',
            'Expert Support': 'Экспертная Поддержка',
            '24/7 Available': 'Доступно 24/7',
            'Start Support Chat': 'Начать Чат Поддержки',
            'View FAQ': 'Посмотреть FAQ',
            'Quick Help Categories': 'Категории Быстрой Помощи',
            'Choose a category to get started or describe your issue': 'Выберите категорию для начала или опишите вашу проблему',
            'Support Chat': 'Чат Поддержки',
            'Online': 'В Сети',
            'Hi there! 👋': 'Привет! 👋',
            'How can we help you today?': 'Как мы можем помочь вам сегодня?',
            'Please select a category:': 'Пожалуйста, выберите категорию:',
            'Language selection': 'Выбор языка',
            'Choose Language': 'Выбрать Язык'
        }
    },
    'zh': {  # Chinese
        'name': '中文',
        'translations': {
            'Support Center - We\'re Here to Help': '支持中心 - 我们在这里为您提供帮助',
            'We\'re Here to Help': '我们在这里为您提供帮助',
            'Get instant support for all your questions. Our AI-powered chatbot and live support team are ready to assist you 24/7.': '为您的所有问题获得即时支持。我们的AI聊天机器人和实时支持团队随时准备为您提供24/7全天候帮助。',
            'Instant Response': '即时响应',
            'Expert Support': '专家支持',
            '24/7 Available': '24/7可用',
            'Start Support Chat': '开始支持聊天',
            'View FAQ': '查看常见问题',
            'Quick Help Categories': '快速帮助类别',
            'Choose a category to get started or describe your issue': '选择类别开始或描述您的问题',
            'Support Chat': '支持聊天',
            'Online': '在线',
            'Hi there! 👋': '您好！👋',
            'How can we help you today?': '今天我们如何为您提供帮助？',
            'Please select a category:': '请选择一个类别：',
            'Language selection': '语言选择',
            'Choose Language': '选择语言'
        }
    },
    'ja': {  # Japanese
        'name': '日本語',
        'translations': {
            'Support Center - We\'re Here to Help': 'サポートセンター - お手伝いします',
            'We\'re Here to Help': 'お手伝いします',
            'Get instant support for all your questions. Our AI-powered chatbot and live support team are ready to assist you 24/7.': 'すべてのご質問に対して即座にサポートを受けられます。AIチャットボットとライブサポートチームが24時間365日対応いたします。',
            'Instant Response': '即座の応答',
            'Expert Support': 'エキスパートサポート',
            '24/7 Available': '24時間365日利用可能',
            'Start Support Chat': 'サポートチャットを開始',
            'View FAQ': 'FAQを見る',
            'Quick Help Categories': 'クイックヘルプカテゴリ',
            'Choose a category to get started or describe your issue': 'カテゴリを選択して開始するか、問題を説明してください',
            'Support Chat': 'サポートチャット',
            'Online': 'オンライン',
            'Hi there! 👋': 'こんにちは！👋',
            'How can we help you today?': '今日はどのようにお手伝いできますか？',
            'Please select a category:': 'カテゴリを選択してください：',
            'Language selection': '言語選択',
            'Choose Language': '言語を選択'
        }
    },
    'ko': {  # Korean
        'name': '한국어',
        'translations': {
            'Support Center - We\'re Here to Help': '지원 센터 - 저희가 도와드리겠습니다',
            'We\'re Here to Help': '저희가 도와드리겠습니다',
            'Get instant support for all your questions. Our AI-powered chatbot and live support team are ready to assist you 24/7.': '모든 질문에 대해 즉시 지원을 받으세요. AI 챗봇과 실시간 지원팀이 24시간 연중무휴로 도움을 드립니다.',
            'Instant Response': '즉시 응답',
            'Expert Support': '전문가 지원',
            '24/7 Available': '24시간 이용 가능',
            'Start Support Chat': '지원 채팅 시작',
            'View FAQ': 'FAQ 보기',
            'Quick Help Categories': '빠른 도움말 카테고리',
            'Choose a category to get started or describe your issue': '시작할 카테고리를 선택하거나 문제를 설명하세요',
            'Support Chat': '지원 채팅',
            'Online': '온라인',
            'Hi there! 👋': '안녕하세요! 👋',
            'How can we help you today?': '오늘 어떻게 도와드릴까요?',
            'Please select a category:': '카테고리를 선택해주세요:',
            'Language selection': '언어 선택',
            'Choose Language': '언어 선택'
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
            'Choose Language': 'اختر اللغة'
        }
    },
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
            'Choose Language': 'भाषा चुनें'
        }
    },
    'nl': {  # Dutch
        'name': 'Nederlands',
        'translations': {
            'Support Center - We\'re Here to Help': 'Ondersteuningscentrum - Wij Zijn Er Om Te Helpen',
            'We\'re Here to Help': 'Wij Zijn Er Om Te Helpen',
            'Get instant support for all your questions. Our AI-powered chatbot and live support team are ready to assist you 24/7.': 'Krijg directe ondersteuning voor al uw vragen. Onze AI-aangedreven chatbot en live ondersteuningsteam staan klaar om u 24/7 te helpen.',
            'Instant Response': 'Directe Reactie',
            'Expert Support': 'Expert Ondersteuning',
            '24/7 Available': '24/7 Beschikbaar',
            'Start Support Chat': 'Start Ondersteuningschat',
            'View FAQ': 'Bekijk FAQ',
            'Quick Help Categories': 'Snelle Hulp Categorieën',
            'Choose a category to get started or describe your issue': 'Kies een categorie om te beginnen of beschrijf uw probleem',
            'Support Chat': 'Ondersteuningschat',
            'Online': 'Online',
            'Hi there! 👋': 'Hallo daar! 👋',
            'How can we help you today?': 'Hoe kunnen wij u vandaag helpen?',
            'Please select a category:': 'Selecteer een categorie:',
            'Language selection': 'Taalselectie',
            'Choose Language': 'Kies Taal'
        }
    }
}

def create_translation_files():
    """Create translation files for all supported languages"""
    for lang_code, lang_data in LANGUAGES.items():
        print(f"Creating translation files for {lang_data['name']} ({lang_code})...")
        
        # Create directory structure
        lang_dir = f'translations/{lang_code}/LC_MESSAGES'
        os.makedirs(lang_dir, exist_ok=True)
        
        # Create catalog
        catalog = Catalog(locale=lang_code)
        
        # Add translations to catalog
        for msgid, msgstr in lang_data['translations'].items():
            catalog.add(msgid, string=msgstr)
        
        # Write PO file
        po_path = f'{lang_dir}/messages.po'
        with open(po_path, 'wb') as f:
            write_po(f, catalog)
        
        # Compile to MO file
        mo_path = f'{lang_dir}/messages.mo'
        with open(mo_path, 'wb') as f:
            write_mo(f, catalog)
        
        print(f"✓ Created {po_path} and {mo_path}")

def main():
    print("Setting up comprehensive translation support...")
    print(f"Creating translation files for {len(LANGUAGES)} languages...")
    
    create_translation_files()
    
    print("\n🎉 Translation setup complete!")
    print("\nSupported languages:")
    for lang_code, lang_data in LANGUAGES.items():
        print(f"  • {lang_code}: {lang_data['name']}")
    
    print("\nTo add more translations:")
    print("1. Edit the LANGUAGES dictionary in this script")
    print("2. Run this script again to regenerate the files")
    print("3. Restart your Flask application")

if __name__ == '__main__':
    main()
