# components/tool_listings.py
import streamlit as st
from database.db_functions import add_data, get_data
import pandas as pd
try:
    from ai.ai_matcher import get_recommendations  # ✅ AI integration
except ImportError:
    # Fallback if module not found
    def get_recommendations(*args, **kwargs):
        return []
from components.translation_utils import t


def render_tool_listing(farmer_name):
    """Renders the form to add a new tool or machine listing with AI suggestions."""
    # Mobile responsive CSS for tool listings
    st.markdown("""
    <style>
    @media (max-width: 768px) {
        /* Stack form columns */
        [data-testid="column"] {
            width: 100% !important;
            margin-bottom: 10px;
        }
        
        /* Form input spacing */
        .stTextInput, .stNumberInput, .stSelectbox, .stTextArea {
            margin-bottom: 10px;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader(t("Add a Farm Tool for Rent"))

    profile = st.session_state.get("farmer_profile", {})
    location_value = profile.get("location", "") if profile else ""
    contact_value = profile.get("contact", "") if profile else ""

    with st.form("tool_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            name = st.text_input(t("Your Name"), value=farmer_name, key="tool_name_input")
            location = st.text_input(t("Your Location (Village)"), value=location_value, key="tool_loc_input")
        with col2:
            tool_name = st.selectbox(
                t("Tool Type"),
                ["Tractor", "Plow", "Seeder", "Sprayer", "Harvester", "Other"],
                key="tool_type_select"
            )
            rent_rate = st.number_input(t("Rent Rate (per day)"), min_value=0.0, format="%.2f", key="tool_rate_input")
        with col3:
            contact = st.text_input(t("Contact Number"), value=contact_value, key="tool_contact_input")
            notes = st.text_area(t("Additional Notes (e.g., condition, availability)"), height=80)
        
        submitted = st.form_submit_button(t("Add Tool Listing"))

        if submitted:
            if name and location and tool_name and rent_rate > 0 and contact:
                tool_data = (name, location, tool_name, rent_rate, contact, notes)
                add_data("tools", tool_data)
                st.session_state.tools = get_data("tools")

                recs = get_recommendations({
                    "type": "tool",
                    "farmer": name,
                    "location": location,
                    "item": tool_name,
                    "notes": notes
                })
                st.info(f"{t('Smart Suggestion')}: {recs}")

                st.success(f"{t('Tool')} '{tool_name}' {t('added successfully by')} {name}!")
            else:
                st.error(t("Please fill in all required fields."))

    st.markdown('</div>', unsafe_allow_html=True)


def render_tool_management(tools_df, farmer_name):
    """Renders the full tool management view with filtering and detailed view."""
    st.subheader(t("All Tool Listings"))

    if not tools_df.empty:
        from database.db_functions import get_farmer_rating
        
        tools_without_rowid = tools_df.drop(columns=['rowid'])
        
        # Add rating info to each listing
        tools_with_ratings = tools_without_rowid.copy()
        tools_with_ratings['avg_rating'] = tools_with_ratings['Farmer'].apply(
            lambda x: get_farmer_rating(x).get('avg_rating', 0.0)
        )
        tools_with_ratings['total_ratings'] = tools_with_ratings['Farmer'].apply(
            lambda x: get_farmer_rating(x).get('total_ratings', 0)
        )
        
        # Filter options
        tool_locations = [t("All")] + sorted(tools_with_ratings["Location"].unique().tolist())
        tool_types = [t("All")] + sorted(tools_with_ratings["Tool"].unique().tolist())
        
        # Enhanced filter UI
        st.markdown("#### 🔍 " + t("Filter & Sort Options"))
        filter_cols = st.columns(5)
        
        with filter_cols[0]:
            selected_tool_loc = st.selectbox(t("📍 Location"), tool_locations, key="tool_loc_filter")
        with filter_cols[1]:
            selected_tool_type = st.selectbox(t("🚜 Tool Type"), tool_types, key="tool_type_filter")
        with filter_cols[2]:
            show_my_listings = st.checkbox(t("👤 My Listings Only"), value=False, key="tool_my_listings")
        with filter_cols[3]:
            sort_by = st.selectbox(
                t("📊 Sort By"),
                [t("Newest First"), t("Price: Low to High"), t("Price: High to Low"), 
                 t("Top Rated"), t("Most Reviewed"), t("Location A-Z")],
                key="tool_sort_by"
            )
        with filter_cols[4]:
            min_rating = st.select_slider(
                t("⭐ Min Rating"),
                options=[0, 1, 2, 3, 4, 5],
                value=0,
                key="tool_min_rating"
            )
        
        # Apply filters
        filtered_tools = tools_with_ratings.copy()
        if selected_tool_loc != t("All"):
            filtered_tools = filtered_tools[filtered_tools["Location"] == selected_tool_loc]
        if selected_tool_type != t("All"):
            filtered_tools = filtered_tools[filtered_tools["Tool"] == selected_tool_type]
        if show_my_listings and farmer_name:
            filtered_tools = filtered_tools[filtered_tools["Farmer"].str.lower() == farmer_name.lower()]
        if min_rating > 0:
            filtered_tools = filtered_tools[filtered_tools["avg_rating"] >= min_rating]
        
        # Apply sorting
        if sort_by == t("Price: Low to High"):
            filtered_tools = filtered_tools.sort_values("Rate", ascending=True)
        elif sort_by == t("Price: High to Low"):
            filtered_tools = filtered_tools.sort_values("Rate", ascending=False)
        elif sort_by == t("Top Rated"):
            filtered_tools = filtered_tools.sort_values("avg_rating", ascending=False)
        elif sort_by == t("Most Reviewed"):
            filtered_tools = filtered_tools.sort_values("total_ratings", ascending=False)
        elif sort_by == t("Location A-Z"):
            filtered_tools = filtered_tools.sort_values("Location", ascending=True)
        else:  # Newest First
            filtered_tools = filtered_tools.iloc[::-1]

        # Display results count
        st.info(f"📋 {t('Showing')} {len(filtered_tools)} {t('of')} {len(tools_with_ratings)} {t('listings')}")
        
        # Display listings as cards with "View Details" button
        for idx, tool in filtered_tools.iterrows():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                # Rating stars display
                rating_display = "⭐" * int(tool['avg_rating']) + "☆" * (5 - int(tool['avg_rating']))
                rating_text = f"{rating_display} {tool['avg_rating']:.1f}/5" if tool['total_ratings'] > 0 else "⭐ No ratings yet"
                
                st.markdown(f"""
                <div style='background: #f9f9f9; padding: 15px; border-radius: 10px; 
                            margin: 10px 0; border-left: 5px solid #4CAF50;'>
                    <h3 style='margin: 0 0 5px 0; color: #2E8B57;'>🚜 {tool['Tool']}</h3>
                    <p style='margin: 3px 0;'><strong>📍</strong> {tool['Location']}</p>
                    <p style='margin: 3px 0;'><strong>💰</strong> ₹{tool['Rate']}/day</p>
                    <p style='margin: 3px 0;'><strong>👤</strong> {tool['Farmer']}</p>
                    <p style='margin: 3px 0;'><strong>{rating_text}</strong> ({tool['total_ratings']} {t('reviews')})</p>
                    <p style='margin: 3px 0; font-size: 14px; color: #666;'>{tool.get('Notes', 'No details')[:100]}...</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("")
                st.markdown("")
                if st.button(f"👁️ {t('View')}", key=f"view_tool_{idx}", use_container_width=True):
                    # Store listing data in session state for detailed view
                    st.session_state.selected_listing = {
                        'type': 'tool',
                        'data': tool.to_dict()
                    }
                    st.session_state.show_listing_detail = True
                    st.rerun()
    else:
        st.info(t("No tools listed yet."))

    st.markdown('<hr>', unsafe_allow_html=True)
    if farmer_name:
        st.subheader(f"{t('Your Tool Listings (Editable by')} {farmer_name})")
        editable_tools = tools_df[tools_df["Farmer"] == farmer_name]

        if not editable_tools.empty:
            editable_for_display = editable_tools.drop(columns=['rowid'])

            updated_tools_df = st.data_editor(
                editable_for_display,
                key="tool_editor",
                use_container_width=True,
                num_rows="dynamic"
            )
            st.session_state.tools.loc[updated_tools_df.index, updated_tools_df.columns] = updated_tools_df.values
        else:
            st.info(t("You have no tool listings yet."))
    else:
        st.warning(t("Please log in to view and manage your listings."))


