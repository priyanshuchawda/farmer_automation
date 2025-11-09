import streamlit as st
import google.generativeai as genai
import os
from datetime import datetime

def render_ai_chatbot_page():
    """
    Render AI Chatbot page for farmers to get real-time farming assistance
    """
    st.header("🤖 AI Farming Assistant")
    st.markdown("Ask me anything about farming, crops, weather, or marketplace!")
    
    # Get API key from environment
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        st.error("⚠️ AI API key not configured. Please add GEMINI_API_KEY to your .env file.")
        st.info("💡 Get your API key from: https://makersuite.google.com/app/apikey")
        return
    
    # Configure AI
    genai.configure(api_key=api_key)
    
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
    
    # System context for the AI
    system_context = f"""You are an AI farming assistant helping {farmer_name}, a farmer from {location}. 
    Provide practical, actionable advice about:
    - Crop cultivation and management
    - Weather-based farming decisions
    - Pest and disease control
    - Market prices and selling strategies
    - Government schemes and subsidies{language_instruction}
    - Farm finance and budgeting
    - Seasonal farming calendar
    
    Keep responses concise, practical, and region-specific when possible.
    If asked about current weather or prices, remind them to check the respective sections in the app.
    """
    
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
        if st.button("🌾 Best crops for my region", width="stretch"):
            st.session_state.quick_question = f"What are the best crops to grow in {location}?"
    
    with col2:
        if st.button("🐛 Pest control tips", width="stretch"):
            st.session_state.quick_question = "What are effective organic pest control methods?"
    
    with col3:
        if st.button("💰 Market timing advice", width="stretch"):
            st.session_state.quick_question = "When is the best time to sell my crops?"
    
    col4, col5, col6 = st.columns(3)
    
    with col4:
        if st.button("🌧️ Monsoon preparation", width="stretch"):
            st.session_state.quick_question = "How should I prepare my farm for monsoon season?"
    
    with col5:
        if st.button("🏛️ Government schemes", width="stretch"):
            st.session_state.quick_question = "What government schemes are available for farmers?"
    
    with col6:
        if st.button("📊 Farm budgeting", width="stretch"):
            st.session_state.quick_question = "How can I better manage my farm finances?"
    
    st.markdown("---")
    
    # Chat input
    user_input = st.text_input(
        "Ask your question:", 
        value=st.session_state.get('quick_question', ''),
        key="chat_input",
        placeholder="E.g., What fertilizer is best for wheat in winter?"
    )
    
    # Clear quick question after using it
    if 'quick_question' in st.session_state:
        del st.session_state.quick_question
    
    col_send, col_clear = st.columns([3, 1])
    
    with col_send:
        send_button = st.button("📤 Send", width="stretch", type="primary")
    
    with col_clear:
        if st.button("🗑️ Clear Chat", width="stretch"):
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
                
                # Create model
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Build conversation history for context
                conversation = system_context + "\n\n"
                for msg in st.session_state.chat_history[-5:]:  # Last 5 messages for context
                    conversation += f"{msg['role']}: {msg['content']}\n"
                
                # Generate response
                response = model.generate_content(conversation)
                
                # Add AI response to history
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response.text,
                    "timestamp": datetime.now().isoformat()
                })
                
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.info("💡 Tip: Make sure your AI API key is valid and has quota available.")
    
    # Usage tips
    with st.expander("ℹ️ How to use the AI Assistant"):
        st.markdown("""
        ### Tips for getting the best answers:
        
        - **Be specific**: Instead of "crop problems", ask "yellow spots on tomato leaves, what's wrong?"
        - **Provide context**: Mention your location, season, or crop type
        - **Ask follow-up questions**: The AI remembers the conversation context
        - **Use quick questions**: Click the suggestion buttons for common queries
        
        ### What can you ask about:
        - 🌾 Crop selection and rotation
        - 💧 Irrigation and water management
        - 🐛 Pest and disease identification
        - 🌱 Seed selection and planting
        - 🌤️ Weather-based farming decisions
        - 💰 Market strategies and pricing
        - 🏛️ Government schemes and subsidies
        - 📊 Farm finance and record keeping
        """)
    
    # Stats
    if st.session_state.chat_history:
        st.markdown("---")
        st.caption(f"💬 Chat messages: {len(st.session_state.chat_history)} | Last updated: {datetime.now().strftime('%I:%M %p')}")


