#!/usr/bin/env python3
"""
Create missing translation directories and files for all supported languages
"""

import os
import subprocess
from pathlib import Path

# All supported languages with their translations
LANGUAGES = {
    'en': 'English',
    'es': 'Español', 
    'fr': 'Français',
    'de': 'Deutsch',
    'it': 'Italiano',
    'pt': 'Português',
    'ru': 'Русский',
    'zh': '中文',
    'ja': '日本語',
    'ko': '한국어',
    'ar': 'العربية',
    'hi': 'हिन्दी',
    'ur': 'اردو',
    'nl': 'Nederlands',
    'sv': 'Svenska',
    'no': 'Norsk',
    'da': 'Dansk',
    'fi': 'Suomi',
    'pl': 'Polski',
    'tr': 'Türkçe',
    'th': 'ไทย'
}

# Common translations for UI elements
TRANSLATIONS = {
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
        'Chat with us': 'Chat with us',
        'Type your message here...': 'Type your message here...',
        'Send': 'Send',
        'Hello! How can I help you today?': 'Hello! How can I help you today?',
        'Thank you for visiting our support center. We\'re here to help!': 'Thank you for visiting our support center. We\'re here to help!'
    },
    'es': {
        'Support Center - We\'re Here to Help': 'Centro de Soporte - Estamos Aquí para Ayudar',
        'We\'re Here to Help': 'Estamos Aquí para Ayudar',
        'Get instant support for all your questions. Our AI-powered chatbot and live support team are ready to assist you 24/7.': 'Obtenga soporte instantáneo para todas sus preguntas. Nuestro chatbot con IA y equipo de soporte en vivo están listos para ayudarle 24/7.',
        'Instant Response': 'Respuesta Instantánea',
        'Expert Support': 'Soporte Experto',
        '24/7 Available': 'Disponible 24/7',
        'Start Chat': 'Iniciar Chat',
        'Browse FAQ': 'Ver Preguntas Frecuentes',
        'Choose Language': 'Elegir Idioma',
        'Chat with us': 'Chatear con nosotros',
        'Type your message here...': 'Escriba su mensaje aquí...',
        'Send': 'Enviar',
        'Hello! How can I help you today?': '¡Hola! ¿Cómo puedo ayudarte hoy?',
        'Thank you for visiting our support center. We\'re here to help!': '¡Gracias por visitar nuestro centro de soporte. Estamos aquí para ayudar!'
    },
    'fr': {
        'Support Center - We\'re Here to Help': 'Centre de Support - Nous Sommes Là pour Vous Aider',
        'We\'re Here to Help': 'Nous Sommes Là pour Vous Aider',
        'Get instant support for all your questions. Our AI-powered chatbot and live support team are ready to assist you 24/7.': 'Obtenez un support instantané pour toutes vos questions. Notre chatbot IA et équipe de support en direct sont prêts à vous assister 24/7.',
        'Instant Response': 'Réponse Instantanée',
        'Expert Support': 'Support Expert',
        '24/7 Available': 'Disponible 24/7',
        'Start Chat': 'Démarrer le Chat',
        'Browse FAQ': 'Parcourir la FAQ',
        'Choose Language': 'Choisir la Langue',
        'Chat with us': 'Chattez avec nous',
        'Type your message here...': 'Tapez votre message ici...',
        'Send': 'Envoyer',
        'Hello! How can I help you today?': 'Bonjour! Comment puis-je vous aider aujourd\'hui?',
        'Thank you for visiting our support center. We\'re here to help!': 'Merci de visiter notre centre de support. Nous sommes là pour vous aider!'
    },
    'de': {
        'Support Center - We\'re Here to Help': 'Support-Center - Wir Sind Da, Um Zu Helfen',
        'We\'re Here to Help': 'Wir Sind Da, Um Zu Helfen',
        'Get instant support for all your questions. Our AI-powered chatbot and live support team are ready to assist you 24/7.': 'Erhalten Sie sofortigen Support für alle Ihre Fragen. Unser KI-gestützter Chatbot und Live-Support-Team sind bereit, Ihnen 24/7 zu helfen.',
        'Instant Response': 'Sofortige Antwort',
        'Expert Support': 'Experten-Support',
        '24/7 Available': '24/7 Verfügbar',
        'Start Chat': 'Chat Starten',
        'Browse FAQ': 'FAQ Durchsuchen',
        'Choose Language': 'Sprache Wählen',
        'Chat with us': 'Chatten Sie mit uns',
        'Type your message here...': 'Geben Sie hier Ihre Nachricht ein...',
        'Send': 'Senden',
        'Hello! How can I help you today?': 'Hallo! Wie kann ich Ihnen heute helfen?',
        'Thank you for visiting our support center. We\'re here to help!': 'Vielen Dank für den Besuch unseres Support-Centers. Wir sind da, um zu helfen!'
    },
    'it': {
        'Support Center - We\'re Here to Help': 'Centro di Supporto - Siamo Qui per Aiutare',
        'We\'re Here to Help': 'Siamo Qui per Aiutare',
        'Get instant support for all your questions. Our AI-powered chatbot and live support team are ready to assist you 24/7.': 'Ottieni supporto istantaneo per tutte le tue domande. Il nostro chatbot AI e il team di supporto dal vivo sono pronti ad assisterti 24/7.',
        'Instant Response': 'Risposta Istantanea',
        'Expert Support': 'Supporto Esperto',
        '24/7 Available': 'Disponibile 24/7',
        'Start Chat': 'Inizia Chat',
        'Browse FAQ': 'Sfoglia FAQ',
        'Choose Language': 'Scegli Lingua',
        'Chat with us': 'Chatta con noi',
        'Type your message here...': 'Digita il tuo messaggio qui...',
        'Send': 'Invia',
        'Hello! How can I help you today?': 'Ciao! Come posso aiutarti oggi?',
        'Thank you for visiting our support center. We\'re here to help!': 'Grazie per aver visitato il nostro centro di supporto. Siamo qui per aiutare!'
    },
    'pt': {
        'Support Center - We\'re Here to Help': 'Centro de Suporte - Estamos Aqui para Ajudar',
        'We\'re Here to Help': 'Estamos Aqui para Ajudar',
        'Get instant support for all your questions. Our AI-powered chatbot and live support team are ready to assist you 24/7.': 'Obtenha suporte instantâneo para todas as suas perguntas. Nosso chatbot com IA e equipe de suporte ao vivo estão prontos para ajudá-lo 24/7.',
        'Instant Response': 'Resposta Instantânea',
        'Expert Support': 'Suporte Especializado',
        '24/7 Available': 'Disponível 24/7',
        'Start Chat': 'Iniciar Chat',
        'Browse FAQ': 'Navegar FAQ',
        'Choose Language': 'Escolher Idioma',
        'Chat with us': 'Converse conosco',
        'Type your message here...': 'Digite sua mensagem aqui...',
        'Send': 'Enviar',
        'Hello! How can I help you today?': 'Olá! Como posso ajudá-lo hoje?',
        'Thank you for visiting our support center. We\'re here to help!': 'Obrigado por visitar nosso centro de suporte. Estamos aqui para ajudar!'
    },
    'ru': {
        'Support Center - We\'re Here to Help': 'Центр Поддержки - Мы Здесь, Чтобы Помочь',
        'We\'re Here to Help': 'Мы Здесь, Чтобы Помочь',
        'Get instant support for all your questions. Our AI-powered chatbot and live support team are ready to assist you 24/7.': 'Получите мгновенную поддержку по всем вашим вопросам. Наш чат-бот с ИИ и команда поддержки готовы помочь вам 24/7.',
        'Instant Response': 'Мгновенный Ответ',
        'Expert Support': 'Экспертная Поддержка',
        '24/7 Available': 'Доступно 24/7',
        'Start Chat': 'Начать Чат',
        'Browse FAQ': 'Просмотр FAQ',
        'Choose Language': 'Выбрать Язык',
        'Chat with us': 'Чат с нами',
        'Type your message here...': 'Введите ваше сообщение здесь...',
        'Send': 'Отправить',
        'Hello! How can I help you today?': 'Привет! Как я могу помочь вам сегодня?',
        'Thank you for visiting our support center. We\'re here to help!': 'Спасибо за посещение нашего центра поддержки. Мы здесь, чтобы помочь!'
    },
    'zh': {
        'Support Center - We\'re Here to Help': '支持中心 - 我们在这里为您服务',
        'We\'re Here to Help': '我们在这里为您服务',
        'Get instant support for all your questions. Our AI-powered chatbot and live support team are ready to assist you 24/7.': '为您的所有问题获得即时支持。我们的AI聊天机器人和在线支持团队随时准备为您提供24/7服务。',
        'Instant Response': '即时响应',
        'Expert Support': '专家支持',
        '24/7 Available': '24/7可用',
        'Start Chat': '开始聊天',
        'Browse FAQ': '浏览常见问题',
        'Choose Language': '选择语言',
        'Chat with us': '与我们聊天',
        'Type your message here...': '在此输入您的消息...',
        'Send': '发送',
        'Hello! How can I help you today?': '您好！今天我可以为您做些什么？',
        'Thank you for visiting our support center. We\'re here to help!': '感谢您访问我们的支持中心。我们在这里为您服务！'
    },
    'ja': {
        'Support Center - We\'re Here to Help': 'サポートセンター - お手伝いします',
        'We\'re Here to Help': 'お手伝いします',
        'Get instant support for all your questions. Our AI-powered chatbot and live support team are ready to assist you 24/7.': 'すべてのご質問に即座にサポートを提供します。AIチャットボットとライブサポートチームが24時間365日対応いたします。',
        'Instant Response': '即座の対応',
        'Expert Support': '専門サポート',
        '24/7 Available': '24時間365日利用可能',
        'Start Chat': 'チャット開始',
        'Browse FAQ': 'よくある質問を見る',
        'Choose Language': '言語を選択',
        'Chat with us': 'チャットする',
        'Type your message here...': 'メッセージをここに入力...',
        'Send': '送信',
        'Hello! How can I help you today?': 'こんにちは！今日はどのようにお手伝いできますか？',
        'Thank you for visiting our support center. We\'re here to help!': 'サポートセンターにお越しいただきありがとうございます。お手伝いします！'
    },
    'ko': {
        'Support Center - We\'re Here to Help': '지원 센터 - 도움을 드리겠습니다',
        'We\'re Here to Help': '도움을 드리겠습니다',
        'Get instant support for all your questions. Our AI-powered chatbot and live support team are ready to assist you 24/7.': '모든 질문에 대한 즉시 지원을 받으세요. AI 챗봇과 라이브 지원팀이 24시간 연중무휴로 도움을 드릴 준비가 되어 있습니다.',
        'Instant Response': '즉시 응답',
        'Expert Support': '전문가 지원',
        '24/7 Available': '24시간 이용 가능',
        'Start Chat': '채팅 시작',
        'Browse FAQ': 'FAQ 보기',
        'Choose Language': '언어 선택',
        'Chat with us': '채팅하기',
        'Type your message here...': '여기에 메시지를 입력하세요...',
        'Send': '보내기',
        'Hello! How can I help you today?': '안녕하세요! 오늘 어떻게 도와드릴까요?',
        'Thank you for visiting our support center. We\'re here to help!': '지원 센터를 방문해 주셔서 감사합니다. 도움을 드리겠습니다!'
    },
    'ar': {
        'Support Center - We\'re Here to Help': 'مركز الدعم - نحن هنا للمساعدة',
        'We\'re Here to Help': 'نحن هنا للمساعدة',
        'Get instant support for all your questions. Our AI-powered chatbot and live support team are ready to assist you 24/7.': 'احصل على دعم فوري لجميع أسئلتك. روبوت الدردشة المدعوم بالذكاء الاصطناعي وفريق الدعم المباشر جاهزان لمساعدتك على مدار الساعة طوال أيام الأسبوع.',
        'Instant Response': 'استجابة فورية',
        'Expert Support': 'دعم خبير',
        '24/7 Available': 'متاح 24/7',
        'Start Chat': 'بدء المحادثة',
        'Browse FAQ': 'تصفح الأسئلة الشائعة',
        'Choose Language': 'اختر اللغة',
        'Chat with us': 'تحدث معنا',
        'Type your message here...': 'اكتب رسالتك هنا...',
        'Send': 'إرسال',
        'Hello! How can I help you today?': 'مرحبا! كيف يمكنني مساعدتك اليوم؟',
        'Thank you for visiting our support center. We\'re here to help!': 'شكرا لزيارة مركز الدعم الخاص بنا. نحن هنا للمساعدة!'
    },
    'hi': {
        'Support Center - We\'re Here to Help': 'सहायता केंद्र - हम यहाँ मदद के लिए हैं',
        'We\'re Here to Help': 'हम यहाँ मदद के लिए हैं',
        'Get instant support for all your questions. Our AI-powered chatbot and live support team are ready to assist you 24/7.': 'अपने सभी प्रश्नों के लिए तुरंत सहायता प्राप्त करें। हमारा AI-संचालित चैटबॉट और लाइव सपोर्ट टीम 24/7 आपकी सहायता के लिए तैयार है।',
        'Instant Response': 'तुरंत जवाब',
        'Expert Support': 'विशेषज्ञ सहायता',
        '24/7 Available': '24/7 उपलब्ध',
        'Start Chat': 'चैट शुरू करें',
        'Browse FAQ': 'FAQ देखें',
        'Choose Language': 'भाषा चुनें',
        'Chat with us': 'हमसे चैट करें',
        'Type your message here...': 'यहाँ अपना संदेश टाइप करें...',
        'Send': 'भेजें',
        'Hello! How can I help you today?': 'नमस्ते! आज मैं आपकी कैसे मदद कर सकता हूँ?',
        'Thank you for visiting our support center. We\'re here to help!': 'हमारे सहायता केंद्र पर आने के लिए धन्यवाद। हम यहाँ मदद के लिए हैं!'
    },
    'ur': {
        'Support Center - We\'re Here to Help': 'سپورٹ سینٹر - ہم یہاں مدد کے لیے ہیں',
        'We\'re Here to Help': 'ہم یہاں مدد کے لیے ہیں',
        'Get instant support for all your questions. Our AI-powered chatbot and live support team are ready to assist you 24/7.': 'اپنے تمام سوالات کے لیے فوری سپورٹ حاصل کریں۔ ہمارا AI چیٹ بوٹ اور لائیو سپورٹ ٹیم 24/7 آپ کی مدد کے لیے تیار ہے۔',
        'Instant Response': 'فوری جواب',
        'Expert Support': 'ماہر سپورٹ',
        '24/7 Available': '24/7 دستیاب',
        'Start Chat': 'چیٹ شروع کریں',
        'Browse FAQ': 'FAQ دیکھیں',
        'Choose Language': 'زبان منتخب کریں',
        'Chat with us': 'ہم سے چیٹ کریں',
        'Type your message here...': 'یہاں اپنا پیغام ٹائپ کریں...',
        'Send': 'بھیجیں',
        'Hello! How can I help you today?': 'سلام! آج میں آپ کی کیسے مدد کر سکتا ہوں؟',
        'Thank you for visiting our support center. We\'re here to help!': 'ہمارے سپورٹ سینٹر میں آنے کا شکریہ۔ ہم یہاں مدد کے لیے ہیں!'
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
        'Chat with us': 'Chat met ons',
        'Type your message here...': 'Typ hier uw bericht...',
        'Send': 'Verzenden',
        'Hello! How can I help you today?': 'Hallo! Hoe kan ik u vandaag helpen?',
        'Thank you for visiting our support center. We\'re here to help!': 'Bedankt voor het bezoeken van ons ondersteuningscentrum. We zijn er om te helpen!'
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
        'Chat with us': 'Chatta med oss',
        'Type your message here...': 'Skriv ditt meddelande här...',
        'Send': 'Skicka',
        'Hello! How can I help you today?': 'Hej! Hur kan jag hjälpa dig idag?',
        'Thank you for visiting our support center. We\'re here to help!': 'Tack för att du besöker vårt supportcenter. Vi är här för att hjälpa!'
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
        'Chat with us': 'Chat med oss',
        'Type your message here...': 'Skriv meldingen din her...',
        'Send': 'Send',
        'Hello! How can I help you today?': 'Hei! Hvordan kan jeg hjelpe deg i dag?',
        'Thank you for visiting our support center. We\'re here to help!': 'Takk for at du besøker vårt støttesenter. Vi er her for å hjelpe!'
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
        'Chat with us': 'Chat med os',
        'Type your message here...': 'Skriv din besked her...',
        'Send': 'Send',
        'Hello! How can I help you today?': 'Hej! Hvordan kan jeg hjælpe dig i dag?',
        'Thank you for visiting our support center. We\'re here to help!': 'Tak for at besøge vores supportcenter. Vi er her for at hjælpe!'
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
        'Chat with us': 'Keskustele kanssamme',
        'Type your message here...': 'Kirjoita viestisi tähän...',
        'Send': 'Lähetä',
        'Hello! How can I help you today?': 'Hei! Miten voin auttaa sinua tänään?',
        'Thank you for visiting our support center. We\'re here to help!': 'Kiitos kun vierailit tukikeskuksessamme. Olemme täällä auttamassa!'
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
        'Chat with us': 'Porozmawiaj z nami',
        'Type your message here...': 'Wpisz swoją wiadomość tutaj...',
        'Send': 'Wyślij',
        'Hello! How can I help you today?': 'Cześć! Jak mogę pomóc Ci dzisiaj?',
        'Thank you for visiting our support center. We\'re here to help!': 'Dziękujemy za odwiedzenie naszego centrum wsparcia. Jesteśmy tu aby pomóc!'
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
        'Chat with us': 'Bizimle sohbet edin',
        'Type your message here...': 'Mesajınızı buraya yazın...',
        'Send': 'Gönder',
        'Hello! How can I help you today?': 'Merhaba! Bugün size nasıl yardımcı olabilirim?',
        'Thank you for visiting our support center. We\'re here to help!': 'Destek merkezimizi ziyaret ettiğiniz için teşekkürler. Yardım için buradayız!'
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
        'Chat with us': 'แชทกับเรา',
        'Type your message here...': 'พิมพ์ข้อความของคุณที่นี่...',
        'Send': 'ส่ง',
        'Hello! How can I help you today?': 'สวัสดี! วันนี้ฉันจะช่วยคุณได้อย่างไร?',
        'Thank you for visiting our support center. We\'re here to help!': 'ขอบคุณที่เยี่ยมชมศูนย์บริการของเรา เราพร้อมช่วยเหลือคุณ!'
    }
}

def create_po_file_content(language_code, translations):
    """Create .po file content with proper headers and translations"""
    po_content = f'''# Translation file for {LANGUAGES[language_code]}
# Copyright (C) 2024
# This file is distributed under the same license as the Flask Chatbot package.
#
#, fuzzy
msgid ""
msgstr ""
"Project-Id-Version: Flask Chatbot 1.0\\n"
"Report-Msgid-Bugs-To: support@youcloudtech.com\\n"
"POT-Creation-Date: 2024-01-01 12:00+0000\\n"
"PO-Revision-Date: 2024-01-01 12:00+0000\\n"
"Last-Translator: Auto Generated\\n"
"Language: {language_code}\\n"
"Language-Team: {LANGUAGES[language_code]}\\n"
"Plural-Forms: nplurals=2; plural=(n != 1);\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"

'''

    # Add translations
    for english_text, translated_text in translations.items():
        po_content += f'msgid "{english_text}"\n'
        po_content += f'msgstr "{translated_text}"\n\n'
    
    return po_content

def main():
    """Create missing translation directories and files"""
    base_dir = Path.cwd()
    translations_dir = base_dir / 'translations'
    
    # Create main translations directory if it doesn't exist
    translations_dir.mkdir(exist_ok=True)
    
    print("Creating translation directories and files...")
    
    for lang_code, lang_name in LANGUAGES.items():
        lang_dir = translations_dir / lang_code / 'LC_MESSAGES'
        
        # Create language directory structure
        lang_dir.mkdir(parents=True, exist_ok=True)
        
        # Create .po file
        po_file = lang_dir / 'messages.po'
        if lang_code in TRANSLATIONS:
            po_content = create_po_file_content(lang_code, TRANSLATIONS[lang_code])
            with open(po_file, 'w', encoding='utf-8') as f:
                f.write(po_content)
            print(f"  ✓ Created {po_file}")
        
        # Compile .po to .mo file
        mo_file = lang_dir / 'messages.mo'
        try:
            result = subprocess.run([
                'pybabel', 'compile', '-d', str(translations_dir), 
                '-l', lang_code, '-i', str(po_file), '-o', str(mo_file)
            ], capture_output=True, text=True, cwd=str(base_dir))
            
            if result.returncode == 0:
                print(f"  ✓ Compiled {mo_file}")
            else:
                # Fallback: create a simple .mo file using msgfmt if available
                try:
                    subprocess.run(['msgfmt', str(po_file), '-o', str(mo_file)], 
                                 check=True, capture_output=True)
                    print(f"  ✓ Compiled {mo_file} (using msgfmt)")
                except:
                    print(f"  ⚠ Warning: Could not compile {mo_file} - you may need to install gettext tools")
        except FileNotFoundError:
            print(f"  ⚠ Warning: pybabel not found, skipping compilation for {lang_code}")
    
    print("\n✅ Translation setup completed!")
    print(f"Created translation files for {len(LANGUAGES)} languages")
    print("\nNote: If compilation failed, you can compile manually later using:")
    print("pybabel compile -d translations")

if __name__ == '__main__':
    main()
