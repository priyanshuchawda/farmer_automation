# components/translation_utils.py
"""
Multi-language translation utility for Farmer Market System
Hybrid system: Manual translations + Deep Translator fallback
"""

import streamlit as st
import importlib
from deep_translator import GoogleTranslator
from functools import lru_cache

# Supported Languages
LANGUAGES = {
    "English": "en",
    "हिन्दी (Hindi)": "hi",
    "मराठी (Marathi)": "mr",
}

# Load translation dictionaries
def load_translations(lang_code):
    """Load translation dictionary for given language"""
    try:
        module = importlib.import_module(f'translations.{lang_code}')
        return module.TRANSLATIONS
    except Exception as e:
        return {}

@lru_cache(maxsize=1000)
def auto_translate(text, target_lang):
    """
    Automatically translate text using deep-translator
    Cached to avoid repeated API calls
    """
    if not text or text.strip() == "":
        return text
    
    try:
        translator = GoogleTranslator(source='en', target=target_lang)
        
        # Split long text into chunks if needed
        max_length = 4500
        if len(text) > max_length:
            chunks = [text[i:i+max_length] for i in range(0, len(text), max_length)]
            translated_chunks = [translator.translate(chunk) for chunk in chunks]
            return " ".join(translated_chunks)
        else:
            return translator.translate(text)
    except Exception as e:
        # If translation fails, return original text
        return text

def t(text, use_auto=True):
    """
    Hybrid translation: Manual translations first, then auto-translate fallback
    
    Args:
        text: Text to translate (English text)
        use_auto: Whether to use auto-translation for missing translations (default: True)
    
    Returns:
        Translated text based on selected language
    """
    if not text:
        return text
    
    # Get selected language from session state
    selected_lang = st.session_state.get('language', 'English')
    lang_code = LANGUAGES.get(selected_lang, 'en')
    
    # If English, return as-is
    if lang_code == 'en':
        return text
    
    # Step 1: Try manual translation from predefined files
    translations = load_translations(lang_code)
    manual_translation = translations.get(text)
    
    if manual_translation:
        # Manual translation found - use it
        return manual_translation
    
    # Step 2: If not found and auto-translation enabled, use deep-translator
    if use_auto:
        return auto_translate(text, lang_code)
    
    # Step 3: If auto-translation disabled, return original
    return text

def get_current_language():
    """
    Get current selected language code
    
    Returns:
        Language code ('en', 'hi', 'mr')
    """
    selected_lang = st.session_state.get('language', 'English')
    return LANGUAGES.get(selected_lang, 'en')

def get_current_language_name():
    """
    Get current selected language name in English
    
    Returns:
        Language name ('English', 'Hindi', 'Marathi')
    """
    selected_lang = st.session_state.get('language', 'English')
    # Extract just the English name
    if 'Hindi' in selected_lang:
        return 'Hindi'
    elif 'Marathi' in selected_lang:
        return 'Marathi'
    else:
        return 'English'

def render_language_selector():
    """Render language selector at top of sidebar"""
    with st.sidebar:
        st.markdown("### 🌐 Language / भाषा")
        
        # Initialize language in session state
        if 'language' not in st.session_state:
            st.session_state.language = 'English'
        
        # Language selector
        selected_language = st.selectbox(
            "भाषा निवडा / Select Language",
            options=list(LANGUAGES.keys()),
            index=list(LANGUAGES.keys()).index(st.session_state.language),
            key="language_selector",
            label_visibility="collapsed"
        )
        
        # Update session state if language changed
        if selected_language != st.session_state.language:
            st.session_state.language = selected_language
            st.rerun()

def translate_dataframe_columns(df, columns_to_translate):
    """
    Translate specific columns in a pandas DataFrame
    
    Args:
        df: DataFrame to translate
        columns_to_translate: List of column names to translate
    
    Returns:
        DataFrame with translated columns
    """
    import pandas as pd
    
    if df.empty:
        return df
    
    df_copy = df.copy()
    
    for col in columns_to_translate:
        if col in df_copy.columns:
            df_copy[col] = df_copy[col].apply(lambda x: t(str(x)) if pd.notna(x) else x)
    
    return df_copy

def format_date_localized(date_obj, format_pattern='%B %d, %Y'):
    """
    Format date with translated month names
    
    Args:
        date_obj: datetime object
        format_pattern: strftime format pattern (default: '%B %d, %Y')
    
    Returns:
        Formatted date string with translated month name
    """
    from datetime import datetime
    
    # Get the formatted date in English
    english_date = date_obj.strftime(format_pattern)
    
    # Extract month name from the formatted date
    month_name = date_obj.strftime('%B')
    
    # Translate the month name
    translated_month = t(month_name)
    
    # Replace English month with translated month
    localized_date = english_date.replace(month_name, translated_month)
    
    return localized_date

def convert_numbers_to_local(text):
    """
    Convert English numerals to Hindi/Marathi Devanagari numerals
    
    Args:
        text: String containing English numbers
    
    Returns:
        String with converted numerals based on selected language
    """
    lang_code = get_current_language()
    
    # Only convert for Hindi and Marathi
    if lang_code not in ['hi', 'mr']:
        return text
    
    # Mapping of English to Devanagari numerals
    number_map = {
        '0': '०', '1': '१', '2': '२', '3': '३', '4': '४',
        '5': '५', '6': '६', '7': '७', '8': '८', '9': '९'
    }
    
    result = text
    for eng, dev in number_map.items():
        result = result.replace(eng, dev)
    
    return result

def translate_location(location):
    """
    Translate location keywords and transliterate place names to local script
    
    Args:
        location: Full address string
    
    Returns:
        Address with translated keywords and transliterated place names
    """
    lang_code = get_current_language()
    
    # If English, return as-is
    if lang_code == 'en':
        return location
    
    # Keywords and place names to translate/transliterate
    # Order matters - translate longer phrases first
    items_to_translate = [
        "Phoenix Marketcity",
        "Upper Ground Floor",
        "Ground Floor", 
        "Clover Park",
        "Viman Nagar",
        "Maharashtra",
        "Unit No",
        "S No",
        "India",
        "Pune",
    ]
    
    translated_location = location
    for item in items_to_translate:
        translated_item = t(item)
        translated_location = translated_location.replace(item, translated_item)
    
    # Convert numbers to local numerals
    translated_location = convert_numbers_to_local(translated_location)
    
    return translated_location
