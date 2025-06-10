#!/usr/bin/env python3
"""
Create minimal valid .mo files to prevent struct.error
"""

import struct
import os
from pathlib import Path

def create_minimal_mo_file(mo_file_path):
    """Create a minimal valid .mo file to avoid struct.error"""
    # MO file format: magic number + header
    magic = 0x950412de  # Little-endian magic number
    version = 0
    num_strings = 1  # At least one string to make it valid
    offset_strings = 28
    offset_translations = 32
    hash_size = 0
    hash_offset = 36
    
    # Simple string table (empty string)
    string_data = b'\x00'  # Empty string
    translation_data = b'\x00'  # Empty translation
    
    with open(mo_file_path, 'wb') as f:
        # Write header (7 * 4 = 28 bytes)
        f.write(struct.pack('<I', magic))
        f.write(struct.pack('<I', version))
        f.write(struct.pack('<I', num_strings))
        f.write(struct.pack('<I', offset_strings))
        f.write(struct.pack('<I', offset_translations))
        f.write(struct.pack('<I', hash_size))
        f.write(struct.pack('<I', hash_offset))
        
        # Write string offset table (4 bytes for length + offset)
        f.write(struct.pack('<I', 0))  # Length of string (0)
        f.write(struct.pack('<I', 36))  # Offset to string
        
        # Write translation offset table (4 bytes for length + offset)  
        f.write(struct.pack('<I', 0))  # Length of translation (0)
        f.write(struct.pack('<I', 37))  # Offset to translation
        
        # Write string data
        f.write(string_data)
        f.write(translation_data)

def main():
    """Fix all empty .mo files"""
    base_dir = Path.cwd()
    translations_dir = base_dir / 'translations'
    
    # Languages that need fixing (those with 0 byte .mo files)
    empty_mo_languages = ['da', 'en', 'fi', 'nl', 'no', 'pl', 'sv', 'th', 'tr']
    
    print("Creating minimal valid .mo files...")
    
    for lang_code in empty_mo_languages:
        mo_file = translations_dir / lang_code / 'LC_MESSAGES' / 'messages.mo'
        if mo_file.exists():
            # Check if file is empty or very small
            if mo_file.stat().st_size < 30:
                create_minimal_mo_file(mo_file)
                print(f"  ✓ Fixed {mo_file} (size: {mo_file.stat().st_size} bytes)")
        else:
            print(f"  ⚠ File not found: {mo_file}")
    
    print("\n✅ Fixed empty .mo files")

if __name__ == '__main__':
    main()
