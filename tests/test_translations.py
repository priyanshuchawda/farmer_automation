# test_translations.py
"""Test translation system"""

import sys
sys.path.append('C:\\Users\\Admin\\Desktop\\pccoe2')

from translations import en, hi, mr

print("=== Testing Translation System ===\n")

# Test English
print("English Translations:")
print(f"  Home: {en.TRANSLATIONS.get('Home')}")
print(f"  Good Morning: {en.TRANSLATIONS.get('Good Morning')}")
print(f"  Market Prices: {en.TRANSLATIONS.get('Market Prices')}")
print()

# Test Hindi
print("Hindi Translations:")
print(f"  Home: {hi.TRANSLATIONS.get('Home')}")
print(f"  Good Morning: {hi.TRANSLATIONS.get('Good Morning')}")
print(f"  Market Prices: {hi.TRANSLATIONS.get('Market Prices')}")
print()

# Test Marathi
print("Marathi Translations:")
print(f"  Home: {mr.TRANSLATIONS.get('Home')}")
print(f"  Good Morning: {mr.TRANSLATIONS.get('Good Morning')}")
print(f"  Market Prices: {mr.TRANSLATIONS.get('Market Prices')}")
print()

# Count translations
print(f"Total English translations: {len(en.TRANSLATIONS)}")
print(f"Total Hindi translations: {len(hi.TRANSLATIONS)}")
print(f"Total Marathi translations: {len(mr.TRANSLATIONS)}")
print()

print("✅ Translation system test complete!")
