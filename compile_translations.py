#!/usr/bin/env python3
"""
Compile translation files from .po to .mo
"""
import os
from babel.messages.mofile import write_mo
from babel.messages.pofile import read_po

languages = ['es', 'fr', 'de']

for lang in languages:
    po_path = f'translations/{lang}/LC_MESSAGES/messages.po'
    mo_path = f'translations/{lang}/LC_MESSAGES/messages.mo'
    
    if os.path.exists(po_path):
        # Read PO file
        with open(po_path, 'rb') as f:
            catalog = read_po(f)
        
        # Write MO file
        with open(mo_path, 'wb') as f:
            write_mo(f, catalog)
        
        print(f"Compiled {lang}: {po_path} -> {mo_path}")
    else:
        print(f"PO file not found: {po_path}")

print("Compilation complete!")
