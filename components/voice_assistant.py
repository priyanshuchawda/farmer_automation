# components/voice_assistant.py
"""
Voice Assistant for Smart Farmer Marketplace
Supports voice commands, voice search, and audio responses in English, Hindi, and Marathi
"""

import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import tempfile
import os
from io import BytesIO
from components.translation_utils import t, get_current_language

class VoiceAssistant:
    """Voice assistant with multilingual support"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.supported_languages = {
            'en': 'en-IN',  # English (India)
            'hi': 'hi-IN',  # Hindi (India)
            'mr': 'mr-IN'   # Marathi (India)
        }
    
    def recognize_speech_from_audio(self, audio_data, language='en'):
        """
        Convert speech audio to text
        
        Args:
            audio_data: Audio bytes
            language: Language code ('en', 'hi', 'mr')
        
        Returns:
            Recognized text or None
        """
        try:
            # Get the appropriate language code
            lang_code = self.supported_languages.get(language, 'en-IN')
            
            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                tmp_file.write(audio_data)
                tmp_file_path = tmp_file.name
            
            # Load audio file
            with sr.AudioFile(tmp_file_path) as source:
                audio = self.recognizer.record(source)
            
            # Recognize speech using Google
            text = self.recognizer.recognize_google(audio, language=lang_code)
            
            # Clean up temporary file
            os.unlink(tmp_file_path)
            
            return text
        
        except sr.UnknownValueError:
            return None  # Could not understand audio
        except sr.RequestError as e:
            st.error(f"Could not request results; {e}")
            return None
        except Exception as e:
            st.error(f"Error recognizing speech: {e}")
            return None
    
    def text_to_speech(self, text, language='en'):
        """
        Convert text to speech audio
        
        Args:
            text: Text to convert
            language: Language code ('en', 'hi', 'mr')
        
        Returns:
            Audio bytes
        """
        try:
            # Get the appropriate language code
            lang_code = self.supported_languages.get(language, 'en-IN')
            
            # Create text-to-speech
            tts = gTTS(text=text, lang=lang_code.split('-')[0], slow=False)
            
            # Save to bytes
            audio_bytes = BytesIO()
            tts.write_to_fp(audio_bytes)
            audio_bytes.seek(0)
            
            return audio_bytes.getvalue()
        
        except Exception as e:
            st.error(f"Error generating speech: {e}")
            return None
    
    def process_voice_command(self, command_text, language='en'):
        """
        Process voice command and return action
        
        Args:
            command_text: Command text from voice
            language: Language code
        
        Returns:
            Dictionary with action and parameters
        """
        command_lower = command_text.lower()
        
        # English commands
        if language == 'en':
            if 'weather' in command_lower:
                return {'action': 'weather', 'text': command_text}
            elif 'price' in command_lower or 'market' in command_lower:
                return {'action': 'price', 'text': command_text}
            elif 'calendar' in command_lower or 'schedule' in command_lower:
                return {'action': 'calendar', 'text': command_text}
            elif 'list tool' in command_lower or 'rent tool' in command_lower:
                return {'action': 'list_tool', 'text': command_text}
            elif 'list crop' in command_lower or 'sell crop' in command_lower:
                return {'action': 'list_crop', 'text': command_text}
            elif 'profile' in command_lower:
                return {'action': 'profile', 'text': command_text}
            elif 'help' in command_lower:
                return {'action': 'help', 'text': command_text}
        
        # Hindi commands (हिंदी)
        elif language == 'hi':
            if 'मौसम' in command_lower or 'weather' in command_lower:
                return {'action': 'weather', 'text': command_text}
            elif 'कीमत' in command_lower or 'मंडी' in command_lower or 'price' in command_lower:
                return {'action': 'price', 'text': command_text}
            elif 'कैलेंडर' in command_lower or 'calendar' in command_lower:
                return {'action': 'calendar', 'text': command_text}
            elif 'औजार' in command_lower or 'tool' in command_lower:
                return {'action': 'list_tool', 'text': command_text}
            elif 'फसल' in command_lower or 'crop' in command_lower:
                return {'action': 'list_crop', 'text': command_text}
            elif 'प्रोफाइल' in command_lower or 'profile' in command_lower:
                return {'action': 'profile', 'text': command_text}
            elif 'मदद' in command_lower or 'help' in command_lower:
                return {'action': 'help', 'text': command_text}
        
        # Marathi commands (मराठी)
        elif language == 'mr':
            if 'हवामान' in command_lower or 'weather' in command_lower:
                return {'action': 'weather', 'text': command_text}
            elif 'किंमत' in command_lower or 'बाजार' in command_lower or 'price' in command_lower:
                return {'action': 'price', 'text': command_text}
            elif 'calendar' in command_lower or 'दिनदर्शिका' in command_lower:
                return {'action': 'calendar', 'text': command_text}
            elif 'साधन' in command_lower or 'tool' in command_lower:
                return {'action': 'list_tool', 'text': command_text}
            elif 'पीक' in command_lower or 'crop' in command_lower:
                return {'action': 'list_crop', 'text': command_text}
            elif 'प्रोफाइल' in command_lower or 'profile' in command_lower:
                return {'action': 'profile', 'text': command_text}
            elif 'मदत' in command_lower or 'help' in command_lower:
                return {'action': 'help', 'text': command_text}
        
        # Default: search or AI query
        return {'action': 'search', 'text': command_text}


def render_voice_input(placeholder="Speak your question...", language=None):
    """
    Render voice input component
    
    Args:
        placeholder: Placeholder text
        language: Language code (if None, uses current app language)
    
    Returns:
        Recognized text or None
    """
    if language is None:
        language = get_current_language()
    
    assistant = VoiceAssistant()
    
    st.markdown(f"""
    <style>
    .voice-container {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin: 20px 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }}
    .voice-icon {{
        font-size: 48px;
        margin: 10px 0;
    }}
    .voice-text {{
        color: white;
        font-size: 18px;
        font-weight: 600;
    }}
    </style>
    """, unsafe_allow_html=True)
    
    # Use streamlit-mic-recorder for browser-based recording
    try:
        from streamlit_mic_recorder import mic_recorder
        
        st.markdown(f"### 🎤 {t('Voice Input')}")
        st.caption(t("Click the microphone and speak in") + f" {t('English')}, {t('Hindi')} " + t('or') + f" {t('Marathi')}")
        
        # Record audio
        audio = mic_recorder(
            start_prompt=t("🎙️ Start Recording"),
            stop_prompt=t("⏹️ Stop Recording"),
            just_once=False,
            use_container_width=True,
            format="wav",
            callback=None,
            args=(),
            kwargs={},
            key="voice_recorder"
        )
        
        if audio:
            st.success(t("Audio recorded! Processing..."))
            
            # Process the audio
            with st.spinner(t("Converting speech to text...")):
                text = assistant.recognize_speech_from_audio(audio['bytes'], language)
            
            if text:
                st.success(f"✅ {t('You said')}: **{text}**")
                return text
            else:
                st.error(t("Sorry, could not understand. Please try again."))
                return None
    
    except ImportError:
        st.warning(t("Voice recording package not installed. Please install streamlit-mic-recorder."))
        
        # Fallback: File upload
        st.info(t("Alternative: Upload an audio file"))
        audio_file = st.file_uploader(t("Upload audio (WAV format)"), type=['wav'], key="audio_upload")
        
        if audio_file:
            with st.spinner(t("Processing audio...")):
                audio_bytes = audio_file.read()
                text = assistant.recognize_speech_from_audio(audio_bytes, language)
            
            if text:
                st.success(f"✅ {t('Recognized')}: **{text}**")
                return text
            else:
                st.error(t("Could not understand audio"))
                return None
    
    return None


def speak_text(text, language=None, auto_play=True):
    """
    Convert text to speech and play it
    
    Args:
        text: Text to speak
        language: Language code (if None, uses current app language)
        auto_play: Whether to auto-play the audio
    """
    if language is None:
        language = get_current_language()
    
    assistant = VoiceAssistant()
    
    with st.spinner(t("Generating audio...")):
        audio_bytes = assistant.text_to_speech(text, language)
    
    if audio_bytes:
        st.audio(audio_bytes, format='audio/mp3', autoplay=auto_play)
        return True
    
    return False


def render_voice_assistant_page():
    """Render the voice assistant page"""
    
    st.header(f"🎤 {t('Voice Assistant')}")
    
    # Mobile responsive CSS
    st.markdown("""
    <style>
    @media (max-width: 768px) {
        .voice-container {
            padding: 15px !important;
        }
        .voice-icon {
            font-size: 36px !important;
        }
        .voice-text {
            font-size: 16px !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    language = get_current_language()
    
    st.markdown(f"""
    <div class='voice-container'>
        <div class='voice-icon'>🗣️</div>
        <div class='voice-text'>{t('Speak to interact with the app')}</div>
        <div style='color: rgba(255,255,255,0.9); margin-top: 10px;'>
            {t('Supported')}: {t('English')} | {t('Hindi')} | {t('Marathi')}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Information box
    st.info(f"""
    **{t('How to use')}:**
    
    1. 🎙️ {t('Click the microphone button')}
    2. 🗣️ {t('Speak your command or question')}
    3. ⏹️ {t('Click stop when done')}
    4. ✨ {t('The app will respond')}
    
    **{t('Example commands')}:**
    - "{t('Show weather forecast')}"
    - "{t('What is tomato price in Pune?')}"
    - "{t('Add task to calendar')}"
    - "{t('List my crops')}"
    - "{t('Show my profile')}"
    """)
    
    # Voice input
    voice_text = render_voice_input(language=language)
    
    if voice_text:
        # Process the command
        assistant = VoiceAssistant()
        command = assistant.process_voice_command(voice_text, language)
        
        st.divider()
        st.subheader(f"📋 {t('Command Recognized')}")
        st.write(f"**{t('Action')}:** {command['action']}")
        st.write(f"**{t('Text')}:** {command['text']}")
        
        # Execute action
        if command['action'] == 'weather':
            response_text = t("Opening weather forecast...")
            speak_text(response_text, language, auto_play=False)
            
            if st.button(f"🌤️ {t('Go to Weather')}", use_container_width=True, type="primary"):
                st.session_state.nav_history.append(st.session_state.selected_menu)
                st.session_state.nav_forward = []
                st.session_state.selected_menu = "🌤️ Weather Forecast"
                st.rerun()
        
        elif command['action'] == 'price':
            response_text = t("Opening market prices...")
            speak_text(response_text, language, auto_play=False)
            
            if st.button(f"💰 {t('Go to Market Prices')}", use_container_width=True, type="primary"):
                st.session_state.nav_history.append(st.session_state.selected_menu)
                st.session_state.nav_forward = []
                st.session_state.selected_menu = "💰 Market Prices"
                st.rerun()
        
        elif command['action'] == 'calendar':
            response_text = t("Opening farming calendar...")
            speak_text(response_text, language, auto_play=False)
            
            if st.button(f"📅 {t('Go to Calendar')}", use_container_width=True, type="primary"):
                st.session_state.nav_history.append(st.session_state.selected_menu)
                st.session_state.nav_forward = []
                st.session_state.selected_menu = "📅 Farming Calendar"
                st.rerun()
        
        elif command['action'] == 'profile':
            response_text = t("Opening your profile...")
            speak_text(response_text, language, auto_play=False)
            
            if st.button(f"👤 {t('Go to Profile')}", use_container_width=True, type="primary"):
                st.session_state.nav_history.append(st.session_state.selected_menu)
                st.session_state.nav_forward = []
                st.session_state.selected_menu = "👤 My Profile"
                st.rerun()
        
        elif command['action'] == 'list_tool':
            response_text = t("Opening tool listing form...")
            speak_text(response_text, language, auto_play=False)
            
            if st.button(f"🔧 {t('Go to Tool Listing')}", use_container_width=True, type="primary"):
                st.session_state.nav_history.append(st.session_state.selected_menu)
                st.session_state.nav_forward = []
                st.session_state.selected_menu = "➕ Create New Listing"
                st.rerun()
        
        elif command['action'] == 'list_crop':
            response_text = t("Opening crop listing form...")
            speak_text(response_text, language, auto_play=False)
            
            if st.button(f"🌾 {t('Go to Crop Listing')}", use_container_width=True, type="primary"):
                st.session_state.nav_history.append(st.session_state.selected_menu)
                st.session_state.nav_forward = []
                st.session_state.selected_menu = "➕ Create New Listing"
                st.rerun()
        
        elif command['action'] == 'help':
            response_text = t("Here are the available features...")
            speak_text(response_text, language, auto_play=False)
            
            st.success(f"""
            **{t('Available Features')}:**
            
            - 🌤️ {t('Weather Forecast')}
            - 💰 {t('Market Prices')}
            - 📅 {t('Farming Calendar')}
            - 🛍️ {t('Marketplace')}
            - 👤 {t('Profile Management')}
            - 🤖 {t('AI Chatbot')}
            - 🗺️ {t('Location Services')}
            """)
        
        else:
            # Search or AI query
            response_text = t("Searching for") + f": {voice_text}"
            speak_text(response_text, language, auto_play=False)
            
            st.info(f"🔍 {t('Search results for')}: **{voice_text}**")
            st.write(t("This would search across all features..."))
    
    # Tips section
    st.divider()
    st.markdown(f"### 💡 {t('Voice Tips')}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        **✅ {t('Good Practices')}:**
        - {t('Speak clearly and slowly')}
        - {t('Use simple commands')}
        - {t('Reduce background noise')}
        - {t('Hold phone close to mouth')}
        """)
    
    with col2:
        st.markdown(f"""
        **❌ {t('Avoid')}:**
        - {t('Very long sentences')}
        - {t('Speaking too fast')}
        - {t('Noisy environments')}
        - {t('Speaking from far away')}
        """)
