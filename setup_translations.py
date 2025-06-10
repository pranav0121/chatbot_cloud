#!/usr/bin/env python3
"""
Translation setup script for Flask-Babel
"""
import os
from babel.messages import Catalog
from babel.messages.pofile import write_po
from babel.messages.mofile import write_mo

# Create translation directories and files
languages = ['es', 'fr', 'de']

for lang in languages:
    # Create directory structure
    lang_dir = f'translations/{lang}/LC_MESSAGES'
    os.makedirs(lang_dir, exist_ok=True)
    
    # Create catalog
    catalog = Catalog(locale=lang)
    
    # Add common translations
    if lang == 'es':  # Spanish
        translations = {
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
            'Language selection': 'Selección de idioma'
        }
    elif lang == 'fr':  # French
        translations = {
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
            'Language selection': 'Sélection de langue'
        }
    elif lang == 'de':  # German
        translations = {
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
            'Language selection': 'Sprachauswahl'
        }
    
    # Add translations to catalog
    for msgid, msgstr in translations.items():
        catalog.add(msgid, string=msgstr)
    
    # Write PO file
    po_path = f'{lang_dir}/messages.po'
    with open(po_path, 'wb') as f:
        write_po(f, catalog)
    
    # Compile to MO file
    mo_path = f'{lang_dir}/messages.mo'
    with open(mo_path, 'wb') as f:
        write_mo(f, catalog)
    
    print(f"Created translation files for {lang}")

print("Translation setup complete!")
