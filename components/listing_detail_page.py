# components/listing_detail_page.py
"""
Detailed Listing View with Contact Buttons and Trust Signals
Shows full listing details, contact options, ratings, and trust badges
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from database.db_functions import get_ratings_for_seller, add_rating, has_user_rated_listing, get_farmer_profile
from components.translation_utils import t
import urllib.parse


def render_listing_detail(listing_type, listing_data):
    """
    Render detailed view of a listing with contact buttons and trust signals.
    
    Args:
        listing_type: 'tool' or 'crop'
        listing_data: Dictionary containing listing information
    """
    
    # Extract listing info
    if listing_type == 'tool':
        title = listing_data.get('Tool', 'Tool')
        price = f"₹{listing_data.get('Rate', 0)}/day"
        details = listing_data.get('Notes', 'No details provided')
        emoji = "🚜"
    else:  # crop
        title = listing_data.get('Crop', 'Crop')
        quantity = listing_data.get('Quantity', 'N/A')
        price = f"₹{listing_data.get('Expected_Price', 0)}/kg"
        details = f"Quantity: {quantity}"
        emoji = "🌾"
    
    location = listing_data.get('Location', 'N/A')
    contact = listing_data.get('Contact', 'N/A')
    seller_name = listing_data.get('Farmer', 'Unknown')
    photo = listing_data.get('Photo', None)
    listing_id = listing_data.get('id', 0)
    
    # Header with back button
    col_back, col_title = st.columns([1, 9])
    with col_back:
        if st.button("⬅️", key="back_btn"):
            st.session_state.nav_history.append(st.session_state.selected_menu)
            st.session_state.nav_forward = []
            st.session_state.selected_menu = "🛍️ Browse Listings"
            st.rerun()
    
    with col_title:
        st.markdown(f"## {emoji} {title}")
    
    # Main listing info card
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #E8F5E9 0%, #F1F8E9 100%); 
                padding: 25px; border-radius: 15px; border: 3px solid #4CAF50; 
                margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);'>
        <h2 style='color: #2E8B57; margin: 0 0 15px 0;'>{emoji} {title}</h2>
        <p style='font-size: 18px; margin: 5px 0;'><strong>📍 {t('Location')}:</strong> {location}</p>
        <p style='font-size: 18px; margin: 5px 0;'><strong>💰 {t('Price')}:</strong> {price}</p>
        <p style='font-size: 16px; margin: 10px 0 0 0; color: #666;'><strong>📝 {t('Details')}:</strong> {details}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Photo if available
    if photo:
        try:
            st.image(photo, width=400, caption=title)
        except:
            pass
    
    st.markdown("---")
    
    # Seller Information with Trust Signals
    st.markdown(f"### 👤 {t('Seller Information')}")
    
    seller_profile = get_farmer_profile(seller_name)
    ratings_df = get_ratings_for_seller(seller_name)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Get member since date
        member_since = "N/A"
        if seller_profile and seller_profile.get('created_date'):
            try:
                created_date = datetime.fromisoformat(seller_profile['created_date'])
                member_since = created_date.strftime("%B %Y")
            except:
                member_since = "N/A"
        
        # Get ratings
        total_ratings = seller_profile.get('total_ratings', 0) if seller_profile else 0
        avg_rating = seller_profile.get('avg_rating', 0.0) if seller_profile else 0.0
        
        # Display trust signals
        stars_display = "⭐" * int(avg_rating) + "☆" * (5 - int(avg_rating))
        
        st.markdown(f"""
        <div style='background: white; padding: 20px; border-radius: 12px; 
                    border-left: 5px solid #2E8B57; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
            <h3 style='margin: 0 0 10px 0; color: #2E8B57;'>👤 {seller_name}</h3>
            <p style='font-size: 16px; margin: 5px 0;'>
                {stars_display} <strong>{avg_rating:.1f}/5</strong> ({total_ratings} {t('ratings')})
            </p>
            <p style='font-size: 14px; margin: 5px 0; color: #666;'>
                📅 {t('Member since')}: {member_since}
            </p>
            <p style='font-size: 16px; margin: 10px 0 0 0;'>
                📞 {contact}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Trust badges
        if total_ratings >= 10:
            st.success("🌟 **Trusted Seller**")
        elif total_ratings >= 5:
            st.info("✅ **Verified Seller**")
        else:
            st.warning("🆕 **New Member**")
    
    st.markdown("")
    
    # BIG CONTACT BUTTONS
    st.markdown(f"### 📞 {t('Contact Seller')}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Call button
        call_link = f"tel:{contact.replace('-', '').replace(' ', '')}"
        st.markdown(f"""
        <a href="{call_link}" target="_self" style="text-decoration: none;">
            <div style='background: linear-gradient(135deg, #4CAF50 0%, #2E8B57 100%); 
                        padding: 20px; border-radius: 12px; text-align: center; 
                        color: white; cursor: pointer; box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                        transition: all 0.3s ease;'>
                <h2 style='margin: 0; color: white;'>📞 {t('Call Now')}</h2>
                <p style='margin: 5px 0 0 0; font-size: 14px;'>{t('Tap to call')}</p>
            </div>
        </a>
        """, unsafe_allow_html=True)
    
    with col2:
        # WhatsApp button
        clean_contact = contact.replace('-', '').replace(' ', '')
        if not clean_contact.startswith('91'):
            clean_contact = '91' + clean_contact
        
        message = f"Hi {seller_name}, I saw your {title} listing on AgroLink. Is it available?"
        encoded_message = urllib.parse.quote(message)
        whatsapp_link = f"https://wa.me/{clean_contact}?text={encoded_message}"
        
        st.markdown(f"""
        <a href="{whatsapp_link}" target="_blank" style="text-decoration: none;">
            <div style='background: linear-gradient(135deg, #25D366 0%, #128C7E 100%); 
                        padding: 20px; border-radius: 12px; text-align: center; 
                        color: white; cursor: pointer; box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                        transition: all 0.3s ease;'>
                <h2 style='margin: 0; color: white;'>💬 {t('WhatsApp')}</h2>
                <p style='margin: 5px 0 0 0; font-size: 14px;'>{t('Send message')}</p>
            </div>
        </a>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Ratings and Reviews Section
    st.markdown(f"### ⭐ {t('Ratings & Reviews')}")
    
    if not ratings_df.empty:
        st.success(f"📊 {len(ratings_df)} {t('reviews from other farmers')}")
        
        for _, rating in ratings_df.head(5).iterrows():
            stars = "⭐" * int(rating['stars']) + "☆" * (5 - int(rating['stars']))
            rater = rating['rater_name']
            comment = rating['comment']
            date = rating['created_date'][:10] if rating['created_date'] else ""
            
            st.markdown(f"""
            <div style='background: #f9f9f9; padding: 15px; border-radius: 10px; 
                        margin: 10px 0; border-left: 4px solid #4CAF50;'>
                <p style='margin: 0; font-size: 16px;'><strong>{stars}</strong> - {rater}</p>
                <p style='margin: 5px 0; color: #666;'>"{comment}"</p>
                <p style='margin: 5px 0 0 0; font-size: 12px; color: #999;'>{date}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info(f"📝 {t('No reviews yet. Be the first to rate this seller!')}")
    
    st.markdown("")
    
    # Rate this seller
    current_user = st.session_state.get('farmer_name', '')
    if current_user and current_user != seller_name:
        already_rated = has_user_rated_listing(current_user, listing_type, listing_id)
        
        if already_rated:
            st.success("✅ You have already rated this seller")
        else:
            with st.expander(f"⭐ {t('Rate this seller')}", expanded=False):
                st.markdown(f"**{t('How was your experience with')} {seller_name}?**")
                
                rating_stars = st.radio(
                    t("Your Rating"),
                    options=[5, 4, 3, 2, 1],
                    format_func=lambda x: "⭐" * x,
                    horizontal=True,
                    key=f"rating_{listing_id}"
                )
                
                rating_comment = st.text_area(
                    t("Your Comment (optional)"),
                    placeholder=t("Share your experience..."),
                    max_chars=200,
                    key=f"comment_{listing_id}"
                )
                
                if st.button(f"✅ {t('Submit Rating')}", key=f"submit_rating_{listing_id}", type="primary"):
                    add_rating(listing_type, listing_id, seller_name, current_user, rating_stars, rating_comment)
                    st.success(f"✅ {t('Thank you for your feedback!')}")
                    st.rerun()
    
    st.markdown("")
    
    # Report button (small, at bottom)
    with st.expander(f"🚩 {t('Report this listing')}", expanded=False):
        st.warning(f"⚠️ {t('Only report if this listing is fake or fraudulent')}")
        report_reason = st.text_area(
            t("Why are you reporting?"),
            placeholder=t("Describe the issue..."),
            key=f"report_{listing_id}"
        )
        if st.button(f"🚩 {t('Submit Report')}", key=f"submit_report_{listing_id}"):
            st.error(f"⚠️ {t('Report submitted. Admin will review.')}")
            # TODO: Store report in database or send email to admin
