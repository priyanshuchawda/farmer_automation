"""
Voice-Enabled AI Chatbot for Farmers
Combines AI chatbot with voice input/output functionality
Supports Hindi, Marathi, and English with mic recording
Includes location-aware features with Google Maps grounding
"""

import streamlit as st
from google import genai
from google.genai import types
import os
from datetime import datetime
from streamlit_mic_recorder import mic_recorder
from components.translation_utils import t, get_current_language
import requests

def get_location_from_coordinates(lat, lon, api_key=None):
    """
    Reverse geocode coordinates to get location name using Google Maps API
    
    Args:
        lat: Latitude
        lon: Longitude
        api_key: Google Maps API key (optional, uses Gemini key if not provided)
    
    Returns:
        dict with location info or None
    """
    try:
        # Try Google Maps Geocoding API if key is available
        if not api_key:
            api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        
        if api_key:
            url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lon}&key={api_key}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('results'):
                    result = data['results'][0]
                    
                    # Extract useful components
                    components = {}
                    for comp in result.get('address_components', []):
                        types_list = comp.get('types', [])
                        if 'locality' in types_list:
                            components['city'] = comp['long_name']
                        elif 'administrative_area_level_2' in types_list:
                            components['district'] = comp['long_name']
                        elif 'administrative_area_level_1' in types_list:
                            components['state'] = comp['long_name']
                        elif 'country' in types_list:
                            components['country'] = comp['long_name']
                    
                    return {
                        'formatted_address': result.get('formatted_address'),
                        'city': components.get('city', ''),
                        'district': components.get('district', ''),
                        'state': components.get('state', ''),
                        'country': components.get('country', ''),
                        'lat': lat,
                        'lon': lon
                    }
        
        # Fallback: use basic description
        return {
            'formatted_address': f"{lat:.4f}, {lon:.4f}",
            'lat': lat,
            'lon': lon
        }
    
    except Exception as e:
        st.warning(f"Location lookup failed: {str(e)}")
        return None


def transcribe_voice_to_text(audio_bytes, language='en'):
    """
    Transcribe audio using Gemini 2.5 Flash
    
    Args:
        audio_bytes: Audio data in bytes
        language: Language code ('en', 'hi', 'mr')
    
    Returns:
        Transcribed text or None
    """
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        st.error("⚠️ GEMINI_API_KEY not found!")
        return None
    
    try:
        client = genai.Client(api_key=api_key)
        
        # Language-specific transcription instructions
        lang_names = {
            'en': 'English',
            'hi': 'Hindi (हिंदी)',
            'mr': 'Marathi (मराठी)'
        }
        lang_name = lang_names.get(language, 'English')
        
        system_instruction = f"""You are a transcription assistant for Indian farmers.
Transcribe the audio accurately in {lang_name}.
Keep natural speech patterns and include all spoken words."""
        
        task_prompt = f"""Transcribe this audio in {lang_name}.

Rules:
- Keep natural speech patterns
- Include all spoken words
- Don't add interpretation
- Just return the transcript text

Transcript:"""
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                task_prompt,
                types.Part.from_bytes(
                    data=audio_bytes,
                    mime_type='audio/wav'
                )
            ],
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.1,
                thinking_config=types.ThinkingConfig(thinking_budget=0)
            )
        )
        
        return response.text.strip()
        
    except Exception as e:
        st.error(f"Error transcribing audio: {str(e)}")
        return None


def render_voice_chatbot():
    """
    Main Voice Chatbot Component
    Shows chatbot interface with mic button for voice input
    """
    
    st.markdown("""
    <style>
    .voice-chatbot-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .chat-message-user {
        background-color: #E3F2FD;
        padding: 15px;
        border-radius: 15px;
        margin: 10px 0;
        border-left: 4px solid #2196F3;
    }
    .chat-message-bot {
        background-color: #E8F5E9;
        padding: 15px;
        border-radius: 15px;
        margin: 10px 0;
        border-left: 4px solid #4CAF50;
    }
    .mic-section {
        background: #FFF3E0;
        padding: 20px;
        border-radius: 12px;
        border: 2px dashed #FF9800;
        text-align: center;
        margin: 20px 0;
    }
    .quick-action-btn {
        margin: 5px;
        padding: 8px 16px;
        border-radius: 20px;
        background: #f0f0f0;
        border: 1px solid #ddd;
        cursor: pointer;
        transition: all 0.3s;
    }
    .quick-action-btn:hover {
        background: #e0e0e0;
        transform: scale(1.05);
    }
    @media (max-width: 768px) {
        .voice-chatbot-header {
            padding: 15px;
        }
        .chat-message-user, .chat-message-bot {
            padding: 12px;
            font-size: 14px;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class='voice-chatbot-header'>
        <h2>🗣️ Ask Advisor</h2>
        <p style='margin:0; font-size:16px;'>Speak or type your farming questions - I'm here to help!</p>
        <p style='margin:5px 0 0 0; font-size:14px; opacity:0.9;'>📍 Location-aware • 🗺️ Maps integrated</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get API key
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        st.error("⚠️ AI API key not configured. Please add GEMINI_API_KEY to your .env file.")
        st.info("💡 Get your API key from: https://makersuite.google.com/app/apikey")
        return
    
    # Initialize Gemini client
    client = genai.Client(api_key=api_key)
    
    # Initialize chat history
    if 'voice_chat_history' not in st.session_state:
        st.session_state.voice_chat_history = []
    
    # Get farmer context
    farmer_name = st.session_state.get("farmer_name", "Farmer")
    farmer_profile = st.session_state.get("farmer_profile", {})
    location = farmer_profile.get('location', 'Unknown')
    
    # Get GPS coordinates if available
    user_lat = farmer_profile.get('latitude')
    user_lon = farmer_profile.get('longitude')
    
    # Location detection section
    with st.expander("📍 Location Settings", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🌍 Detect My Location", use_container_width=True):
                st.info("Please enable location access in your browser when prompted")
                st.session_state.request_location = True
        
        with col2:
            if user_lat and user_lon:
                st.success(f"📍 {location}")
                st.caption(f"Coords: {user_lat:.4f}, {user_lon:.4f}")
            else:
                st.warning("Location not set")
    
    # Get language
    language = get_current_language()
    selected_lang = st.session_state.get('language', 'English')
    language_map = {
        "English": "English",
        "हिन्दी (Hindi)": "Hindi (हिन्दी)",
        "मराठी (Marathi)": "Marathi (मराठी)"
    }
    target_language = language_map.get(selected_lang, "English")
    
    # System context for AI with Maps awareness
    system_context = f"""You are an expert agricultural advisor serving Indian farmers with access to Google Maps data.

YOUR EXPERTISE:
- Crop management: planting, fertilization, pest control, harvesting
- Soil health and crop rotation strategies
- Weather-based farming decisions
- Market timing and price optimization
- Government schemes and subsidies
- Farm equipment and technology
- Local recommendations: nearby markets, shops, agro dealers
- Cost-effective solutions for small-scale farmers

FARMER YOU'RE HELPING:
Name: {farmer_name}
Location: {location}, India
Language: {target_language}

RESPONSE PRINCIPLES:
1. Concise: 3-5 sentences for simple questions
2. Actionable: Provide specific steps with timing and quantities
3. Localized: Consider {location} climate and practices
4. Location-aware: Use Maps data for nearby recommendations when asked
5. Budget-conscious: Mention costs in ₹ when relevant
6. Language: Reply ONLY in {target_language}
7. Safe: Include safety warnings when needed

For location-based queries (nearby places, directions), use Google Maps grounding.
Now answer the farmer's question clearly and helpfully:"""
    
    # Voice Input Section
    st.markdown("### 🎤 Voice Input")
    st.markdown("""
    <div class='mic-section'>
        <p style='margin:0;font-size:18px;font-weight:600;color:#F57C00;'>Click START to speak your question</p>
        <p style='margin:5px 0 0 0;font-size:14px;color:#666;'>Supported: English, Hindi (हिंदी), Marathi (मराठी)</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Microphone recorder
    col1, col2 = st.columns([3, 1])
    
    with col1:
        audio = mic_recorder(
            start_prompt=f"🔴 {t('Start Recording')}",
            stop_prompt=f"⏹️ {t('Stop Recording')}",
            just_once=False,
            use_container_width=True,
            key="voice_chatbot_recorder"
        )
    
    with col2:
        lang_select = st.selectbox(
            "🌐",
            ["en", "hi", "mr"],
            format_func=lambda x: {"en": "🇬🇧 EN", "hi": "🇮🇳 HI", "mr": "🇮🇳 MR"}[x],
            index=["en", "hi", "mr"].index(language),
            key="voice_lang_select",
            label_visibility="collapsed"
        )
    
    # Process recorded audio
    if audio:
        st.success(f"✅ {t('Audio recorded!')} ({len(audio['bytes'])} bytes)")
        
        if st.button(f"🤖 {t('Process & Send')}", use_container_width=True, type="primary"):
            with st.spinner(f"🔄 {t('Converting speech to text...')}"):
                transcribed_text = transcribe_voice_to_text(audio['bytes'], lang_select)
                
                if transcribed_text:
                    st.success(f"📝 {t('You said')}: **{transcribed_text}**")
                    # Store for sending
                    st.session_state.voice_transcribed_text = transcribed_text
                    st.session_state.auto_send_voice = True
                    st.rerun()
                else:
                    st.error(t("Could not understand audio. Please try again."))
    
    st.markdown("---")
    
    # Chat Display Area
    st.markdown("### 💬 Conversation")
    
    chat_container = st.container()
    
    with chat_container:
        if not st.session_state.voice_chat_history:
            st.info(f"👋 {t('Hello')} {farmer_name}! {t('Ask me anything about farming, crops, weather, or market prices!')}")
        
        # Display chat history
        for message in st.session_state.voice_chat_history:
            if message["role"] == "user":
                st.markdown(f"""
                <div class='chat-message-user'>
                    <strong>🧑‍🌾 {t('You')}:</strong><br>{message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class='chat-message-bot'>
                    <strong>🤖 {t('AI Assistant')}:</strong><br>{message["content"]}
                </div>
                """, unsafe_allow_html=True)
                
                # Show Maps sources if available
                if "sources" in message and message["sources"]:
                    with st.expander("🗺️ Google Maps Sources", expanded=False):
                        for source in message["sources"]:
                            st.markdown(f"📍 [{source['title']}]({source['uri']})")
                            st.caption("_From Google Maps_")
    
    st.markdown("---")
    
    # Quick Action Buttons
    st.markdown(f"### 💡 {t('Quick Questions')}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🌾 Best crops", key="qbtn1", use_container_width=True):
            st.session_state.quick_voice_question = f"What are the best crops for {location}?"
            st.rerun()
    
    with col2:
        if st.button("🐛 Pest control", key="qbtn2", use_container_width=True):
            st.session_state.quick_voice_question = "Organic pest control methods?"
            st.rerun()
    
    with col3:
        if st.button("💰 Market timing", key="qbtn3", use_container_width=True):
            st.session_state.quick_voice_question = "Best time to sell crops?"
            st.rerun()
    
    col4, col5, col6 = st.columns(3)
    
    with col4:
        if st.button("🏪 Nearby shops", key="qbtn4", use_container_width=True):
            st.session_state.quick_voice_question = "Where can I find agricultural shops near me?"
            st.rerun()
    
    with col5:
        if st.button("🏛️ Govt schemes", key="qbtn5", use_container_width=True):
            st.session_state.quick_voice_question = "Available government schemes?"
            st.rerun()
    
    with col6:
        if st.button("🌧️ Weather prep", key="qbtn6", use_container_width=True):
            st.session_state.quick_voice_question = "How to prepare for monsoon?"
            st.rerun()
    
    st.markdown("---")
    
    # Text Input Section
    st.markdown(f"### ⌨️ {t('Type Your Question')}")
    
    # Get default value from voice transcription or quick question
    default_value = ""
    if st.session_state.get('voice_transcribed_text'):
        default_value = st.session_state.pop('voice_transcribed_text', '')
    elif st.session_state.get('quick_voice_question'):
        default_value = st.session_state.pop('quick_voice_question', '')
    
    user_input = st.text_area(
        label=t("Your question:"),
        value=default_value,
        height=100,
        placeholder=t("E.g., What fertilizer is best for wheat in winter?"),
        key="voice_chat_input"
    )
    
    col_send, col_clear = st.columns([3, 1])
    
    with col_send:
        send_button = st.button("📤 Send Message", key="voice_send_btn", use_container_width=True, type="primary")
        # Auto-send if voice was transcribed
        if st.session_state.get('auto_send_voice'):
            send_button = True
            st.session_state.auto_send_voice = False
    
    with col_clear:
        if st.button("🗑️ Clear", key="voice_clear_btn", use_container_width=True):
            st.session_state.voice_chat_history = []
            st.rerun()
    
    # Process user input
    if send_button and user_input.strip():
        with st.spinner("🤖 AI is thinking..."):
            try:
                # Add user message to history
                st.session_state.voice_chat_history.append({
                    "role": "user",
                    "content": user_input,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Build conversation history
                conversation_history = ""
                for msg in st.session_state.voice_chat_history[-6:]:
                    role = "Farmer" if msg['role'] == "user" else "Assistant"
                    conversation_history += f"{role}: {msg['content']}\n\n"
                
                full_prompt = conversation_history.strip()
                
                # Detect if query needs location/maps (keywords)
                location_keywords = ['near', 'nearby', 'where', 'location', 'shop', 'store', 'market', 
                                    'mandi', 'दुकान', 'बाजार', 'कहाँ', 'पास', 'जवळ']
                needs_maps = any(keyword in user_input.lower() for keyword in location_keywords)
                
                # Try models in order with Maps grounding if needed
                models_to_try = ['gemini-2.5-flash', 'gemini-2.0-flash']
                response_text = None
                grounding_sources = []
                
                for model_name in models_to_try:
                    try:
                        # Build config with optional Maps grounding
                        config_params = {
                            "system_instruction": system_context,
                            "temperature": 0.4,
                            "max_output_tokens": 500,
                            "thinking_config": types.ThinkingConfig(thinking_budget=0)
                        }
                        
                        # Add Google Maps grounding if location query and coords available
                        if needs_maps and user_lat and user_lon:
                            config_params["tools"] = [types.Tool(google_maps=types.GoogleMaps())]
                            config_params["tool_config"] = types.ToolConfig(
                                retrieval_config=types.RetrievalConfig(
                                    lat_lng=types.LatLng(
                                        latitude=user_lat,
                                        longitude=user_lon
                                    )
                                )
                            )
                        
                        response = client.models.generate_content(
                            model=model_name,
                            contents=full_prompt,
                            config=types.GenerateContentConfig(**config_params)
                        )
                        
                        response_text = response.text
                        
                        # Check for grounding metadata (Maps sources)
                        if hasattr(response.candidates[0], 'grounding_metadata'):
                            grounding = response.candidates[0].grounding_metadata
                            if hasattr(grounding, 'grounding_chunks') and grounding.grounding_chunks:
                                for chunk in grounding.grounding_chunks:
                                    if hasattr(chunk, 'maps'):
                                        grounding_sources.append({
                                            'title': chunk.maps.title,
                                            'uri': chunk.maps.uri
                                        })
                        
                        break
                    except Exception as model_error:
                        if model_name == models_to_try[-1]:
                            raise model_error
                        continue
                
                # Add AI response to history with sources if available
                assistant_message = {
                    "role": "assistant",
                    "content": response_text,
                    "timestamp": datetime.now().isoformat()
                }
                
                if grounding_sources:
                    assistant_message["sources"] = grounding_sources
                
                st.session_state.voice_chat_history.append(assistant_message)
                
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.info("💡 Tip: Check your AI API key and quota.")
    
    # Stats Footer
    if st.session_state.voice_chat_history:
        st.markdown("---")
        st.caption(f"💬 {len(st.session_state.voice_chat_history)} messages | ⏰ {datetime.now().strftime('%I:%M %p')}")
    
    # Tips Expander
    with st.expander(f"💡 {t('Tips & Examples')}"):
        st.markdown(f"""
        **✅ {t('For Best Results')}:**
        
        1. 🎤 {t('Speak clearly in a quiet place')}
        2. 📱 {t('Hold device close to mouth')}
        3. 🗣️ {t('Speak naturally - no need to slow down')}
        4. 🌐 {t('Can mix Hindi, Marathi, English words')}
        5. ⏱️ {t('Keep questions under 30 seconds')}
        6. 📍 {t('Enable location for nearby recommendations')}
        
        **📝 {t('Example Questions')}:**
        
        **Farming Advice:**
        - English: "What is the best time to plant tomatoes?"
        - Hindi: "मेरे खेत में सफेद मक्खी का इलाज क्या है?"
        - Marathi: "गहू साठी कोणत खत चांगल आहे?"
        - Mixed: "Mere field mein pest problem hai, kya karu?"
        
        **Location-Based (with GPS):**
        - "Where can I find seed shops near me?"
        - "Nearest agricultural equipment dealers?"
        - "मेरे पास कौन सी मंडी है?" (Nearest mandi)
        - "जवळची खत दुकानं कुठे आहेत?" (Nearby fertilizer shops)
        """)
    
    # Add a note about location permissions
    if not (user_lat and user_lon):
        st.info("💡 **Tip:** Enable location access for personalized nearby recommendations (shops, mandis, dealers)")

