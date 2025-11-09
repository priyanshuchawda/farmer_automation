# components/voice_button.py
"""
Floating voice button component that appears on all pages
Provides quick access to voice input from anywhere in the app
"""

import streamlit as st
from components.translation_utils import t, get_current_language
from components.voice_assistant import VoiceAssistant

def render_floating_voice_button():
    """
    Render a floating voice button in the bottom-right corner
    This appears on all pages for quick voice access
    """
    
    # CSS for floating button
    st.markdown("""
    <style>
    .floating-voice-btn {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 1000;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 50%;
        width: 60px;
        height: 60px;
        font-size: 28px;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .floating-voice-btn:hover {
        transform: scale(1.1);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
    }
    
    .voice-pulse {
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% {
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }
        50% {
            box-shadow: 0 4px 20px rgba(102, 126, 234, 0.6);
        }
        100% {
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }
    }
    
    /* Mobile adjustments */
    @media (max-width: 768px) {
        .floating-voice-btn {
            width: 50px;
            height: 50px;
            font-size: 24px;
            bottom: 15px;
            right: 15px;
        }
    }
    
    /* Voice modal */
    .voice-modal {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: white;
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
        z-index: 2000;
        min-width: 400px;
        max-width: 90vw;
    }
    
    .voice-modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        z-index: 1999;
    }
    
    @media (max-width: 768px) {
        .voice-modal {
            min-width: 90vw;
            padding: 20px;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Check if voice modal should be shown
    if 'show_voice_modal' not in st.session_state:
        st.session_state.show_voice_modal = False
    
    # Floating button (always visible)
    col1, col2, col3 = st.columns([8, 1, 1])
    
    with col3:
        if st.button("🎤", key="floating_voice_btn", help=t("Voice Assistant"), width="stretch"):
            st.session_state.show_voice_modal = True
            st.rerun()


def render_voice_quick_input():
    """
    Render a compact voice input widget that can be embedded in any page
    """
    language = get_current_language()
    assistant = VoiceAssistant()
    
    st.markdown(f"### 🎤 {t('Quick Voice Input')}")
    
    with st.expander(f"🗣️ {t('Click to speak')}", expanded=False):
        st.caption(t("Speak your command or question"))
        
        try:
            from streamlit_mic_recorder import mic_recorder
            
            # Compact voice recorder
            audio = mic_recorder(
                start_prompt="🎙️",
                stop_prompt="⏹️",
                just_once=False,
                width="stretch",
                format="wav",
                key=f"quick_voice_{st.session_state.get('quick_voice_counter', 0)}"
            )
            
            if audio:
                with st.spinner(t("Processing...")):
                    text = assistant.recognize_speech_from_audio(audio['bytes'], language)
                
                if text:
                    st.success(f"✅ {text}")
                    
                    # Process command
                    command = assistant.process_voice_command(text, language)
                    
                    if command['action'] != 'search':
                        # Show action button
                        action_map = {
                            'weather': ('🌤️ Weather Forecast', "🌤️ Weather Forecast"),
                            'price': ('💰 Market Prices', "💰 Market Prices"),
                            'calendar': ('📅 Farming Calendar', "📅 Farming Calendar"),
                            'profile': ('👤 My Profile', "👤 My Profile"),
                            'list_tool': ('➕ Create New Listing', "➕ Create New Listing"),
                            'list_crop': ('➕ Create New Listing', "➕ Create New Listing"),
                        }
                        
                        if command['action'] in action_map:
                            button_text, menu_item = action_map[command['action']]
                            if st.button(f"➡️ {t('Go to')} {button_text}", width="stretch"):
                                st.session_state.nav_history.append(st.session_state.selected_menu)
                                st.session_state.nav_forward = []
                                st.session_state.selected_menu = menu_item
                                st.rerun()
                else:
                    st.error(t("Could not understand. Try again."))
        
        except ImportError:
            st.info(t("Voice feature requires additional setup. Go to 🎤 Voice Assistant page."))


def add_voice_shortcuts():
    """
    Add voice shortcuts to sidebar
    Shows quick voice commands available
    """
    with st.sidebar:
        with st.expander(f"🎤 {t('Voice Shortcuts')}", expanded=False):
            st.markdown(f"""
            **{t('Say')}:**
            - "{t('Show weather forecast')}"
            - "{t('Market prices')}"
            - "{t('My profile')}"
            - "{t('Open calendar')}"
            
            ➡️ {t('Or go to')} **{t('Voice Assistant')}** {t('page')}
            """)
            
            if st.button(f"🎤 {t('Open Voice Assistant')}", width="stretch", key="sidebar_voice"):
                st.session_state.nav_history.append(st.session_state.selected_menu)
                st.session_state.nav_forward = []
                st.session_state.selected_menu = "🎤 Voice Assistant"
                st.rerun()
