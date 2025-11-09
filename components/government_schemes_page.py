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
        # Try AI 2.5 Flash first, fallback to 2.0 Flash
        try:
            self.client.models.generate_content(
                model='AI-2.5-flash',
                contents="test",
                config=types.GenerateContentConfig(temperature=0.1)
            )
            self.model = 'AI-2.5-flash'
            print("✅ Using AI 2.5 Flash")
        except:
            self.model = 'AI-2.0-flash-exp'
            print("⚠️ Fallback to AI 2.0 Flash")
        self.cache = CacheManager()
    
    def search_government_schemes(self, location, crop_type=None, force_refresh=False):
        """
        Search for government agricultural schemes using Google Search grounding.
        
        Args:
            location: Farmer's location (state/district)
            crop_type: Optional crop type for specific schemes
            force_refresh: Force fetch fresh data instead of using cache
        
        Returns:
            dict: Schemes information with sources
        """
        cache_key = f"schemes_{location}_{crop_type or 'general'}"
        
        # Check cache first (unless force refresh)
        if not force_refresh:
            cached_data = self._get_from_cache(cache_key)
            if cached_data:
                cached_data['from_cache'] = True
                cached_data['cache_age'] = self._get_cache_age(cache_key)
                return cached_data
        
        try:
            # Build search query
            if crop_type:
                search_query = f"""Find current government agricultural schemes for {crop_type} farmers in {location}, India:

1. List active central government schemes (PM-KISAN, PMFBY, KCC, etc.)
2. List state-specific schemes for {location}
3. For each scheme provide:
   - Scheme name
   - Key benefits
   - Eligibility criteria
   - Application process
   - Contact information
4. Include recent updates or new schemes from 2024-2025

Focus on schemes specifically beneficial for {crop_type} cultivation."""
            else:
                search_query = f"""Find current government agricultural schemes in {location}, India:

1. List all active central government schemes for farmers
2. List state-specific agricultural schemes for {location}
3. For each major scheme provide:
   - Scheme name
   - Key benefits
   - Eligibility criteria
   - How to apply
4. Include recent updates from 2024-2025
5. Mention helpline numbers or online portals"""

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
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            location = st.text_input(
                "Your Location (State/District)",
                value=st.session_state.get('user_location', 'Maharashtra'),
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
            search_btn = st.button("🔍 Search Schemes", type="primary", use_container_width=True)
        
        with col2:
            refresh_btn = st.button("🔄 Force Refresh", use_container_width=True,
                                   help="Get latest data (ignores cache)")
        
        # Search for schemes
        if search_btn or refresh_btn:
            with st.spinner("Searching government schemes..."):
                crop = None if crop_type == "All Crops" else crop_type
                schemes_data = helper.search_government_schemes(
                    location, 
                    crop, 
                    force_refresh=refresh_btn
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
    
    # TAB 4: EMI Calculator
    with tab4:
        st.subheader("💰 Agricultural Loan EMI Calculator")
        
        st.write("Calculate your monthly EMI for agricultural loans:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            principal = st.number_input(
                "Loan Amount (₹)",
                min_value=10000,
                max_value=10000000,
                value=200000,
                step=10000
            )
            
            rate = st.number_input(
                "Interest Rate (% per annum)",
                min_value=1.0,
                max_value=20.0,
                value=7.0,
                step=0.5
            )
        
        with col2:
            tenure_years = st.number_input(
                "Loan Tenure (years)",
                min_value=1,
                max_value=20,
                value=5
            )
            
            tenure_months = tenure_years * 12
        
        if st.button("💰 Calculate EMI", type="primary"):
            result = helper.calculate_loan_emi(principal, rate, tenure_months)
            
            if result:
                st.success("✅ EMI Calculation")
                st.markdown("---")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Monthly EMI", f"₹{result['emi']:,.2f}")
                
                with col2:
                    st.metric("Total Payment", f"₹{result['total_payment']:,.2f}")
                
                with col3:
                    st.metric("Total Interest", f"₹{result['total_interest']:,.2f}")
                
                # Breakdown
                st.markdown("---")
                st.subheader("Payment Breakdown")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Principal Amount:** ₹{principal:,.2f}")
                    st.write(f"**Interest Rate:** {rate}% per annum")
                    st.write(f"**Loan Tenure:** {tenure_years} years ({tenure_months} months)")
                
                with col2:
                    st.write(f"**Monthly EMI:** ₹{result['emi']:,.2f}")
                    st.write(f"**Total Interest:** ₹{result['total_interest']:,.2f}")
                    interest_percent = (result['total_interest'] / principal) * 100
                    st.write(f"**Interest %:** {interest_percent:.1f}% of principal")
                
                # Tips
                st.info("💡 **Tip:** Lower interest rates and shorter tenures reduce total interest paid. Check for government subsidy schemes!")
    
    # Information footer
    st.markdown("---")
    st.info("""
    💡 **Smart Caching System:**
    - Schemes data is cached for 2 hours
    - Click "Force Refresh" to get latest information
    - Cache age is shown when viewing cached data
    - Saves API costs and improves performance
    """)


