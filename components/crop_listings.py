# components/crop_listings.py
import streamlit as st
from database.db_functions import add_data, get_data
from datetime import date
import pandas as pd
try:
    from ai.ai_matcher import get_recommendations  # ✅ AI integration
except ImportError:
    # Fallback if module not found
    def get_recommendations(*args, **kwargs):
        return []
from components.translation_utils import t


def render_crop_listing(farmer_name):
    """Renders the form to add a new crop listing with AI recommendations."""
    # Mobile responsive CSS for crop listings
    st.markdown("""
    <style>
    @media (max-width: 768px) {
        /* Stack form columns */
        [data-testid="column"] {
            width: 100% !important;
            margin-bottom: 10px;
        }
        
        /* Form input spacing */
        .stTextInput, .stNumberInput, .stSelectbox {
            margin-bottom: 10px;
        }
        
        /* Button sizing */
        .stButton>button {
            font-size: 0.9rem !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader(t("Add Crop for Sale"))

    profile = st.session_state.get("farmer_profile", {})
    location_value = profile.get("location", "") if profile else ""
    contact_value = profile.get("contact", "") if profile else ""
    
    with st.form("crop_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            name = st.text_input(t("Your Name"), value=farmer_name, key="crop_name_input")
            location = st.text_input(t("Your Location (Village)"), value=location_value, key="crop_loc_input")
        with col2:
            crop_name = st.text_input(t("Crop Name (e.g., Wheat, Rice)"), key="crop_type_input")
            quantity = st.number_input(t("Quantity"), min_value=0.0, format="%.2f", key="crop_qty_input")
            unit = st.selectbox(t("Unit"), [t("Quintals"), t("Kilograms"), t("Tonnes")], key="crop_unit_select")
        with col3:
            expected_price = st.number_input(t("Expected Price (per unit)"), min_value=0.0, format="%.2f", key="crop_price_input")
            contact = st.text_input(t("Contact Number"), value=contact_value, key="crop_contact_input")
        
        submitted = st.form_submit_button(t("Add Crop Listing"))
        
        if submitted:
            if name and location and crop_name and quantity > 0 and expected_price > 0 and contact:
                listing_date = date.today().strftime("%Y-%m-%d")
                quantity_str = f"{quantity} {unit}"
                crop_data = (name, location, crop_name, quantity_str, expected_price, contact, listing_date)
                
                add_data("crops", crop_data)
                st.session_state.crops = get_data("crops")
                
                recs = get_recommendations({
                    "type": "crop",
                    "farmer": name,
                    "location": location,
                    "item": crop_name,
                    "quantity": quantity_str,
                    "expected_price": expected_price
                })
                st.info(f"{t('Smart Suggestion')}: {recs}")
                
                total_value = quantity * expected_price
                st.success(f"{t('Crop')} '{crop_name}' {t('listed successfully! Estimated value')}: ₹{total_value:,.2f}")
            else:
                st.error(t("Please fill in all required fields."))
    st.markdown('</div>', unsafe_allow_html=True)


def render_crop_management(crops_df, farmer_name):
    """Renders the full crop management view with filtering and detailed view."""
    st.subheader(t("All Crop Listings"))
    
    if not crops_df.empty:
        from database.db_functions import get_farmer_rating
        
        crops_without_rowid = crops_df.drop(columns=['rowid'])
        
        # Add rating info to each listing
        crops_with_ratings = crops_without_rowid.copy()
        crops_with_ratings['avg_rating'] = crops_with_ratings['Farmer'].apply(
            lambda x: get_farmer_rating(x).get('avg_rating', 0.0)
        )
        crops_with_ratings['total_ratings'] = crops_with_ratings['Farmer'].apply(
            lambda x: get_farmer_rating(x).get('total_ratings', 0)
        )
        
        # Filter options
        crop_locations = [t("All")] + sorted(crops_with_ratings["Location"].unique().tolist())
        crop_types = [t("All")] + sorted(crops_with_ratings["Crop"].unique().tolist())
        
        # Enhanced filter UI
        st.markdown("#### 🔍 " + t("Filter & Sort Options"))
        filter_cols = st.columns(5)
        
        with filter_cols[0]:
            selected_crop_loc = st.selectbox(t("📍 Location"), crop_locations, key="crop_loc_filter")
        with filter_cols[1]:
            selected_crop_type = st.selectbox(t("🌾 Crop Type"), crop_types, key="crop_type_filter")
        with filter_cols[2]:
            show_my_listings = st.checkbox(t("👤 My Listings Only"), value=False, key="crop_my_listings")
        with filter_cols[3]:
            sort_by = st.selectbox(
                t("📊 Sort By"),
                [t("Newest First"), t("Price: Low to High"), t("Price: High to Low"), 
                 t("Top Rated"), t("Most Reviewed"), t("Location A-Z")],
                key="crop_sort_by"
            )
        with filter_cols[4]:
            min_rating = st.select_slider(
                t("⭐ Min Rating"),
                options=[0, 1, 2, 3, 4, 5],
                value=0,
                key="crop_min_rating"
            )
        
        # Apply filters
        filtered_crops = crops_with_ratings.copy()
        if selected_crop_loc != t("All"):
            filtered_crops = filtered_crops[filtered_crops["Location"] == selected_crop_loc]
        if selected_crop_type != t("All"):
            filtered_crops = filtered_crops[filtered_crops["Crop"] == selected_crop_type]
        if show_my_listings and farmer_name:
            filtered_crops = filtered_crops[filtered_crops["Farmer"].str.lower() == farmer_name.lower()]
        if min_rating > 0:
            filtered_crops = filtered_crops[filtered_crops["avg_rating"] >= min_rating]
        
        # Apply sorting
        if sort_by == t("Price: Low to High"):
            filtered_crops = filtered_crops.sort_values("Expected_Price", ascending=True)
        elif sort_by == t("Price: High to Low"):
            filtered_crops = filtered_crops.sort_values("Expected_Price", ascending=False)
        elif sort_by == t("Top Rated"):
            filtered_crops = filtered_crops.sort_values("avg_rating", ascending=False)
        elif sort_by == t("Most Reviewed"):
            filtered_crops = filtered_crops.sort_values("total_ratings", ascending=False)
        elif sort_by == t("Location A-Z"):
            filtered_crops = filtered_crops.sort_values("Location", ascending=True)
        else:  # Newest First
            filtered_crops = filtered_crops.iloc[::-1]

        # Display results count
        st.info(f"📋 {t('Showing')} {len(filtered_crops)} {t('of')} {len(crops_with_ratings)} {t('listings')}")
        
        # Display listings as cards with "View Details" button
        for idx, crop in filtered_crops.iterrows():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                # Rating stars display
                rating_display = "⭐" * int(crop['avg_rating']) + "☆" * (5 - int(crop['avg_rating']))
                rating_text = f"{rating_display} {crop['avg_rating']:.1f}/5" if crop['total_ratings'] > 0 else "⭐ No ratings yet"
                
                st.markdown(f"""
                <div style='background: #f9f9f9; padding: 15px; border-radius: 10px; 
                            margin: 10px 0; border-left: 5px solid #4CAF50;'>
                    <h3 style='margin: 0 0 5px 0; color: #2E8B57;'>🌾 {crop['Crop']}</h3>
                    <p style='margin: 3px 0;'><strong>📍</strong> {crop['Location']}</p>
                    <p style='margin: 3px 0;'><strong>💰</strong> ₹{crop['Expected_Price']}/kg</p>
                    <p style='margin: 3px 0;'><strong>📦</strong> Quantity: {crop['Quantity']}</p>
                    <p style='margin: 3px 0;'><strong>👤</strong> {crop['Farmer']}</p>
                    <p style='margin: 3px 0;'><strong>{rating_text}</strong> ({crop['total_ratings']} {t('reviews')})</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("")
                st.markdown("")
                if st.button(f"👁️ {t('View')}", key=f"view_crop_{idx}", use_container_width=True):
                    # Store listing data in session state for detailed view
                    st.session_state.selected_listing = {
                        'type': 'crop',
                        'data': crop.to_dict()
                    }
                    st.session_state.show_listing_detail = True
                    st.rerun()
    else:
        st.info(t("No crops listed yet."))

    st.markdown('<hr>', unsafe_allow_html=True)
    if farmer_name:
        st.subheader(f"{t('Your Crop Listings (Editable by')} {farmer_name})")
        
        editable_crops = crops_df[crops_df["Farmer"] == farmer_name]
        
        if not editable_crops.empty:
            editable_for_display = editable_crops.drop(columns=['rowid'])
            
            updated_crops_df = st.data_editor(
                editable_for_display,
                key="crop_editor",
                width="stretch",
                num_rows="dynamic"
            )
            st.session_state.crops.loc[updated_crops_df.index, updated_crops_df.columns] = updated_crops_df.values
            
        else:
            st.info(t("You have no crop listings yet."))
    else:
        st.warning("Please log in to view and manage your listings.")


