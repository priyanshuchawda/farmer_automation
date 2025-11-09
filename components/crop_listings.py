# components/crop_listings.py
import streamlit as st
from database.db_functions import add_data, get_data
from datetime import date
import pandas as pd
from ai.ai_matcher import get_recommendations  # ✅ AI AI integration
from components.translation_utils import t


def render_crop_listing(farmer_name):
    """Renders the form to add a new crop listing with AI recommendations."""
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
    """Renders the full crop management view with filtering and editable tables."""
    st.subheader(t("All Crop Listings"))
    
    if not crops_df.empty:
        crops_without_rowid = crops_df.drop(columns=['rowid'])
        crop_locations = [t("All")] + sorted(crops_without_rowid["Location"].unique().tolist())
        crop_types = [t("All")] + sorted(crops_without_rowid["Crop"].unique().tolist())
        
        filter_cols = st.columns(3)
        selected_crop_loc = filter_cols[0].selectbox(t("Filter by Location"), crop_locations, key="crop_loc_filter")
        selected_crop_type = filter_cols[1].selectbox(t("Filter by Crop Type"), crop_types, key="crop_type_filter")
        
        filtered_crops = crops_without_rowid.copy()
        if selected_crop_loc != t("All"):
            filtered_crops = filtered_crops[filtered_crops["Location"] == selected_crop_loc]
        if selected_crop_type != t("All"):
            filtered_crops = filtered_crops[filtered_crops["Crop"] == selected_crop_type]

        st.dataframe(filtered_crops, use_container_width=True)
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
                use_container_width=True,
                num_rows="dynamic"
            )
            st.session_state.crops.loc[updated_crops_df.index, updated_crops_df.columns] = updated_crops_df.values
            
        else:
            st.info(t("You have no crop listings yet."))
    else:
        st.warning("Please log in to view and manage your listings.")


