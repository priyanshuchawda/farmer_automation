import streamlit as st
from google import genai
from google.genai import types
import os
from datetime import datetime

def render_ai_chatbot_page():
    """
    Render AI Chatbot page for farmers to get real-time farming assistance
    """
    st.header("🤖 AI Farming Assistant")
    st.markdown("Ask me anything about farming, crops, weather, or marketplace!")
    
    # Get API key from environment
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        st.error("⚠️ AI API key not configured. Please add GEMINI_API_KEY to your .env file.")
        st.info("💡 Get your API key from: https://makersuite.google.com/app/apikey")
        return
    
    # Initialize Gemini client
    client = genai.Client(api_key=api_key)
    
    # Initialize chat history in session state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Get farmer context
    farmer_name = st.session_state.get("farmer_name", "Farmer")
    farmer_profile = st.session_state.get("farmer_profile", {})
    location = farmer_profile.get('location', 'Unknown')
    
    # Get language instruction
    selected_lang = st.session_state.get('language', 'English')
    language_map = {
        "English": "English",
        "हिन्दी (Hindi)": "Hindi (हिन्दी)",
        "मराठी (Marathi)": "Marathi (मराठी)"
    }
    target_language = language_map.get(selected_lang, "English")
    language_instruction = f"\n\nIMPORTANT: Reply ONLY in {target_language} language." if target_language != "English" else ""
    
    # System instruction - role and behavior
    system_context = f"""You are an expert agricultural advisor serving Indian farmers.

YOUR EXPERTISE:
- Crop management: planting, fertilization, pest control, harvesting
- Soil health and crop rotation strategies
- Weather-based farming decisions
- Market timing and price optimization
- Government schemes and subsidies
- Farm equipment and technology
- Cost-effective solutions for small-scale farmers

FARMER YOU'RE HELPING:
Name: {farmer_name}
Location: {location}, India
Language: {target_language}

RESPONSE PRINCIPLES:
1. Concise: 3-5 sentences for simple questions, detailed steps only when needed
2. Actionable: Provide specific steps with timing, quantities, and tools
3. Localized: Consider {location} climate, soil, and practices
4. Budget-conscious: Mention costs, prefer affordable solutions (₹ amounts when relevant)
5. App-aware: Reference app features (Weather, Market Prices, Calendar, Schemes)
6. Language: Reply ONLY in {target_language}, never mix languages
7. Safe: Include safety warnings for chemicals, equipment, weather risks

RESPONSE STRUCTURE:
[Direct answer to question]

[If action needed: 2-3 numbered steps with specifics]

[Helpful tip, caution, or app feature reference]

FEW-SHOT EXAMPLES:

Example 1 - Pest Problem:
Q: "Yellow spots on tomato leaves"
A: "Yellow spots indicate Early Blight fungal disease, very common in humid {location} climate.

Control measures:
1. Remove infected leaves today and burn them (stops spread)
2. Spray Copper Oxychloride 50% WP - mix 30g per 10L water (₹180-250/kg) every 7 days
3. Space plants 60cm apart for better air flow

Safety: Wear mask when spraying. Harvest tomatoes 15 days after last spray. Check Weather section - don't spray before rain."

Example 2 - Planting Time:
Q: "Best time to plant wheat"
A: "For {location}, optimal wheat sowing window is November 1-20 for maximum yield.

Preparation (start now):
1. Deep plough 2-3 times - first plough 6 inches deep, then 4 inches
2. Mix 50kg DAP + 25kg Urea per acre during final ploughing (₹3,500 total)
3. Sow with seed drill 20kg seed/acre OR broadcast 25kg/acre

Check our Weather section first - avoid sowing if 3-day rain forecast shows 50%+ probability. Rain within 48 hours damages germination."

Example 3 - Price Question (Hindi):
Q: "कीमत कब अच्छी मिलेगी"
A: "गेहूं की कीमत मार्च-अप्रैल में सबसे अच्छी मिलती है (15-20% ज्यादा)।

क्या करें:
1. कटाई के तुरंत बाद मत बेचें - सभी बेचते हैं तो कीमत गिरती है
2. ऐप के Market Prices section में रोज़ mandi भाव देखें
3. MSP ₹2275/quintal से कम में कभी न बेचें

स्टोरेज टिप: अगर godown है तो 2-3 महीने रुकें - कीमत ₹2500-2600 तक जा सकती है। बिना godown के मत रखें, चूहे/नमी का खतरा।"

Now answer the farmer's question clearly and helpfully:"""
    
    # Display chat interface
    st.markdown("---")
    
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        # Display chat history
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(f"""
                <div style='background-color:#E3F2FD;padding:10px;border-radius:10px;margin:10px 0;'>
                    <strong>🧑‍🌾 You:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style='background-color:#E8F5E9;padding:10px;border-radius:10px;margin:10px 0;'>
                    <strong>🤖 AI Assistant:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
    
    # Quick suggestion buttons
    st.markdown("### 💡 Quick Questions:")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🌾 Best crops for my region", key="btn_crops", use_container_width=True):
            st.session_state.quick_question = f"What are the best crops to grow in {location}?"
            st.rerun()
    
    with col2:
        if st.button("🐛 Pest control tips", key="btn_pest", use_container_width=True):
            st.session_state.quick_question = "What are effective organic pest control methods?"
            st.rerun()
    
    with col3:
        if st.button("💰 Market timing advice", key="btn_market", use_container_width=True):
            st.session_state.quick_question = "When is the best time to sell my crops?"
            st.rerun()
    
    col4, col5, col6 = st.columns(3)
    
    with col4:
        if st.button("🌧️ Monsoon preparation", key="btn_monsoon", use_container_width=True):
            st.session_state.quick_question = "How should I prepare my farm for monsoon season?"
            st.rerun()
    
    with col5:
        if st.button("🏛️ Government schemes", key="btn_schemes", use_container_width=True):
            st.session_state.quick_question = "What government schemes are available for farmers?"
            st.rerun()
    
    with col6:
        if st.button("📊 Farm budgeting", key="btn_budget", use_container_width=True):
            st.session_state.quick_question = "How can I better manage my farm finances?"
            st.rerun()
    
    st.markdown("---")
    
    # Chat input - use quick_question if available
    default_value = st.session_state.pop('quick_question', '')
    
    user_input = st.text_input(
        "Ask your question:", 
        value=default_value,
        key="chat_input",
        placeholder="E.g., What fertilizer is best for wheat in winter?"
    )
    
    col_send, col_clear = st.columns([3, 1])
    
    with col_send:
        send_button = st.button("📤 Send", key="send_btn", use_container_width=True, type="primary")
    
    with col_clear:
        if st.button("🗑️ Clear Chat", key="clear_btn", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
    
    # Process user input
    if send_button and user_input:
        with st.spinner("🤖 AI is thinking..."):
            try:
                # Add user message to history
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": user_input,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Build conversation history for context (last 5 messages)
                conversation_history = ""
                for msg in st.session_state.chat_history[-6:]:  # -6 to include current
                    role = "Farmer" if msg['role'] == "user" else "Assistant"
                    conversation_history += f"{role}: {msg['content']}\n\n"
                
                # Final prompt with context
                full_prompt = conversation_history.strip()
                
                # Try models in order: 2.5-flash, 2.0-flash, 1.5-flash
                models_to_try = ['gemini-2.5-flash', 'gemini-2.0-flash']
                response_text = None
                
                for model_name in models_to_try:
                    try:
                        response = client.models.generate_content(
                            model=model_name,
                            contents=full_prompt,
                            config=types.GenerateContentConfig(
                                system_instruction=system_context,
                                temperature=0.4,  # Balanced: creative but reliable
                                max_output_tokens=500,  # Concise responses
                                thinking_config=types.ThinkingConfig(thinking_budget=0)  # Disable thinking for speed
                            )
                        )
                        response_text = response.text
                        break  # Success, exit loop
                    except Exception as model_error:
                        if model_name == models_to_try[-1]:  # Last model failed
                            raise model_error
                        continue  # Try next model
                
                # Add AI response to history
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response_text,
                    "timestamp": datetime.now().isoformat()
                })
                
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.info("💡 Tip: Make sure your AI API key is valid and has quota available.")
    
    # Stats
    if st.session_state.chat_history:
        st.markdown("---")
        st.caption(f"💬 Chat messages: {len(st.session_state.chat_history)} | Last updated: {datetime.now().strftime('%I:%M %p')}")



