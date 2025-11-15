# components/simple_finance_page.py
"""
SIMPLE FARM FINANCE - Like Pocket Diary
Just track: Money In and Money Out
"""

import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date
from calendar import month_name
from components.translation_utils import t

DB_NAME = 'farmermarket.db'

def init_simple_finance_db():
    """Create simple money tracking table."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute("""CREATE TABLE IF NOT EXISTS simple_money_tracker (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        farmer_name TEXT NOT NULL,
        entry_type TEXT NOT NULL,
        amount REAL NOT NULL,
        reason TEXT NOT NULL,
        entry_date TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")
    
    conn.commit()
    conn.close()

def add_money_entry(farmer_name, entry_type, amount, reason, entry_date):
    """Add money in/out entry."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        INSERT INTO simple_money_tracker (farmer_name, entry_type, amount, reason, entry_date)
        VALUES (?, ?, ?, ?, ?)
    """, (farmer_name, entry_type, amount, reason, entry_date))
    conn.commit()
    conn.close()

def get_month_summary(farmer_name, year, month):
    """Get money in/out summary for a month."""
    conn = sqlite3.connect(DB_NAME)
    
    # Get entries for the month
    query = """
        SELECT entry_type, SUM(amount) as total
        FROM simple_money_tracker
        WHERE farmer_name = ?
        AND strftime('%Y', entry_date) = ?
        AND strftime('%m', entry_date) = ?
        GROUP BY entry_type
    """
    
    df = pd.read_sql_query(query, conn, params=(farmer_name, str(year), f"{month:02d}"))
    conn.close()
    
    money_in = df[df['entry_type'] == 'Money In']['total'].sum() if not df.empty else 0
    money_out = df[df['entry_type'] == 'Money Out']['total'].sum() if not df.empty else 0
    
    return money_in, money_out

def get_recent_entries(farmer_name, limit=10):
    """Get recent money entries."""
    conn = sqlite3.connect(DB_NAME)
    query = """
        SELECT entry_type, amount, reason, entry_date
        FROM simple_money_tracker
        WHERE farmer_name = ?
        ORDER BY entry_date DESC, created_at DESC
        LIMIT ?
    """
    df = pd.read_sql_query(query, conn, params=(farmer_name, limit))
    conn.close()
    return df

def render_simple_finance_page():
    """Render simple pocket diary style finance tracker."""
    
    # Initialize DB
    init_simple_finance_db()
    
    farmer_name = st.session_state.get("farmer_name", "")
    if not farmer_name:
        st.warning("⚠️ " + t("Please login to track your money"))
        return
    
    # CSS for pocket diary look
    st.markdown("""
    <style>
    .money-in-card {
        background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
        padding: 25px;
        border-radius: 15px;
        border-left: 8px solid #4CAF50;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        margin: 15px 0;
    }
    
    .money-out-card {
        background: linear-gradient(135deg, #FFEBEE 0%, #FFCDD2 100%);
        padding: 25px;
        border-radius: 15px;
        border-left: 8px solid #F44336;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        margin: 15px 0;
    }
    
    .profit-card {
        background: linear-gradient(135deg, #FFF9C4 0%, #FFF59D 100%);
        padding: 30px;
        border-radius: 15px;
        border: 4px solid #FFC107;
        box-shadow: 0 6px 16px rgba(0,0,0,0.2);
        text-align: center;
        margin: 20px 0;
    }
    
    .loss-card {
        background: linear-gradient(135deg, #FFCCBC 0%, #FFAB91 100%);
        padding: 30px;
        border-radius: 15px;
        border: 4px solid #FF5722;
        box-shadow: 0 6px 16px rgba(0,0,0,0.2);
        text-align: center;
        margin: 20px 0;
    }
    
    .big-amount {
        font-size: 48px;
        font-weight: bold;
        margin: 10px 0;
    }
    
    .diary-title {
        font-size: 24px;
        font-weight: bold;
        color: #2E8B57;
        text-align: center;
        margin: 20px 0;
    }
    
    @media (max-width: 768px) {
        .big-amount { font-size: 36px; }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header - Like Pocket Diary
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #8BC34A 0%, #689F38 100%);
                padding: 25px; border-radius: 15px; text-align: center; 
                margin-bottom: 30px; box-shadow: 0 4px 12px rgba(0,0,0,0.2);'>
        <h1 style='color: white; margin: 0; font-size: 32px;'>📒 {t("My Money Diary")}</h1>
        <p style='color: white; margin: 10px 0 0 0; font-size: 18px; opacity: 0.95;'>
            {t("Simple as your pocket diary - Track in 30 seconds!")}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Month selector
    today = date.today()
    col1, col2 = st.columns(2)
    with col1:
        selected_month = st.selectbox(
            "📅 " + t("Select Month"),
            range(1, 13),
            index=today.month - 1,
            format_func=lambda x: month_name[x]
        )
    with col2:
        selected_year = st.selectbox(
            "📅 " + t("Select Year"),
            range(today.year - 2, today.year + 2),
            index=2
        )
    
    # Get month summary
    money_in, money_out = get_month_summary(farmer_name, selected_year, selected_month)
    profit_loss = money_in - money_out
    
    st.markdown(f"<div class='diary-title'>💰 {month_name[selected_month]} {selected_year}</div>", 
                unsafe_allow_html=True)
    
    # Display like pocket diary - Two pages
    col1, col2 = st.columns(2)
    
    with col1:
        # Left Page - Money In (Paisa Aaya)
        st.markdown(f"""
        <div class='money-in-card'>
            <h2 style='color: #2E8B57; margin: 0 0 15px 0; text-align: center;'>
                📗 {t("Money In")}
            </h2>
            <div style='text-align: center;'>
                <div class='big-amount' style='color: #2E8B57;'>
                    ₹{money_in:,.0f}
                </div>
                <p style='margin: 0; color: #666; font-size: 16px;'>({t("Paisa Aaya")})</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Right Page - Money Out (Paisa Gaya)
        st.markdown(f"""
        <div class='money-out-card'>
            <h2 style='color: #C62828; margin: 0 0 15px 0; text-align: center;'>
                📕 {t("Money Out")}
            </h2>
            <div style='text-align: center;'>
                <div class='big-amount' style='color: #C62828;'>
                    ₹{money_out:,.0f}
                </div>
                <p style='margin: 0; color: #666; font-size: 16px;'>({t("Paisa Gaya")})</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Profit/Loss at bottom - Like counting at end of month
    if profit_loss >= 0:
        st.markdown(f"""
        <div class='profit-card'>
            <h2 style='color: #F57F17; margin: 0 0 10px 0;'>🎉 {t("PROFIT")} 🎉</h2>
            <div class='big-amount' style='color: #F57F17;'>
                ₹{profit_loss:,.0f}
            </div>
            <p style='margin: 10px 0 0 0; font-size: 18px; color: #666;'>
                ✅ {t("Good! You earned more than you spent!")}
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class='loss-card'>
            <h2 style='color: #BF360C; margin: 0 0 10px 0;'>⚠️ {t("LOSS")} ⚠️</h2>
            <div class='big-amount' style='color: #BF360C;'>
                ₹{abs(profit_loss):,.0f}
            </div>
            <p style='margin: 10px 0 0 0; font-size: 18px; color: #666;'>
                ⚠️ {t("Be careful! You spent more than you earned!")}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick Add Buttons
    st.markdown(f"### ⚡ {t('Quick Add (30 seconds)')}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.form("add_money_in"):
            st.markdown(f"#### 📗 {t('Add Money In')}")
            
            in_amount = st.number_input(
                t("How much money came in?") + " (₹)",
                min_value=1,
                value=1000,
                step=100,
                key="in_amount"
            )
            
            in_reason = st.text_input(
                t("What for?"),
                placeholder=t("e.g., Sold Tomatoes, Sold Wheat, Rented Tool"),
                help=t("Describe where the money came from"),
                key="in_reason"
            )
            
            in_date = st.date_input(
                t("Date"),
                value=today,
                max_value=today,
                key="in_date"
            )
            
            if st.form_submit_button("💚 " + t("SAVE Money In"), use_container_width=True, type="primary"):
                if in_reason and in_reason.strip():
                    add_money_entry(farmer_name, "Money In", in_amount, in_reason.strip(), in_date.strftime("%Y-%m-%d"))
                    st.success(f"✅ {t('Saved!')} ₹{in_amount:,.0f} - {in_reason}")
                    st.rerun()
                else:
                    st.error(f"⚠️ {t('Please enter a reason')}")
    
    with col2:
        with st.form("add_money_out"):
            st.markdown(f"#### 📕 {t('Add Money Out')}")
            
            out_amount = st.number_input(
                t("How much money went out?") + " (₹)",
                min_value=1,
                value=500,
                step=100,
                key="out_amount"
            )
            
            out_reason = st.text_input(
                t("What for?"),
                placeholder=t("e.g., Bought Seeds, Paid Workers, Tool Repair"),
                help=t("Describe where the money went"),
                key="out_reason"
            )
            
            out_date = st.date_input(
                t("Date"),
                value=today,
                max_value=today,
                key="out_date"
            )
            
            if st.form_submit_button("❤️ " + t("SAVE Money Out"), use_container_width=True, type="secondary"):
                if out_reason and out_reason.strip():
                    add_money_entry(farmer_name, "Money Out", out_amount, out_reason.strip(), out_date.strftime("%Y-%m-%d"))
                    st.success(f"✅ {t('Saved!')} ₹{out_amount:,.0f} - {out_reason}")
                    st.rerun()
                else:
                    st.error(f"⚠️ {t('Please enter a reason')}")
    
    st.markdown("---")
    
    # Recent History - Simple List
    st.markdown(f"### 📜 {t('Recent History')} ({t('Last 10 entries')})")
    
    recent_df = get_recent_entries(farmer_name, 10)
    
    if not recent_df.empty:
        for idx, entry in recent_df.iterrows():
            entry_type = entry['entry_type']
            amount = entry['amount']
            reason = entry['reason']
            entry_date = entry['entry_date']
            
            if entry_type == "Money In":
                color = "#4CAF50"
                icon = "📗"
                sign = "+"
            else:
                color = "#F44336"
                icon = "📕"
                sign = "-"
            
            st.markdown(f"""
            <div style='background: white; padding: 15px; border-radius: 10px; 
                        margin: 10px 0; border-left: 5px solid {color}; 
                        box-shadow: 0 2px 6px rgba(0,0,0,0.1);'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <span style='font-size: 20px;'>{icon}</span>
                        <strong style='font-size: 18px; color: {color};'>{sign}₹{amount:,.0f}</strong>
                        <span style='margin-left: 15px; color: #666;'>{reason}</span>
                    </div>
                    <div style='text-align: right; color: #999; font-size: 14px;'>
                        {entry_date}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info(f"📝 {t('No entries yet')}. {t('Start by adding money in or out above!')}")
    
    # Help Section
    st.markdown("---")
    with st.expander(f"❓ {t('How to use this?')}"):
        st.markdown(f"""
        ### 🎯 {t("It's as simple as your pocket diary!")}
        
        **{t("Step 1:")}** {t("When money comes in (sold crops, got subsidy, etc.):")}
        - {t("Click")} "📗 {t('Add Money In')}"
        - {t("Enter amount and select reason")}
        - {t("Click SAVE")}
        
        **{t("Step 2:")}** {t("When money goes out (bought seeds, paid workers, etc.):")}
        - {t("Click")} "📕 {t('Add Money Out')}"
        - {t("Enter amount and select reason")}
        - {t("Click SAVE")}
        
        **{t("Step 3:")}** {t("At end of month, see your profit/loss automatically!")}
        
        **⏱️ {t("Takes only 30 seconds!")}** {t("Do it while sitting on tractor or at home!")}
        """)
