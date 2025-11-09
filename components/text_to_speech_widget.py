# components/text_to_speech_widget.py
"""
Text-to-Speech Widget - Read any text aloud in user's selected language
Perfect for farmers with low literacy
"""

import streamlit as st
from gtts import gTTS
from io import BytesIO
import base64
from components.translation_utils import get_current_language

def text_to_audio(text, language='en'):
    """
    Convert text to audio bytes
    
    Args:
        text: Text to convert
        language: Language code ('en', 'hi', 'mr')
    
    Returns:
        Audio bytes
    """
    try:
        # Create text-to-speech
        tts = gTTS(text=text, lang=language, slow=False)
        
        # Save to bytes
        audio_bytes = BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        
        return audio_bytes.getvalue()
    except Exception as e:
        st.error(f"Error generating audio: {e}")
        return None


def create_audio_player_html(audio_bytes, autoplay=False):
    """
    Create HTML audio player with base64 encoded audio
    
    Args:
        audio_bytes: Audio data
        autoplay: Whether to autoplay
    
    Returns:
        HTML string
    """
    b64_audio = base64.b64encode(audio_bytes).decode()
    autoplay_attr = 'autoplay' if autoplay else ''
    
    html = f"""
    <audio controls {autoplay_attr} style="width: 100%; margin: 10px 0;">
        <source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3">
        Your browser does not support the audio element.
    </audio>
    """
    return html


def speak_button(text, button_text="🔊 Listen", language=None, key_suffix=""):
    """
    Create a button that speaks the given text when clicked
    
    Args:
        text: Text to speak
        button_text: Button label
        language: Language code (if None, uses current app language)
        key_suffix: Unique suffix for button key
    
    Returns:
        True if button was clicked
    """
    if language is None:
        language = get_current_language()
    
    if st.button(button_text, key=f"speak_btn_{key_suffix}", width="content"):
        with st.spinner("🎵 Generating audio..."):
            audio_bytes = text_to_audio(text, language)
        
        if audio_bytes:
            # Display audio player
            st.audio(audio_bytes, format='audio/mp3')
            return True
    
    return False


def auto_speak(text, language=None, show_controls=True):
    """
    Automatically speak text with audio controls displayed
    
    Args:
        text: Text to speak
        language: Language code
        show_controls: Whether to show audio controls
    """
    if language is None:
        language = get_current_language()
    
    audio_bytes = text_to_audio(text, language)
    
    if audio_bytes:
        if show_controls:
            st.audio(audio_bytes, format='audio/mp3')
        else:
            # Hidden autoplay audio
            html = create_audio_player_html(audio_bytes, autoplay=True)
            st.markdown(html, unsafe_allow_html=True)


def render_read_aloud_panel(texts_to_read, language=None):
    """
    Render a panel with multiple text items that can be read aloud
    
    Args:
        texts_to_read: Dictionary with {label: text} pairs
        language: Language code
    """
    if language is None:
        language = get_current_language()
    
    st.markdown("""
    <style>
    .read-aloud-panel {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .read-item {
        display: flex;
        align-items: center;
        margin: 8px 0;
        padding: 8px;
        background: white;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🔊 Read Aloud")
    
    for label, text in texts_to_read.items():
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"**{label}**")
        with col2:
            speak_button(text, "🔊", language, key_suffix=label.replace(" ", "_"))


def add_listen_everywhere():
    """
    Add a global 'Listen' toggle that reads page content aloud
    Should be called on every page
    """
    # Add to sidebar
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🔊 Listen Mode")
        
        # Toggle for auto-read
        auto_read = st.toggle(
            "🔊 Auto-read content", 
            value=st.session_state.get('auto_read_mode', False),
            key="auto_read_toggle",
            help="Automatically read page content aloud"
        )
        
        if auto_read != st.session_state.get('auto_read_mode', False):
            st.session_state.auto_read_mode = auto_read
            st.rerun()


def speak_text_block(text, title=None, language=None, auto_play=False):
    """
    Display a text block with a listen button
    Perfect for important information, instructions, or alerts
    
    Args:
        text: Text to display and speak
        title: Optional title
        language: Language code
        auto_play: Whether to auto-play on render
    """
    if language is None:
        language = get_current_language()
    
    # Create container
    with st.container():
        if title:
            st.markdown(f"**{title}**")
        
        col1, col2 = st.columns([5, 1])
        
        with col1:
            st.write(text)
        
        with col2:
            if st.button("🔊", key=f"speak_{hash(text)}", help="Listen"):
                with st.spinner("🎵"):
                    audio_bytes = text_to_audio(text, language)
                    if audio_bytes:
                        st.audio(audio_bytes, format='audio/mp3')
        
        # Auto-play if enabled
        if auto_play or st.session_state.get('auto_read_mode', False):
            audio_bytes = text_to_audio(text, language)
            if audio_bytes:
                html = create_audio_player_html(audio_bytes, autoplay=True)
                st.markdown(html, unsafe_allow_html=True)


def add_page_narrator():
    """
    Add a prominent "Read Page" button at the top of every page
    Reads the page title and main instructions aloud
    """
    page_title = st.session_state.get('selected_menu', 'Home')
    language = get_current_language()
    
    # Create a prominent banner at the top
    st.markdown("""
    <style>
    .listen-banner {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 10px 20px;
        border-radius: 10px;
        margin-bottom: 15px;
        text-align: center;
        color: white;
    }
    
    @media (max-width: 768px) {
        .listen-banner {
            padding: 8px 15px;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Read page button at top
    col1, col2, col3 = st.columns([2, 6, 2])
    
    with col2:
        if st.button(f"🔊 Listen to this page", key="read_page_btn", width="stretch", type="secondary"):
            # Create descriptive text based on page
            descriptions = {
                "🏠 Home": f"Welcome to your home dashboard. You can see today's tasks, weather updates, and quick actions here.",
                "🌤️ Weather Forecast": f"Weather forecast page. Here you can check current weather, five day forecast, and farming recommendations.",
                "💰 Market Prices": f"Market prices page. Check current vegetable and crop prices in different markets.",
                "📅 Farming Calendar": f"Farming calendar. View and manage your farming tasks and activities.",
                "👤 My Profile": f"Your profile page. View and edit your personal information and farm details.",
                "🛍️ Browse Listings": f"Marketplace. Browse tools and crops available for rent or sale.",
                "🎤 Voice Assistant": f"Voice assistant. Speak your commands to navigate the app hands-free.",
            }
            
            text_to_speak = descriptions.get(page_title, f"You are on {page_title} page")
            
            with st.spinner("🎵 Preparing audio..."):
                audio_bytes = text_to_audio(text_to_speak, language)
                if audio_bytes:
                    st.audio(audio_bytes, format='audio/mp3', autoplay=True)
