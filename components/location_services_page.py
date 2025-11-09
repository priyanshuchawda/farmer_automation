# components/location_services_page.py
"""
Location Services Page - Demonstrates Google Maps Grounding with Gemini 2.5 Flash
Provides location-aware services for farmers including:
- Nearby agricultural services
- Market locations
- Veterinary clinics
- Input suppliers
- Government offices
"""

import streamlit as st
from components.location_manager import LocationManager, get_farmer_location_context

def render_location_services_page():
    """Render location-based services using Google Maps Grounding"""
    
    st.title("🗺️ Location Services")
    st.markdown("**Powered by Google Maps & Gemini 2.5 Flash**")
    
    # Check if user has location set
    farmer_name = st.session_state.get('farmer_name')
    if not farmer_name:
        st.warning("⚠️ Please login to use location services.")
        return
    
    location_context = get_farmer_location_context(farmer_name)
    
    if not location_context:
        st.warning("⚠️ Please set your location in your profile first.")
        if st.button("📍 Go to Profile Settings"):
            st.session_state['page'] = 'view_profile'
            st.rerun()
        return
    
    latitude, longitude, location_name = location_context
    
    # Display current location
    st.success(f"📍 **Your Location:** {location_name}")
    st.info(f"🌐 **Coordinates:** {latitude:.6f}, {longitude:.6f}")
    
    # Create tabs for different services
    tabs = st.tabs([
        "🔍 Nearby Places",
        "🏪 Agricultural Services", 
        "🏥 Veterinary Services",
        "🏛️ Government Offices",
        "🎯 Custom Search"
    ])
    
    # Tab 1: Nearby Places
    with tabs[0]:
        st.subheader("🔍 Explore Nearby")
        
        quick_searches = {
            "🛒 Markets": "Agricultural markets and mandis near me",
            "🌾 Input Stores": "Agricultural input and seed stores nearby",
            "🚜 Equipment Dealers": "Farm equipment and tractor dealers within 10km",
            "⛽ Petrol Pumps": "Petrol and diesel pumps near me",
            "🏦 Banks": "Banks and ATMs nearby",
            "🍽️ Restaurants": "Restaurants and food places near me"
        }
        
        cols = st.columns(3)
        for idx, (emoji_name, query) in enumerate(quick_searches.items()):
            with cols[idx % 3]:
                if st.button(emoji_name, width="stretch"):
                    st.session_state['quick_search'] = query
                    st.session_state['search_triggered'] = True
        
        if st.session_state.get('search_triggered', False):
            query = st.session_state.get('quick_search', '')
            if query:
                with st.spinner(f"🔍 Searching: {query}..."):
                    location_manager = LocationManager()
                    result = location_manager.find_nearby_places(latitude, longitude, query)
                    
                    if result and isinstance(result, dict):
                        st.markdown("---")
                        st.markdown(result['text'])
                        
                        if result.get('sources'):
                            st.markdown("---")
                            st.markdown("**🗺️ Places Found (from Google Maps):**")
                            for source in result['sources']:
                                col1, col2 = st.columns([4, 1])
                                with col1:
                                    st.markdown(f"**{source['title']}**")
                                with col2:
                                    st.link_button("View", source['uri'], width="stretch")
                    else:
                        st.error("❌ Could not find nearby places.")
                
                st.session_state['search_triggered'] = False
    
    # Tab 2: Agricultural Services
    with tabs[1]:
        st.subheader("🏪 Agricultural Services")
        
        st.markdown("""
        Find agricultural services and facilities near your location:
        - Seed and fertilizer stores
        - Agricultural equipment dealers
        - Cold storage facilities
        - Processing units
        """)
        
        service_type = st.selectbox(
            "Select Service Type:",
            [
                "Seed and Fertilizer Stores",
                "Agricultural Equipment Dealers",
                "Cold Storage Facilities",
                "Agricultural Processing Units",
                "Soil Testing Labs",
                "Organic Input Suppliers"
            ]
        )
        
        radius = st.slider("Search Radius (km)", 1, 50, 10)
        
        if st.button("🔍 Search Agricultural Services", width="stretch"):
            query = f"{service_type} within {radius}km of my location"
            
            with st.spinner(f"🔍 Finding {service_type}..."):
                location_manager = LocationManager()
                result = location_manager.find_nearby_places(latitude, longitude, query)
                
                if result and isinstance(result, dict):
                    st.markdown("---")
                    st.markdown(result['text'])
                    
                    if result.get('sources'):
                        st.markdown("---")
                        st.markdown(f"**🗺️ {service_type} Found:**")
                        for idx, source in enumerate(result['sources'], 1):
                            with st.expander(f"{idx}. {source['title']}"):
                                st.link_button("📍 View on Google Maps", source['uri'], width="stretch")
    
    # Tab 3: Veterinary Services
    with tabs[2]:
        st.subheader("🏥 Veterinary Services")
        
        st.markdown("""
        Find veterinary care for your livestock:
        - Veterinary hospitals and clinics
        - Animal dispensaries
        - Emergency animal care
        - Veterinary pharmacies
        """)
        
        vet_service = st.radio(
            "What do you need?",
            [
                "Veterinary Hospitals",
                "Veterinary Clinics", 
                "Animal Dispensaries",
                "Emergency Veterinary Care",
                "Veterinary Pharmacies"
            ]
        )
        
        if st.button("🔍 Find Veterinary Services", width="stretch"):
            query = f"{vet_service} near me with ratings and reviews"
            
            with st.spinner(f"🔍 Finding {vet_service}..."):
                location_manager = LocationManager()
                result = location_manager.find_nearby_places(latitude, longitude, query)
                
                if result and isinstance(result, dict):
                    st.markdown("---")
                    st.markdown(result['text'])
                    
                    if result.get('sources'):
                        st.markdown("---")
                        st.markdown(f"**🏥 {vet_service} Found:**")
                        for idx, source in enumerate(result['sources'], 1):
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.markdown(f"**{idx}. {source['title']}**")
                            with col2:
                                st.link_button("View", source['uri'], width="stretch")
    
    # Tab 4: Government Offices
    with tabs[3]:
        st.subheader("🏛️ Government Offices")
        
        st.markdown("""
        Locate government offices and services:
        - Agriculture department offices
        - Tehsil/Taluka offices
        - Krishi Bhavan
        - Agricultural extension centers
        """)
        
        gov_service = st.selectbox(
            "Select Office Type:",
            [
                "Agriculture Department Office",
                "Tehsil Office",
                "Taluka Office",
                "Krishi Bhavan",
                "Agricultural Extension Center",
                "Horticulture Department",
                "Animal Husbandry Office"
            ]
        )
        
        if st.button("🔍 Find Government Office", width="stretch"):
            query = f"{gov_service} near me with address and contact details"
            
            with st.spinner(f"🔍 Finding {gov_service}..."):
                location_manager = LocationManager()
                result = location_manager.find_nearby_places(latitude, longitude, query)
                
                if result and isinstance(result, dict):
                    st.markdown("---")
                    st.markdown(result['text'])
                    
                    if result.get('sources'):
                        st.markdown("---")
                        st.markdown(f"**🏛️ {gov_service} Found:**")
                        for source in result['sources']:
                            with st.expander(source['title']):
                                st.link_button("📍 Get Directions", source['uri'], width="stretch")
    
    # Tab 5: Custom Search
    with tabs[4]:
        st.subheader("🎯 Custom Location Search")
        
        st.markdown("""
        **Enter your custom search query:**
        
        Examples:
        - "Best irrigation equipment dealers near me"
        - "Organic fertilizer suppliers within 20km"
        - "Agricultural cooperatives in my area"
        - "Dairy collection centers nearby"
        """)
        
        custom_query = st.text_area(
            "Your Search Query:",
            placeholder="e.g., Find the best agricultural consultants near me with good reviews",
            height=100
        )
        
        col1, col2 = st.columns([3, 1])
        with col1:
            include_ratings = st.checkbox("Include ratings and reviews", value=True)
        with col2:
            include_hours = st.checkbox("Include opening hours", value=True)
        
        if st.button("🔍 Search Now", width="stretch", type="primary"):
            if custom_query:
                # Enhance query with additional requirements
                enhanced_query = custom_query
                if include_ratings:
                    enhanced_query += " with ratings and reviews"
                if include_hours:
                    enhanced_query += " with opening hours"
                
                with st.spinner("🔍 Searching..."):
                    location_manager = LocationManager()
                    result = location_manager.find_nearby_places(latitude, longitude, enhanced_query)
                    
                    if result and isinstance(result, dict):
                        st.markdown("---")
                        st.success("✅ **Search Results:**")
                        st.markdown(result['text'])
                        
                        if result.get('sources'):
                            st.markdown("---")
                            st.markdown("**🗺️ Found Locations:**")
                            
                            for idx, source in enumerate(result['sources'], 1):
                                with st.container():
                                    col1, col2 = st.columns([4, 1])
                                    with col1:
                                        st.markdown(f"**{idx}. {source['title']}**")
                                    with col2:
                                        st.link_button("📍 Open", source['uri'], width="stretch")
                                    st.markdown("---")
                        
                        if result.get('widget_token'):
                            st.info("🗺️ Interactive map widget available (requires Google Maps JavaScript API)")
                    else:
                        st.error("❌ Could not complete the search. Please try again.")
            else:
                st.warning("⚠️ Please enter a search query.")
    
    # Footer with tips
    st.markdown("---")
    with st.expander("💡 Tips for Better Search Results"):
        st.markdown("""
        **Get the best results from location services:**
        
        1. **Be Specific**: Instead of "stores near me", try "agricultural seed stores near me"
        2. **Add Distance**: Specify distance like "within 5km" or "within 10 miles"
        3. **Include Criteria**: Add "with good reviews", "open now", "with parking"
        4. **Use Local Terms**: Use local names like "mandi", "krushi kendra", etc.
        5. **Multiple Searches**: Try different search terms if first search doesn't give results
        
        **Examples of Good Searches:**
        - ✅ "Organic fertilizer dealers within 15km with reviews"
        - ✅ "24-hour veterinary emergency services near me"
        - ✅ "Government agricultural offices with contact details"
        - ❌ "stores" (too vague)
        - ❌ "help" (not specific)
        """)
    
    # Attribution
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.85rem;'>
        <p>Powered by <strong>Gemini 2.5 Flash</strong> with <strong>Google Maps Grounding</strong></p>
        <p style='font-size: 0.75rem;'>Location data and recommendations from Google Maps</p>
    </div>
    """, unsafe_allow_html=True)
