"""
Voice-Powered Listing Creator
Uses Gemini 2.5 Flash for audio transcription and structured data extraction
Supports Hindi, Marathi, and English
"""

import streamlit as st
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import Optional, Literal
import os
from datetime import date
from components.translation_utils import t, get_current_language
from database.db_functions import add_data, get_data
from streamlit_mic_recorder import mic_recorder


# ----------------------------------------
# --- PYDANTIC MODELS FOR STRUCTURED OUTPUT ---
# ----------------------------------------

class ToolListing(BaseModel):
    """Schema for Tool/Machine listing extracted from voice"""
    farmer_name: Optional[str] = Field(description="Name of the farmer")
    location: Optional[str] = Field(description="Village or location name")
    tool_type: Optional[Literal["Tractor", "Plow", "Seeder", "Sprayer", "Harvester", "Other"]] = Field(
        description="Type of farm tool or machine"
    )
    rent_rate: Optional[float] = Field(description="Rent rate per day in rupees")
    contact: Optional[str] = Field(description="Contact phone number (10 digits)")
    notes: Optional[str] = Field(description="Additional notes about condition, availability, etc.")


class CropListing(BaseModel):
    """Schema for Crop listing extracted from voice"""
    farmer_name: Optional[str] = Field(description="Name of the farmer")
    location: Optional[str] = Field(description="Village or location name")
    crop_name: Optional[str] = Field(description="Name of the crop (e.g., Wheat, Rice, Tomato)")
    quantity: Optional[float] = Field(description="Quantity in numeric value")
    unit: Optional[Literal["Quintals", "Kilograms", "Tonnes"]] = Field(
        description="Unit of measurement"
    )
    price_per_unit: Optional[float] = Field(description="Expected price per unit in rupees")
    contact: Optional[str] = Field(description="Contact phone number (10 digits)")


class LaborListing(BaseModel):
    """Schema for Labor/Worker job listing extracted from voice"""
    posted_by: Optional[str] = Field(description="Name of the farmer posting the job")
    location: Optional[str] = Field(description="Village or location name")
    work_type: Optional[Literal["Harvesting", "Planting", "Irrigation", "General Farm Work", "Other"]] = Field(
        description="Type of work needed"
    )
    workers_needed: Optional[int] = Field(description="Number of workers needed")
    duration_days: Optional[int] = Field(description="Duration in days")
    wage_per_day: Optional[float] = Field(description="Daily wage in rupees")
    contact: Optional[str] = Field(description="Contact phone number (10 digits)")
    description: Optional[str] = Field(description="Additional job details")
    start_date: Optional[str] = Field(description="Start date in YYYY-MM-DD format")


# ----------------------------------------
# --- GEMINI AI FUNCTIONS ---
# ----------------------------------------

def get_gemini_client():
    """Initialize and return Gemini client"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        # Try streamlit secrets
        api_key = st.secrets.get("GEMINI_API_KEY")
    
    if not api_key:
        st.error("⚠️ GEMINI_API_KEY not found! Please configure it in .env or Streamlit secrets.")
        return None
    
    return genai.Client(api_key=api_key)


def transcribe_and_extract_listing(audio_bytes, listing_type, language='en'):
    """
    Transcribe audio and extract structured listing data using Gemini 2.5 Flash
    Using Gemini's native audio understanding with optimized prompts
    
    Args:
        audio_bytes: Audio data in bytes
        listing_type: 'tool', 'crop', or 'labor'
        language: Language code ('en', 'hi', 'mr')
    
    Returns:
        dict with transcript and extracted data
    """
    client = get_gemini_client()
    if not client:
        return None
    
    try:
        # Create system instruction and prompt based on listing type
        # Using Google's best practices: clear instructions, examples, constraints
        
        if listing_type == 'tool':
            # System instruction defines the role and behavior
            system_instruction = """You are a helpful AI assistant for Indian farmers creating farm tool rental listings.
You understand Hindi (हिंदी), Marathi (मराठी), and English fluently, including mixed code-switching.
Extract information accurately from audio and return structured JSON data."""
            
            # Main task with clear instructions and examples
            task_prompt = """Listen to the audio and extract farm tool rental information.

REQUIRED FIELDS:
- farmer_name: Full name of the farmer
- location: Village or town name
- tool_type: Must be one of: Tractor, Plow, Seeder, Sprayer, Harvester, Other
- rent_rate: Daily rental price in rupees (number only)
- contact: 10-digit phone number
- notes: Additional details about condition, availability

EXTRACTION RULES:
1. Phone numbers: Extract 10 digits even if spoken as words
   Example: "nau aath do char" = 9824
   Example: "98-765-43210" = 9876543210

2. Tool types: Map variations to standard types
   ट्रैक्टर/tractor → Tractor
   हल/plow → Plow
   बीज बोने की मशीन/seeder → Seeder
   छिड़काव यंत्र/sprayer → Sprayer

3. Numbers: Convert spoken to digits
   "do hazar" = 2000
   "teen sau" = 300

4. Missing info: Use null if not mentioned

EXAMPLES:
Input: "Mera naam Ram. Tractor kiraye par. 2000 rupay per day. Phone 9876543210"
Output: {"farmer_name": "Ram", "location": null, "tool_type": "Tractor", "rent_rate": 2000, "contact": "9876543210", "notes": null}

Now extract from the audio:"""
            
            schema = ToolListing.model_json_schema()
            
        elif listing_type == 'crop':
            system_instruction = """You are a helpful AI assistant for Indian farmers creating crop sale listings.
You understand Hindi (हिंदी), Marathi (मराठी), and English fluently, including mixed code-switching.
Extract information accurately from audio and return structured JSON data."""
            
            task_prompt = """Listen to the audio and extract crop sale information.

REQUIRED FIELDS:
- farmer_name: Full name of the farmer
- location: Village or town name
- crop_name: Name of the crop
- quantity: Numeric amount
- unit: Must be one of: Quintals, Kilograms, Tonnes
- price_per_unit: Price in rupees (number only)
- contact: 10-digit phone number

EXTRACTION RULES:
1. Crop names: Recognize multilingual variations
   गेहूं/गहू/wheat → wheat
   चावल/तांदूळ/rice → rice
   टमाटर/टोमॅटो/tomato → tomato
   प्याज/कांदा/onion → onion

2. Quantities: Convert to numbers
   "sau kilo" = 100 Kilograms
   "pachas quintal" = 50 Quintals
   "ek tonne" = 1 Tonnes

3. Units: Map to standard units
   किलो/kilo → Kilograms
   क्विंटल/quintal → Quintals
   टन/tonne → Tonnes

4. Phone numbers: Extract 10 digits
5. Missing info: Use null

EXAMPLES:
Input: "Mai Suresh. 100 quintal tamatar. 20 rupay kilo. 9823456789"
Output: {"farmer_name": "Suresh", "location": null, "crop_name": "tamatar", "quantity": 100, "unit": "Quintals", "price_per_unit": 20, "contact": "9823456789"}

Now extract from the audio:"""
            
            schema = CropListing.model_json_schema()
            
        else:  # labor
            system_instruction = """You are a helpful AI assistant for Indian farmers posting worker job listings.
You understand Hindi (हिंदी), Marathi (मराठी), and English fluently, including mixed code-switching.
Extract information accurately from audio and return structured JSON data."""
            
            task_prompt = """Listen to the audio and extract worker job information.

REQUIRED FIELDS:
- posted_by: Name of the farmer posting
- location: Village or town name
- work_type: Must be one of: Harvesting, Planting, Irrigation, General Farm Work, Other
- workers_needed: Number of workers (integer)
- duration_days: Job duration in days (integer)
- wage_per_day: Daily wage in rupees (number)
- contact: 10-digit phone number
- description: Additional job details (optional)
- start_date: YYYY-MM-DD format if mentioned (optional)

EXTRACTION RULES:
1. Work types: Map variations
   कटाई/harvesting/katai → Harvesting
   बोवाई/planting/bonai → Planting
   सिंचाई/irrigation/sinchai → Irrigation

2. Numbers: Convert all spoken numbers
   "panch majdur" = 5 workers
   "das din" = 10 days
   "paanch sau rupay" = 500 rupees

3. Phone numbers: Extract 10 digits
4. Missing info: Use null

EXAMPLES:
Input: "Mujhe 5 majdur chahiye katai ke liye. 10 din. 500 rupay daily. Call 9876543210"
Output: {"posted_by": null, "location": null, "work_type": "Harvesting", "workers_needed": 5, "duration_days": 10, "wage_per_day": 500, "contact": "9876543210", "description": null, "start_date": null}

Now extract from the audio:"""
            
            schema = LaborListing.model_json_schema()
        
        # SINGLE API CALL - Gemini understands audio directly and returns structured JSON!
        # Using system instruction for better prompt separation and clarity
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
                response_mime_type="application/json",
                response_json_schema=schema,
                temperature=0.1,  # Low temperature for deterministic extraction
                thinking_config=types.ThinkingConfig(thinking_budget=0)  # Disable thinking for speed
            )
        )
        
        # Parse the response
        import json
        extracted_data = json.loads(response.text)
        
        # Generate a human-friendly transcript for display
        # (Quick second call just for showing what was said)
        # Using clear, specific instruction with output prefix
        transcript_system = "You are a transcription assistant. Provide clean, accurate transcripts."
        transcript_task = """Transcribe this audio accurately.

Rules:
- Keep natural speech patterns
- Include all spoken words
- Don't add interpretation or formatting
- Just return the transcript text

Transcript:"""
        
        transcript_response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                transcript_task,
                types.Part.from_bytes(
                    data=audio_bytes,
                    mime_type='audio/wav'
                )
            ],
            config=types.GenerateContentConfig(
                system_instruction=transcript_system,
                temperature=0.1,
                thinking_config=types.ThinkingConfig(thinking_budget=0)
            )
        )
        
        return {
            'transcript': transcript_response.text,
            'extracted_data': extracted_data,
            'success': True
        }
        
    except Exception as e:
        st.error(f"Error processing audio: {str(e)}")
        return {
            'transcript': '',
            'extracted_data': None,
            'success': False,
            'error': str(e)
        }


# ----------------------------------------
# --- UI COMPONENTS ---
# ----------------------------------------

def render_voice_listing_creator(farmer_name):
    """
    Main UI component for voice-powered listing creation
    """
    st.markdown("""
    <style>
    .voice-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        margin-bottom: 20px;
    }
    .voice-instructions {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #2E8B57;
        margin: 10px 0;
    }
    .preview-box {
        background: #fff3cd;
        padding: 15px;
        border-radius: 10px;
        border: 2px solid #ffc107;
        margin: 10px 0;
    }
    .mic-button {
        font-size: 3rem;
        text-align: center;
        padding: 20px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="voice-card">', unsafe_allow_html=True)
    st.title("🎤 " + t("Voice Listing Creator"))
    st.markdown(t("Speak naturally in Hindi, Marathi, or English - AI will understand!"))
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Get user profile for pre-filling
    profile = st.session_state.get("farmer_profile", {})
    
    # Listing type selection
    col1, col2, col3 = st.columns(3)
    with col1:
        listing_type = st.selectbox(
            t("What do you want to list?"),
            ["tool", "crop", "labor"],
            format_func=lambda x: {
                "tool": "🚜 " + t("Farm Tool/Machine"),
                "crop": "🌾 " + t("Crop for Sale"),
                "labor": "👷 " + t("Worker/Labor Job")
            }[x]
        )
    
    with col2:
        language = st.selectbox(
            t("Preferred Language"),
            ["en", "hi", "mr"],
            format_func=lambda x: {
                "en": "🇬🇧 English",
                "hi": "🇮🇳 हिंदी",
                "mr": "🇮🇳 मराठी"
            }[x],
            index=["en", "hi", "mr"].index(get_current_language())
        )
    
    # Instructions
    st.markdown('<div class="voice-instructions">', unsafe_allow_html=True)
    st.subheader("📝 " + t("Instructions"))
    
    if listing_type == "tool":
        st.markdown(f"""
        **{t("Speak clearly for 30-60 seconds. Mention")}:**
        - {t("Your name")} (आपका नाम / तुमचे नाव)
        - {t("Village/Location")} (गांव / गाव)
        - {t("Tool type")} (औजार का प्रकार / साधनाचा प्रकार)
        - {t("Rent per day")} (किराया प्रति दिन / भाडे प्रतिदिन)
        - {t("Contact number")} (फोन नंबर / दूरध्वनी क्रमांक)
        
        **{t("Example")}:** *"Mera naam Ramu. Main Wagholi gaon se hu. Mere paas ek tractor hai jo main kiraye par dena chahta hu. 
        Ek din ka 2000 rupay. Mera phone number 9876543210."*
        """)
    elif listing_type == "crop":
        st.markdown(f"""
        **{t("Speak clearly for 30-60 seconds. Mention")}:**
        - {t("Your name")} (आपका नाम / तुमचे नाव)
        - {t("Village/Location")} (गांव / गाव)
        - {t("Crop name")} (फसल / पीक)
        - {t("Quantity and unit")} (मात्रा / प्रमाण)
        - {t("Price per unit")} (कीमत / किंमत)
        - {t("Contact number")} (फोन नंबर / दूरध्वनी क्रमांक)
        
        **{t("Example")}:** *"Namaste, mai Suresh. Shirur gaon se. Mere paas 100 quintal gehun hai. 
        20 rupay kilo chahiye. Contact number 9823456789."*
        """)
    else:  # labor
        st.markdown(f"""
        **{t("Speak clearly for 30-60 seconds. Mention")}:**
        - {t("Your name")} (आपका नाम / तुमचे नाव)
        - {t("Village/Location")} (गांव / गाव)
        - {t("Work type")} (काम का प्रकार / कामाचा प्रकार)
        - {t("Workers needed")} (मजदूरों की संख्या / कामगार)
        - {t("Duration")} (अवधि / कालावधी)
        - {t("Daily wage")} (मजदूरी / मजुरी)
        - {t("Contact number")} (फोन नंबर / दूरध्वनी क्रमांक)
        
        **{t("Example")}:** *"Mai Ganesh Patil. Pune se. Mujhe 5 majdur chahiye harvesting ke liye. 
        10 din ka kaam hai. 500 rupay per day dunga. Mobile 9876543210."*
        """)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Microphone recorder
    st.markdown('<div class="mic-button">🎤</div>', unsafe_allow_html=True)
    st.markdown(f"**{t('Click START to record your listing')}** ⬇️")
    
    audio = mic_recorder(
        start_prompt=f"🔴 {t('Start Recording')}",
        stop_prompt=f"⏹️ {t('Stop Recording')}",
        just_once=False,
        use_container_width=True,
        key="voice_listing_recorder"
    )
    
    # Process audio when recorded
    if audio:
        st.success(f"✅ {t('Audio recorded successfully!')} ({len(audio['bytes'])} bytes)")
        
        # Add a process button
        if st.button(f"🤖 {t('Process Audio with AI')}", use_container_width=True):
            with st.spinner(f"🔄 {t('AI is processing your speech...')}"):
                result = transcribe_and_extract_listing(
                    audio['bytes'],
                    listing_type,
                    language
                )
                
                if result and result['success']:
                    # Store in session state for review
                    st.session_state.voice_listing_result = result
                    st.session_state.voice_listing_type = listing_type
                    st.rerun()
    
    # Display results and preview if available
    if 'voice_listing_result' in st.session_state:
        result = st.session_state.voice_listing_result
        listing_type = st.session_state.voice_listing_type
        
        st.markdown("---")
        st.subheader("📝 " + t("Transcript"))
        st.info(result['transcript'])
        
        st.markdown("---")
        st.subheader("📋 " + t("Extracted Information"))
        
        extracted = result['extracted_data']
        
        # Create editable form for preview and corrections
        with st.form("voice_listing_preview"):
            st.markdown('<div class="preview-box">', unsafe_allow_html=True)
            st.warning(f"⚠️ {t('Please review and correct any mistakes before submitting')}")
            st.markdown('</div>', unsafe_allow_html=True)
            
            if listing_type == "tool":
                col1, col2 = st.columns(2)
                with col1:
                    farmer_name_val = st.text_input(
                        t("Farmer Name"),
                        value=extracted.get('farmer_name') or farmer_name or '',
                        key="voice_farmer_name"
                    )
                    location_val = st.text_input(
                        t("Location"),
                        value=extracted.get('location') or profile.get('location', ''),
                        key="voice_location"
                    )
                    tool_type_val = st.selectbox(
                        t("Tool Type"),
                        ["Tractor", "Plow", "Seeder", "Sprayer", "Harvester", "Other"],
                        index=["Tractor", "Plow", "Seeder", "Sprayer", "Harvester", "Other"].index(
                            extracted.get('tool_type') or "Other"
                        ) if extracted.get('tool_type') in ["Tractor", "Plow", "Seeder", "Sprayer", "Harvester", "Other"] else 5,
                        key="voice_tool_type"
                    )
                with col2:
                    rent_rate_val = st.number_input(
                        t("Rent Rate (per day)"),
                        value=float(extracted.get('rent_rate') or 0),
                        min_value=0.0,
                        key="voice_rent_rate"
                    )
                    contact_val = st.text_input(
                        t("Contact Number"),
                        value=extracted.get('contact') or profile.get('contact', ''),
                        key="voice_contact"
                    )
                    notes_val = st.text_area(
                        t("Notes"),
                        value=extracted.get('notes') or '',
                        key="voice_notes"
                    )
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button(f"✅ {t('Confirm and Add Listing')}", use_container_width=True):
                        if farmer_name_val and location_val and tool_type_val and rent_rate_val > 0 and contact_val:
                            tool_data = (farmer_name_val, location_val, tool_type_val, rent_rate_val, contact_val, notes_val)
                            add_data("tools", tool_data)
                            st.session_state.tools = get_data("tools")
                            st.success(f"🎉 {t('Tool listing created successfully!')} - {tool_type_val}")
                            # Clear session state
                            del st.session_state.voice_listing_result
                            del st.session_state.voice_listing_type
                            st.rerun()
                        else:
                            st.error(t("Please fill in all required fields."))
                
                with col2:
                    if st.form_submit_button(f"🔄 {t('Record Again')}", use_container_width=True):
                        del st.session_state.voice_listing_result
                        del st.session_state.voice_listing_type
                        st.rerun()
            
            elif listing_type == "crop":
                col1, col2 = st.columns(2)
                with col1:
                    farmer_name_val = st.text_input(
                        t("Farmer Name"),
                        value=extracted.get('farmer_name') or farmer_name or '',
                        key="voice_farmer_name"
                    )
                    location_val = st.text_input(
                        t("Location"),
                        value=extracted.get('location') or profile.get('location', ''),
                        key="voice_location"
                    )
                    crop_name_val = st.text_input(
                        t("Crop Name"),
                        value=extracted.get('crop_name') or '',
                        key="voice_crop_name"
                    )
                with col2:
                    quantity_val = st.number_input(
                        t("Quantity"),
                        value=float(extracted.get('quantity') or 0),
                        min_value=0.0,
                        key="voice_quantity"
                    )
                    unit_val = st.selectbox(
                        t("Unit"),
                        ["Quintals", "Kilograms", "Tonnes"],
                        index=["Quintals", "Kilograms", "Tonnes"].index(
                            extracted.get('unit') or "Quintals"
                        ) if extracted.get('unit') in ["Quintals", "Kilograms", "Tonnes"] else 0,
                        key="voice_unit"
                    )
                    price_val = st.number_input(
                        t("Price per unit"),
                        value=float(extracted.get('price_per_unit') or 0),
                        min_value=0.0,
                        key="voice_price"
                    )
                    contact_val = st.text_input(
                        t("Contact Number"),
                        value=extracted.get('contact') or profile.get('contact', ''),
                        key="voice_contact"
                    )
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button(f"✅ {t('Confirm and Add Listing')}", use_container_width=True):
                        if farmer_name_val and location_val and crop_name_val and quantity_val > 0 and price_val > 0 and contact_val:
                            listing_date = date.today().strftime("%Y-%m-%d")
                            quantity_str = f"{quantity_val} {unit_val}"
                            crop_data = (farmer_name_val, location_val, crop_name_val, quantity_str, price_val, contact_val, listing_date)
                            add_data("crops", crop_data)
                            st.session_state.crops = get_data("crops")
                            st.success(f"🎉 {t('Crop listing created successfully!')} - {crop_name_val}")
                            # Clear session state
                            del st.session_state.voice_listing_result
                            del st.session_state.voice_listing_type
                            st.rerun()
                        else:
                            st.error(t("Please fill in all required fields."))
                
                with col2:
                    if st.form_submit_button(f"🔄 {t('Record Again')}", use_container_width=True):
                        del st.session_state.voice_listing_result
                        del st.session_state.voice_listing_type
                        st.rerun()
            
            else:  # labor
                col1, col2 = st.columns(2)
                with col1:
                    posted_by_val = st.text_input(
                        t("Posted By"),
                        value=extracted.get('posted_by') or farmer_name or '',
                        key="voice_posted_by"
                    )
                    location_val = st.text_input(
                        t("Location"),
                        value=extracted.get('location') or profile.get('location', ''),
                        key="voice_location"
                    )
                    work_type_val = st.selectbox(
                        t("Work Type"),
                        ["Harvesting", "Planting", "Irrigation", "General Farm Work", "Other"],
                        index=["Harvesting", "Planting", "Irrigation", "General Farm Work", "Other"].index(
                            extracted.get('work_type') or "General Farm Work"
                        ) if extracted.get('work_type') in ["Harvesting", "Planting", "Irrigation", "General Farm Work", "Other"] else 3,
                        key="voice_work_type"
                    )
                    workers_val = st.number_input(
                        t("Workers Needed"),
                        value=int(extracted.get('workers_needed') or 1),
                        min_value=1,
                        key="voice_workers"
                    )
                with col2:
                    duration_val = st.number_input(
                        t("Duration (days)"),
                        value=int(extracted.get('duration_days') or 1),
                        min_value=1,
                        key="voice_duration"
                    )
                    wage_val = st.number_input(
                        t("Wage per day"),
                        value=float(extracted.get('wage_per_day') or 0),
                        min_value=0.0,
                        key="voice_wage"
                    )
                    contact_val = st.text_input(
                        t("Contact Number"),
                        value=extracted.get('contact') or profile.get('contact', ''),
                        key="voice_contact"
                    )
                    start_date_val = st.date_input(
                        t("Start Date"),
                        value=date.today(),
                        key="voice_start_date"
                    )
                description_val = st.text_area(
                    t("Description"),
                    value=extracted.get('description') or '',
                    key="voice_description"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button(f"✅ {t('Confirm and Add Listing')}", use_container_width=True):
                        if posted_by_val and location_val and work_type_val and workers_val > 0 and duration_val > 0 and wage_val > 0 and contact_val:
                            labor_data = (
                                posted_by_val, location_val, work_type_val, workers_val,
                                duration_val, wage_val, contact_val, description_val,
                                start_date_val.strftime("%Y-%m-%d"), "Open"
                            )
                            add_data("labor_jobs", labor_data)
                            st.session_state.labor_jobs = get_data("labor_jobs")
                            st.success(f"🎉 {t('Labor job posted successfully!')} - {work_type_val}")
                            # Clear session state
                            del st.session_state.voice_listing_result
                            del st.session_state.voice_listing_type
                            st.rerun()
                        else:
                            st.error(t("Please fill in all required fields."))
                
                with col2:
                    if st.form_submit_button(f"🔄 {t('Record Again')}", use_container_width=True):
                        del st.session_state.voice_listing_result
                        del st.session_state.voice_listing_type
                        st.rerun()
    
    # Tips section
    st.markdown("---")
    with st.expander(f"💡 {t('Tips for Best Results')}"):
        st.markdown(f"""
        1. **{t('Speak clearly')}** - {t('Find a quiet place')}
        2. **{t('Speak naturally')}** - {t('No need to speak slowly')}
        3. **{t('Mention all details')}** - {t('Name, location, item, price, contact')}
        4. **{t('Use any language')}** - {t('Hindi, Marathi, English - all work!')}
        5. **{t('Review before submitting')}** - {t('AI is smart but double-check!')}
        6. **{t('Phone numbers')}** - {t('Say digits clearly, can use spaces')}
        
        **{t('Example mixing languages')}:**
        *"Mera naam Suresh Patil. Main Shirur gaon se hu. I have one tractor for rent. 
        2000 rupay per day. Contact number nau aath do teen char panch cha sat ath nau."*
        """)
