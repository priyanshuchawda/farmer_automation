"""
Simplified Voice Chatbot - Minimal UI for home page integration
"""

import streamlit as st
from google import genai
import os
from streamlit_mic_recorder import mic_recorder
from components.translation_utils import t, get_current_language

def transcribe_voice(audio_bytes, language='en'):
    """Transcribe audio using Gemini"""
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return None
    
    try:
        client = genai.Client(api_key=api_key)
        
        # Upload audio
        audio_file = client.files.upload(path_or_bytes=audio_bytes, mime_type="audio/wav")
        
        # Transcribe
        model_name = "gemini-2.5-flash"
        prompt = f"Transcribe this audio accurately. Language: {language}"
        
        response = client.models.generate_content(
            model=model_name,
            contents=[prompt, audio_file]
        )
        
        if response and response.text:
            return response.text.strip()
    except Exception as e:
        st.error(f"Transcription error: {str(e)}")
    return None


def render_simple_voice_chatbot():
    """
    Minimal chatbot UI - just mic button and chat
    """
    
    # Minimal CSS
    st.markdown("""
    <style>
    .chat-message-user {
        background: #E3F2FD;
        padding: 12px;
        border-radius: 8px;
        margin: 8px 0;
        border-left: 3px solid #2196F3;
    }
    .chat-message-bot {
        background: #E8F5E9;
        padding: 12px;
        border-radius: 8px;
        margin: 8px 0;
        border-left: 3px solid #4CAF50;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Get API key
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        st.error("⚠️ AI API key not configured")
        return
    
    # Initialize Gemini client
    client = genai.Client(api_key=api_key)
    
    # Initialize chat history
    if 'simple_chat_history' not in st.session_state:
        st.session_state.simple_chat_history = []
    
    # Get farmer context
    farmer_name = st.session_state.get("farmer_name", "Farmer")
    farmer_profile = st.session_state.get("farmer_profile", {})
    location = farmer_profile.get('location', 'India')
    
    # Language
    language = get_current_language()
    selected_lang = st.session_state.get('language', 'English')
    
    # System prompt
    system_context = f"""You are an expert agricultural advisor for Indian farmers.
Farmer: {farmer_name}, Location: {location}
Language: Reply in {selected_lang}
Be concise (3-5 sentences), practical, and provide actionable advice."""
    
    # Voice Input Section
    st.markdown("### 🎤 Voice Input")
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        audio = mic_recorder(
            start_prompt="🔴 Start Recording",
            stop_prompt="⏹️ Stop Recording",
            just_once=False,
            width="stretch",
            key="simple_mic"
        )
    
    with col2:
        lang_code = st.selectbox(
            "Lang",
            ["en", "hi", "mr"],
            format_func=lambda x: {"en": "EN", "hi": "HI", "mr": "MR"}[x],
            key="simple_lang",
            label_visibility="collapsed"
        )
    
    # Process audio
    if audio and st.button("🤖 Process Voice", width="stretch", type="primary"):
        with st.spinner("Converting speech..."):
            transcribed = transcribe_voice(audio['bytes'], lang_code)
            if transcribed:
                st.success(f"📝 You said: {transcribed}")
                st.session_state.pending_voice_message = transcribed
                st.rerun()
    
    st.markdown("---")
    
    # Chat Display
    if st.session_state.simple_chat_history:
        for msg in st.session_state.simple_chat_history:
            if msg["role"] == "user":
                st.markdown(f"""
                <div class='chat-message-user'>
                    <strong>🧑‍🌾 You:</strong> {msg["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class='chat-message-bot'>
                    <strong>🤖 Advisor:</strong> {msg["content"]}
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info(f"👋 Hello {farmer_name}! Ask me anything about farming.")
    
    st.markdown("---")
    
    # Text Input
    st.markdown("### ⌨️ Type Your Question")
    
    default_text = st.session_state.pop('pending_voice_message', '')
    
    user_input = st.text_area(
        "Your question:",
        value=default_text,
        height=80,
        placeholder="E.g., Best crops for monsoon season?",
        key="simple_chat_input"
    )
    
    col_send, col_clear = st.columns([3, 1])
    
    with col_send:
        if st.button("📤 Send", width="stretch", type="primary") and user_input.strip():
            # Add user message
            st.session_state.simple_chat_history.append({
                "role": "user",
                "content": user_input
            })
            
            # Get AI response
            with st.spinner("🤖 AI is thinking..."):
                try:
                    # Build conversation history
                    contents = [system_context]
                    for msg in st.session_state.simple_chat_history:
                        contents.append(f"{msg['role']}: {msg['content']}")
                    
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents="\n".join(contents)
                    )
                    
                    if response and response.text:
                        st.session_state.simple_chat_history.append({
                            "role": "assistant",
                            "content": response.text
                        })
                    
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with col_clear:
        if st.button("🗑️ Clear", width="stretch"):
            st.session_state.simple_chat_history = []
            st.rerun()
