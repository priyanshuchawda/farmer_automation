# components/government_schemes_page.py
"""
Government Schemes & Financial Tools for Farmers
Uses AI with Google Search grounding to find real-time scheme information
"""

import streamlit as st
from google import genai
from google.genai import types
import os
from datetime import datetime, timedelta
from database.cache_manager import CacheManager
import json

class GovernmentSchemesHelper:
    """Helper class for government schemes and financial tools."""
    
    def __init__(self):
        """Initialize AI AI with Google Search."""
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY not found in environment")
        
        self.client = genai.Client(api_key=api_key)
        # Try Gemini 2.5 Flash first, fallback to 2.0 Flash
        try:
            self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents="test",
                config=types.GenerateContentConfig(temperature=0.1)
            )
            self.model = 'gemini-2.5-flash'
            print("✅ Using Gemini 2.5 Flash")
        except:
            self.model = 'gemini-2.0-flash'
            print("⚠️ Fallback to Gemini 2.0 Flash")
        self.cache = CacheManager()
    
    def search_government_schemes(self, location, crop_type=None, force_refresh=False, language="English"):
        """
        Search for government agricultural schemes using Google Search grounding.
        
        Args:
            location: Farmer's location (city, state/district)
            crop_type: Optional crop type for specific schemes
            force_refresh: Force fetch fresh data instead of using cache
            language: Response language (English, Hindi, Marathi)
        
        Returns:
            dict: Schemes information with sources
        """
        cache_key = f"schemes_{location}_{crop_type or 'general'}_{language}"
        
        # Check cache first (unless force refresh)
        if not force_refresh:
            cached_data = self._get_from_cache(cache_key)
            if cached_data:
                cached_data['from_cache'] = True
                cached_data['cache_age'] = self._get_cache_age(cache_key)
                return cached_data
        
        # Language instruction
        lang_instruction = f"\n\n**IMPORTANT: Write the ENTIRE response in {language} language ONLY. Do NOT mix languages. All text, headings, and content must be in {language}.**"
        
        try:
            # Build search query with structured output format
            if crop_type:
                search_query = f"""Search for current government agricultural schemes for {crop_type} farmers in {location}, India.

**Search the web and provide a well-structured response for farmers:**

## 🇮🇳 CENTRAL GOVERNMENT SCHEMES
List 3-4 major central schemes (PM-KISAN, PMFBY, Kisan Credit Card, etc.)
For each scheme:
- **Scheme Name & Full Form**
- **Key Benefits** (in simple terms)
- **Who Can Apply** (eligibility in simple terms)
- **How to Apply** (step-by-step process)
- **Official Website/Helpline**

## 🏛️ STATE SCHEMES FOR {location.upper()}
List 2-3 state-specific schemes for {location}
For each scheme:
- **Scheme Name**
- **Special Benefits for {crop_type} Farmers**
- **Who Can Apply**
- **Application Process**
- **Contact Details**

## 💡 IMPORTANT TIPS
- Best time to apply
- Required documents
- Common mistakes to avoid

Format everything in bullet points and use simple language that farmers can understand.{lang_instruction}"""
            else:
                search_query = f"""Search for current government agricultural schemes available in {location}, India.

**Provide a farmer-friendly structured response:**

## 🇮🇳 MAJOR CENTRAL GOVERNMENT SCHEMES

List 4-5 major schemes like:
- PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)
- PMFBY (Pradhan Mantri Fasal Bima Yojana)
- Kisan Credit Card (KCC)
- PM Kisan Maandhan Yojana
- Soil Health Card Scheme

For each scheme:
- **Benefits:** (what farmers get)
- **Who Can Apply:** (eligibility)
- **How to Apply:** (step-by-step)
- **Website/Helpline:** (contact info)

## 🏛️ {location.upper()} STATE SCHEMES

List state-specific schemes with:
- Scheme name and benefits
- Eligibility criteria
- Application method
- Local contact numbers

## 📞 HELPLINE & SUPPORT
- Kisan Call Center: 1800-180-1551
- State Agriculture Helpline
- Online Portal Links

## ⚠️ IMPORTANT NOTES
- Documents needed: Aadhar, Bank Account, Land Records
- Application deadlines
- Tips for successful application

Use simple language and bullet points. Make it easy for farmers to understand and act.{lang_instruction}"""

            # Use AI with Google Search grounding
            response = self.client.models.generate_content(
                model=self.model,
                contents=search_query,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                    temperature=0.3,
                    response_modalities=["TEXT"]
                )
            )
            
            text = response.text
            
            # Extract sources
            sources = []
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
                    grounding_metadata = candidate.grounding_metadata
                    if hasattr(grounding_metadata, 'grounding_chunks'):
                        for chunk in grounding_metadata.grounding_chunks:
                            if hasattr(chunk, 'web') and chunk.web:
                                sources.append({
                                    'url': chunk.web.uri,
                                    'title': chunk.web.title if hasattr(chunk.web, 'title') else 'Source'
                                })
            
            result = {
                'content': text,
                'sources': sources,
                'location': location,
                'crop_type': crop_type,
                'fetched_at': datetime.now().isoformat(),
                'from_cache': False
            }
            
            # Cache for 2 hours
            self._save_to_cache(cache_key, result, hours=2)
            
            return result
            
        except Exception as e:
            return {
                'error': str(e),
                'content': 'Unable to fetch schemes information. Please try again.',
                'sources': []
            }
    
    def check_eligibility(self, farmer_profile, scheme_name, location):
        """Check if farmer is eligible for a specific scheme."""
        
        try:
            query = f"""Based on this farmer profile, check eligibility for {scheme_name} in {location}, India:

Farmer Profile:
- Location: {location}
- Land Size: {farmer_profile.get('land_size', 'Not specified')}
- Crop Type: {farmer_profile.get('crop_type', 'Not specified')}
- Farmer Category: {farmer_profile.get('category', 'Not specified')}

Please provide:
1. Is this farmer likely eligible? (Yes/No/Partial)
2. Specific eligibility criteria for {scheme_name}
3. What documents are needed?
4. Steps to apply
5. Any special conditions or requirements

Search for the latest {scheme_name} guidelines and eligibility criteria."""

            response = self.client.models.generate_content(
                model=self.model,
                contents=query,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                    temperature=0.3
                )
            )
            
            return {
                'eligibility_check': response.text,
                'scheme_name': scheme_name,
                'farmer_location': location
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def calculate_loan_emi(self, principal, rate, tenure_months):
        """Calculate EMI for agricultural loans."""
        try:
            # EMI formula: P × r × (1 + r)^n / ((1 + r)^n - 1)
            monthly_rate = rate / (12 * 100)
            emi = (principal * monthly_rate * (1 + monthly_rate)**tenure_months) / \
                  ((1 + monthly_rate)**tenure_months - 1)
            
            total_payment = emi * tenure_months
            total_interest = total_payment - principal
            
            return {
                'emi': round(emi, 2),
                'total_payment': round(total_payment, 2),
                'total_interest': round(total_interest, 2),
                'principal': principal,
                'rate': rate,
                'tenure_months': tenure_months
            }
        except:
            return None
    
    def _get_from_cache(self, key):
        """Get data from custom cache."""
        try:
            conn = self.cache._CacheManager__get_connection() if hasattr(self.cache, '_CacheManager__get_connection') else None
            if not conn:
                import sqlite3
                conn = sqlite3.connect('farmermarket.db')
            
            c = conn.cursor()
            c.execute("""SELECT data, expires_at FROM schemes_cache 
                        WHERE cache_key = ? AND expires_at > ?""",
                     (key, datetime.now().isoformat()))
            result = c.fetchone()
            conn.close()
            
            if result:
                return json.loads(result[0])
            return None
        except:
            return None
    
    def _save_to_cache(self, key, data, hours=2):
        """Save data to custom cache."""
        try:
            import sqlite3
            conn = sqlite3.connect('farmermarket.db')
            c = conn.cursor()
            
            # Create table if not exists
            c.execute("""CREATE TABLE IF NOT EXISTS schemes_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cache_key TEXT UNIQUE,
                data TEXT,
                cached_at TEXT,
                expires_at TEXT
            )""")
            
            cached_at = datetime.now()
            expires_at = cached_at + timedelta(hours=hours)
            
            c.execute("""INSERT OR REPLACE INTO schemes_cache 
                        (cache_key, data, cached_at, expires_at)
                        VALUES (?, ?, ?, ?)""",
                     (key, json.dumps(data), cached_at.isoformat(), expires_at.isoformat()))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Cache save error: {e}")
    
    def _get_cache_age(self, key):
        """Get how old the cache is."""
        try:
            import sqlite3
            conn = sqlite3.connect('farmermarket.db')
            c = conn.cursor()
            c.execute("SELECT cached_at FROM schemes_cache WHERE cache_key = ?", (key,))
            result = c.fetchone()
            conn.close()
            
            if result:
                cached_time = datetime.fromisoformat(result[0])
                age = datetime.now() - cached_time
                return f"{int(age.total_seconds() / 60)} minutes ago"
            return None
        except:
            return None


def render_government_schemes_page():
    """Render the government schemes and financial tools page."""
    
    st.header("🏛️ Government Schemes & Financial Tools")
    
    # Initialize helper
    if 'schemes_helper' not in st.session_state:
        st.session_state.schemes_helper = GovernmentSchemesHelper()
    
    helper = st.session_state.schemes_helper
    
    # Tabs for different features
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Available Schemes",
        "✅ Eligibility Checker", 
        "📄 Document Helper",
        "💰 EMI Calculator"
    ])
    
    # TAB 1: Available Schemes
    with tab1:
        st.subheader("📋 Agricultural Schemes Database")
        
        # Get farmer's location from profile
        farmer_name = st.session_state.get("farmer_name")
        default_location = "Maharashtra"
        city_name = None
        state_name = "Maharashtra"
        
        if farmer_name:
            from database.db_functions import get_farmer_profile
            farmer_profile = get_farmer_profile(farmer_name)
            if farmer_profile:
                farmer_location = farmer_profile.get('location', '')
                if farmer_location:
                    # Extract city and state from address
                    location_parts = [part.strip() for part in farmer_location.split(',')]
                    
                    # Find state name
                    for part in location_parts:
                        if any(state in part.lower() for state in ['maharashtra', 'karnataka', 'punjab', 'gujarat', 'tamil nadu', 'kerala', 'rajasthan', 'madhya pradesh', 'uttar pradesh', 'bihar', 'west bengal', 'andhra pradesh', 'telangana', 'odisha', 'haryana']):
                            state_name = part
                            break
                    else:
                        # Use second-to-last part as likely state
                        if len(location_parts) >= 2:
                            state_name = location_parts[-2]
                    
                    # Find city name (look for major cities)
                    for part in location_parts:
                        if any(city in part.lower() for city in ['pune', 'mumbai', 'nashik', 'bangalore', 'delhi', 'ahmedabad', 'hyderabad', 'chennai', 'kolkata', 'jaipur', 'lucknow', 'kanpur', 'nagpur', 'indore', 'bhopal', 'patna', 'surat', 'vadodara']):
                            city_name = part
                            break
                    
                    # Build location string: "City, State" or just "State"
                    if city_name:
                        default_location = f"{city_name}, {state_name}"
                    else:
                        default_location = state_name
        
        # Show immediate loading message
        loading_placeholder = st.empty()
        
        # Get current language
        from components.translation_utils import get_current_language_name
        current_language = get_current_language_name()
        
        # Auto-load schemes for farmer's location
        auto_load = 'auto_loaded_schemes' not in st.session_state
        if auto_load and default_location:
            loading_placeholder.info(f"🔍 Searching government schemes for {default_location}...")
            
            schemes_data = helper.search_government_schemes(default_location, None, force_refresh=False, language=current_language)
            
            loading_placeholder.empty()  # Clear loading message
            
            if 'error' not in schemes_data:
                st.success(f"📍 Government Schemes for: **{default_location}**")
                
                # Display content
                st.markdown("---")
                st.markdown(schemes_data['content'])
                
                # Show sources
                if schemes_data.get('sources'):
                    st.markdown("---")
                    st.subheader("📚 Sources & References")
                    for source in schemes_data['sources']:
                        st.markdown(f"- [{source['title']}]({source['url']})")
                
                st.session_state['last_schemes_data'] = schemes_data
                st.session_state['auto_loaded_schemes'] = True
            else:
                loading_placeholder.error(f"❌ Could not load schemes. Please try manual search below.")
            
            st.markdown("---")
        
        # Manual search section
        st.markdown("### 🔍 Search Schemes for Other Locations")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            location = st.text_input(
                "Location (State/District)",
                value=default_location,
                help="Enter your state or district name"
            )
        
        with col2:
            crop_type = st.selectbox(
                "Crop Type (Optional)",
                ["All Crops", "Wheat", "Rice", "Cotton", "Sugarcane", "Vegetables", "Fruits", "Pulses"],
                help="Select crop for specific schemes"
            )
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            search_btn = st.button("🔍 Search Schemes", type="primary", width="stretch")
        
        with col2:
            refresh_btn = st.button("🔄 Force Refresh", width="stretch",
                                   help="Get latest data (ignores cache)")
        
        # Manual search for schemes
        if search_btn or refresh_btn:
            with st.spinner("Searching government schemes..."):
                crop = None if crop_type == "All Crops" else crop_type
                schemes_data = helper.search_government_schemes(
                    location, 
                    crop, 
                    force_refresh=refresh_btn,
                    language=current_language
                )
                
                if 'error' not in schemes_data:
                    # Show cache status
                    if schemes_data.get('from_cache'):
                        st.info(f"📦 Using cached data (Updated: {schemes_data.get('cache_age', 'recently')})")
                    else:
                        st.success("✅ Fresh data fetched from web")
                    
                    # Display content
                    st.markdown("---")
                    st.markdown(schemes_data['content'])
                    
                    # Show sources
                    if schemes_data.get('sources'):
                        st.markdown("---")
                        st.subheader("📚 Sources")
                        for source in schemes_data['sources']:
                            st.markdown(f"- [{source['title']}]({source['url']})")
                    
                    # Save to session
                    st.session_state['last_schemes_data'] = schemes_data
                else:
                    st.error(f"Error: {schemes_data.get('error')}")
        
        # Show last searched data
        elif 'last_schemes_data' in st.session_state:
            data = st.session_state['last_schemes_data']
            if data.get('from_cache'):
                st.info(f"📦 Showing cached data (Updated: {data.get('cache_age', 'recently')})")
            st.markdown(data['content'])
            
            if data.get('sources'):
                st.markdown("---")
                st.subheader("📚 Sources")
                for source in data['sources']:
                    st.markdown(f"- [{source['title']}]({source['url']})")
    
    # TAB 2: Eligibility Checker
    with tab2:
        st.subheader("✅ Check Your Eligibility")
        
        st.write("Enter your details to check eligibility for specific schemes:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            farmer_location = st.text_input("Location", value="Maharashtra")
            land_size = st.number_input("Land Size (acres)", min_value=0.0, value=2.0, step=0.5)
            crop = st.selectbox("Primary Crop", ["Wheat", "Rice", "Cotton", "Sugarcane", "Vegetables", "Fruits", "Pulses"])
        
        with col2:
            category = st.selectbox("Farmer Category", ["Small", "Marginal", "Medium", "Large"])
            scheme_name = st.text_input("Scheme Name", 
                                       placeholder="e.g., PM-KISAN, PMFBY, KCC",
                                       help="Enter the scheme you want to check")
        
        if st.button("✅ Check Eligibility", type="primary"):
            if scheme_name:
                with st.spinner("Checking eligibility..."):
                    profile = {
                        'land_size': f"{land_size} acres",
                        'crop_type': crop,
                        'category': category
                    }
                    
                    result = helper.check_eligibility(profile, scheme_name, farmer_location)
                    
                    if 'error' not in result:
                        st.success("✅ Eligibility Check Complete")
                        st.markdown("---")
                        st.markdown(result['eligibility_check'])
                    else:
                        st.error(f"Error: {result['error']}")
            else:
                st.warning("Please enter a scheme name")
    
    # TAB 3: Document Helper
    with tab3:
        st.subheader("📄 Required Documents Guide")
        
        st.write("Select a scheme to see required documents:")
        
        common_schemes = [
            "PM-KISAN (Income Support)",
            "PMFBY (Crop Insurance)",
            "KCC (Kisan Credit Card)",
            "Soil Health Card Scheme",
            "PM Fasal Bima Yojana",
            "Interest Subvention Scheme",
            "Custom Scheme"
        ]
        
        selected_scheme = st.selectbox("Select Scheme", common_schemes)
        
        if selected_scheme == "Custom Scheme":
            custom_scheme = st.text_input("Enter Scheme Name")
            scheme_for_docs = custom_scheme
        else:
            scheme_for_docs = selected_scheme
        
        if st.button("📄 Get Document Requirements"):
            if scheme_for_docs:
                with st.spinner("Fetching document requirements..."):
                    query = f"""What documents are required to apply for {scheme_for_docs} in India?

Please provide:
1. List of all required documents
2. Self-attested or original requirements
3. Additional documents for specific cases
4. Where to submit documents
5. Online submission options if available

Search for latest official requirements."""

                    try:
                        response = helper.client.models.generate_content(
                            model=helper.model,
                            contents=query,
                            config=types.GenerateContentConfig(
                                tools=[types.Tool(google_search=types.GoogleSearch())],
                                temperature=0.3
                            )
                        )
                        
                        st.success("✅ Document Requirements")
                        st.markdown("---")
                        st.markdown(response.text)
                        
                    except Exception as e:
                        st.error(f"Error: {e}")
    
    # TAB 4: AI-Powered Loan Calculator
    with tab4:
        st.subheader("💰 Smart Agricultural Loan Calculator")
        st.caption("AI searches real interest rates and calculates EMI for your location")
        
        # Get farmer's location
        farmer_location_for_loan = default_location if 'default_location' in locals() else "Maharashtra"
        
        st.info(f"📍 Getting loan information for: **{farmer_location_for_loan}**")
        
        # Loan type selection
        loan_types = [
            "Kisan Credit Card (KCC)",
            "Crop Loan",
            "Equipment Purchase Loan",
            "Land Development Loan",
            "Dairy Loan",
            "Poultry Loan",
            "General Agricultural Loan"
        ]
        
        col1, col2 = st.columns(2)
        
        with col1:
            loan_type = st.selectbox("Select Loan Type", loan_types)
            loan_amount = st.number_input(
                "Loan Amount (₹)",
                min_value=10000,
                max_value=10000000,
                value=200000,
                step=10000,
                help="Enter the amount you need"
            )
        
        with col2:
            loan_purpose = st.text_input(
                "Loan Purpose (Optional)",
                placeholder="e.g., Buy tractor, Seeds, Irrigation",
                help="Helps get more specific information"
            )
            tenure_years = st.number_input(
                "Desired Tenure (years)",
                min_value=1,
                max_value=20,
                value=3,
                help="How many years to repay"
            )
        
        if st.button("🔍 Search Rates & Calculate EMI", type="primary", use_container_width=True):
            with st.spinner(f"🔍 Searching current {loan_type} rates in {farmer_location_for_loan}..."):
                
                # Build AI query to search for real loan data
                search_query = f"""Search for current agricultural loan information for {loan_type} in {farmer_location_for_loan}, India.

**Find and provide the following information:**

## 💰 LOAN DETAILS FOR {loan_type.upper()}

### Current Interest Rates
- Search for current interest rates from major banks (SBI, HDFC, ICICI, Punjab National Bank, Bank of Maharashtra)
- Government subsidy rates (if applicable)
- Interest subvention schemes available
- Special rates for {farmer_location_for_loan}

### Loan Terms & Conditions
- Maximum loan amount available
- Typical tenure options
- Processing fees
- Collateral requirements
- Documentation needed

### EMI Calculation
Based on:
- **Loan Amount:** ₹{loan_amount:,}
- **Tenure:** {tenure_years} years ({tenure_years * 12} months)
- **Current Average Interest Rate:** [Find real rate]

Calculate and show:
1. **Monthly EMI Amount**
2. **Total Interest Payable**
3. **Total Amount Payable**
4. **EMI Breakdown Table** (First 6 months showing principal + interest split)

### Available Schemes & Subsidies
- Interest subvention schemes
- Government subsidies for {loan_purpose if loan_purpose else loan_type}
- Special schemes in {farmer_location_for_loan}

### Where to Apply
- List 3-4 banks offering best rates in {farmer_location_for_loan}
- Online application links
- Branch contact information
- Required documents

### 💡 RECOMMENDATIONS
- Best time to apply
- Tips to get better interest rates
- How to improve loan eligibility

**Format the response in a clear, structured way with:**
- Headings and subheadings
- Bullet points
- Tables for EMI breakdown
- Actual numbers and calculations
- Simple language for farmers"""

                try:
                    response = helper.client.models.generate_content(
                        model=helper.model,
                        contents=search_query,
                        config=types.GenerateContentConfig(
                            tools=[types.Tool(google_search=types.GoogleSearch())],
                            temperature=0.2,  # Lower temperature for accurate calculations
                            response_modalities=["TEXT"]
                        )
                    )
                    
                    st.success("✅ Loan Information & EMI Calculation")
                    st.markdown("---")
                    
                    # Display AI response
                    st.markdown(response.text)
                    
                    # Show sources if available
                    if hasattr(response, 'grounding_metadata') and response.grounding_metadata:
                        st.markdown("---")
                        st.subheader("📚 Information Sources")
                        for source in response.grounding_metadata.grounding_supports:
                            if hasattr(source, 'uri'):
                                st.markdown(f"- [{source.title if hasattr(source, 'title') else 'Source'}]({source.uri})")
                    
                except Exception as e:
                    st.error(f"❌ Error fetching loan information: {str(e)}")
                    
                    # Fallback: Basic EMI calculation
                    st.warning("⚠️ Using fallback calculator with estimated rate (7% p.a.)")
                    
                    rate = 7.0  # Default rate
                    tenure_months = tenure_years * 12
                    monthly_rate = rate / (12 * 100)
                    
                    if monthly_rate > 0:
                        emi = loan_amount * monthly_rate * ((1 + monthly_rate) ** tenure_months) / (((1 + monthly_rate) ** tenure_months) - 1)
                        total_payment = emi * tenure_months
                        total_interest = total_payment - loan_amount
                        
                        st.markdown("---")
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Monthly EMI", f"₹{emi:,.2f}")
                        with col2:
                            st.metric("Total Interest", f"₹{total_interest:,.2f}")
                        with col3:
                            st.metric("Total Payment", f"₹{total_payment:,.2f}")
                        
                        st.info("💡 **Note:** This is an estimate. Actual rates may vary. Please search again or contact your bank.")
        
        # Quick comparison section
        st.markdown("---")
        st.markdown("### 🏦 Quick Loan Comparison")
        st.caption("Common agricultural loan types and typical rates")
        
        comparison_data = {
            "Loan Type": ["Kisan Credit Card", "Crop Loan", "Tractor Loan", "Land Development"],
            "Typical Rate (%)": ["4-7%", "7-9%", "8-10%", "9-11%"],
            "Max Amount": ["₹3 Lakhs", "As per crop", "₹10-15 Lakhs", "₹50 Lakhs+"],
            "Tenure": ["1 year", "6-12 months", "7-9 years", "10-15 years"]
        }
        
        import pandas as pd
        df = pd.DataFrame(comparison_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.caption("💡 **Tip:** Rates shown are approximate. Click 'Search Rates' above for current rates in your area.")


