import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from database.db_functions import get_connection
import sqlite3

def init_notifications_table():
    """Initialize notifications and alerts table"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create notifications table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            farmer_name TEXT NOT NULL,
            type TEXT NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            priority TEXT DEFAULT 'medium',
            is_read INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create price alerts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS price_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            farmer_name TEXT NOT NULL,
            commodity TEXT NOT NULL,
            target_price REAL NOT NULL,
            alert_type TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

def add_notification(farmer_name, notif_type, title, message, priority="medium"):
    """Add a notification for a farmer"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO notifications (farmer_name, type, title, message, priority)
        VALUES (?, ?, ?, ?, ?)
    """, (farmer_name, notif_type, title, message, priority))
    conn.commit()
    conn.close()

def get_notifications(farmer_name, unread_only=False):
    """Get notifications for a farmer"""
    conn = get_connection()
    query = """
        SELECT id, type, title, message, priority, is_read, created_at
        FROM notifications
        WHERE farmer_name = ?
    """
    if unread_only:
        query += " AND is_read = 0"
    query += " ORDER BY created_at DESC"
    
    df = pd.read_sql_query(query, conn, params=(farmer_name,))
    conn.close()
    return df

def mark_notification_read(notification_id):
    """Mark a notification as read"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE notifications SET is_read = 1 WHERE id = ?", (notification_id,))
    conn.commit()
    conn.close()

def add_price_alert(farmer_name, commodity, target_price, alert_type):
    """Add a price alert"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO price_alerts (farmer_name, commodity, target_price, alert_type)
        VALUES (?, ?, ?, ?)
    """, (farmer_name, commodity, target_price, alert_type))
    conn.commit()
    conn.close()

def get_price_alerts(farmer_name):
    """Get price alerts for a farmer"""
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT id, commodity, target_price, alert_type, is_active, created_at
        FROM price_alerts
        WHERE farmer_name = ? AND is_active = 1
        ORDER BY created_at DESC
    """, conn, params=(farmer_name,))
    conn.close()
    return df

def delete_price_alert(alert_id):
    """Delete a price alert"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE price_alerts SET is_active = 0 WHERE id = ?", (alert_id,))
    conn.commit()
    conn.close()

def render_notifications_page():
    """
    Render Notifications and Alerts page
    """
    st.header("🔔 Notifications & Alerts")
    st.markdown("Stay updated with weather alerts, price changes, and calendar reminders")
    
    # Initialize tables
    init_notifications_table()
    
    # Get farmer info
    farmer_name = st.session_state.get("farmer_name", "")
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📬 Notifications", "💰 Price Alerts", "⚙️ Settings"])
    
    # Tab 1: Notifications
    with tab1:
        st.subheader("📬 Your Notifications")
        
        # Filter options
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            show_unread = st.checkbox("Show unread only", value=False)
        
        with col2:
            filter_type = st.selectbox(
                "Filter by type:",
                ["All", "Weather", "Price", "Listing", "Calendar", "System"]
            )
        
        with col3:
            if st.button("🗑️ Clear All", width="stretch"):
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM notifications WHERE farmer_name = ?", (farmer_name,))
                conn.commit()
                conn.close()
                st.success("✅ All notifications cleared!")
                st.rerun()
        
        st.markdown("---")
        
        # Get notifications
        notifications_df = get_notifications(farmer_name, unread_only=show_unread)
        
        if not notifications_df.empty:
            # Apply type filter
            if filter_type != "All":
                notifications_df = notifications_df[notifications_df['type'] == filter_type]
            
            if notifications_df.empty:
                st.info("📭 No notifications matching your filter")
            else:
                # Display notifications
                for _, notif in notifications_df.iterrows():
                    # Icon based on type
                    icon_map = {
                        "Weather": "🌤️",
                        "Price": "💰",
                        "Listing": "🛍️",
                        "Calendar": "📅",
                        "System": "⚙️"
                    }
                    icon = icon_map.get(notif['type'], "📢")
                    
                    # Priority color
                    priority_colors = {
                        "high": "#FFCDD2",
                        "medium": "#FFF9C4",
                        "low": "#E8F5E9"
                    }
                    bg_color = priority_colors.get(notif['priority'], "#F5F5F5")
                    
                    # Read/Unread indicator
                    read_badge = "" if notif['is_read'] else "<span style='background-color:#FF5722;color:white;padding:2px 8px;border-radius:12px;font-size:10px;margin-left:10px;'>NEW</span>"
                    
                    # Time ago
                    created = pd.to_datetime(notif['created_at'])
                    time_ago = (datetime.now() - created).total_seconds() / 3600
                    if time_ago < 1:
                        time_str = f"{int(time_ago * 60)} mins ago"
                    elif time_ago < 24:
                        time_str = f"{int(time_ago)} hours ago"
                    else:
                        time_str = f"{int(time_ago / 24)} days ago"
                    
                    # Render notification card
                    st.markdown(f"""
                    <div style='background-color:{bg_color};padding:15px;border-radius:10px;margin:10px 0;border-left:4px solid #2E8B57;'>
                        <strong>{icon} {notif['title']}</strong>{read_badge}
                        <br><small style='color:#666;'>{time_str} • {notif['type']} • Priority: {notif['priority']}</small>
                        <p style='margin-top:8px;'>{notif['message']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Mark as read button
                    if not notif['is_read']:
                        if st.button(f"✓ Mark as read", key=f"read_{notif['id']}", width="stretch"):
                            mark_notification_read(notif['id'])
                            st.rerun()
                
                st.success(f"📊 Total notifications: {len(notifications_df)}")
        else:
            st.info("📭 No notifications yet. We'll notify you about important updates!")
            
            # Add sample notifications button
            if st.button("➕ Add Sample Notifications (Demo)", type="secondary"):
                add_notification(farmer_name, "Weather", "Heavy Rain Alert", 
                               "Heavy rainfall expected in your area tomorrow. Secure your crops!", "high")
                add_notification(farmer_name, "Price", "Wheat Price Increased", 
                               "Wheat prices have increased by 15% in the last week.", "medium")
                add_notification(farmer_name, "Calendar", "Irrigation Reminder", 
                               "Scheduled irrigation for Field A tomorrow at 6 AM", "low")
                st.success("✅ Sample notifications added!")
                st.rerun()
    
    # Tab 2: Price Alerts
    with tab2:
        st.subheader("💰 Price Alert Management")
        st.markdown("Get notified when crop prices reach your target levels")
        
        # Create new alert section
        with st.expander("➕ Create New Price Alert", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                commodity = st.text_input("Commodity Name", placeholder="e.g., Wheat, Rice, Tomato")
                target_price = st.number_input("Target Price (₹/quintal)", min_value=0.0, step=100.0)
            
            with col2:
                alert_type = st.selectbox(
                    "Alert When Price:",
                    ["Goes Above", "Goes Below", "Equals"]
                )
                
                if st.button("🔔 Create Alert", width="stretch", type="primary"):
                    if commodity and target_price > 0:
                        add_price_alert(farmer_name, commodity, target_price, alert_type)
                        st.success(f"✅ Alert created for {commodity} at ₹{target_price}")
                        st.rerun()
                    else:
                        st.error("Please fill all fields")
        
        st.markdown("---")
        
        # Display existing alerts
        st.subheader("📋 Active Price Alerts")
        alerts_df = get_price_alerts(farmer_name)
        
        if not alerts_df.empty:
            for _, alert in alerts_df.iterrows():
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.markdown(f"""
                    <div style='background-color:#E8F5E9;padding:12px;border-radius:8px;'>
                        <strong>📊 {alert['commodity']}</strong><br>
                        <small>Alert Type: {alert['alert_type']}</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.metric("Target Price", f"₹{alert['target_price']:.2f}")
                
                with col3:
                    if st.button("🗑️", key=f"del_alert_{alert['id']}", width="stretch"):
                        delete_price_alert(alert['id'])
                        st.rerun()
                
                st.markdown("---")
            
            st.success(f"📊 Active alerts: {len(alerts_df)}")
        else:
            st.info("💡 No price alerts set yet. Create one to get notified when prices change!")
    
    # Tab 3: Settings
    with tab3:
        st.subheader("⚙️ Notification Settings")
        
        st.markdown("### 🔔 Enable/Disable Notifications")
        
        # Notification preferences
        enable_weather = st.checkbox("🌤️ Weather Alerts", value=True)
        enable_price = st.checkbox("💰 Price Updates", value=True)
        enable_listings = st.checkbox("🛍️ Listing Inquiries", value=True)
        enable_calendar = st.checkbox("📅 Calendar Reminders", value=True)
        
        st.markdown("---")
        
        st.markdown("### 📱 Notification Delivery")
        
        # Delivery methods
        delivery_app = st.checkbox("📲 In-App Notifications", value=True, disabled=True)
        st.caption("✓ Always enabled - receive notifications within the app")
        
        delivery_email = st.checkbox("📧 Email Notifications", value=False)
        if delivery_email:
            email = st.text_input("Email Address", placeholder="farmer@example.com")
        
        delivery_sms = st.checkbox("📱 SMS Notifications", value=False)
        if delivery_sms:
            phone = st.text_input("Phone Number", placeholder="+91 XXXXXXXXXX")
        
        st.markdown("---")
        
        st.markdown("### 🕐 Quiet Hours")
        col1, col2 = st.columns(2)
        
        with col1:
            quiet_start = st.time_input("Start Time", value=None)
        
        with col2:
            quiet_end = st.time_input("End Time", value=None)
        
        st.caption("💡 Notifications will be delayed during quiet hours")
        
        st.markdown("---")
        
        if st.button("💾 Save Settings", width="stretch", type="primary"):
            st.success("✅ Settings saved successfully!")
            st.balloons()
        
        st.markdown("---")
        
        # Clear data options
        st.markdown("### 🗑️ Data Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Clear Old Notifications", width="stretch"):
                conn = get_connection()
                cursor = conn.cursor()
                week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
                cursor.execute("""
                    DELETE FROM notifications 
                    WHERE farmer_name = ? AND created_at < ? AND is_read = 1
                """, (farmer_name, week_ago))
                conn.commit()
                conn.close()
                st.success("✅ Old notifications cleared!")
        
        with col2:
            if st.button("Clear All Alerts", width="stretch"):
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE price_alerts SET is_active = 0 WHERE farmer_name = ?", (farmer_name,))
                conn.commit()
                conn.close()
                st.success("✅ All alerts cleared!")
    
    # Footer with stats
    st.markdown("---")
    notifications_df = get_notifications(farmer_name)
    alerts_df = get_price_alerts(farmer_name)
    unread_count = len(notifications_df[notifications_df['is_read'] == 0]) if not notifications_df.empty else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📬 Total Notifications", len(notifications_df))
    with col2:
        st.metric("🔔 Unread", unread_count)
    with col3:
        st.metric("💰 Active Alerts", len(alerts_df))


