# components/farm_finance_page.py
"""
Farm Finance Management System
Complete financial tracking and analysis for farm operations
Uses AI AI for intelligent insights and analysis
"""

import streamlit as st
from google import genai
from google.genai import types
import os
from datetime import datetime, timedelta
import sqlite3
import json
import pandas as pd
from components.translation_utils import t
from dotenv import load_dotenv

load_dotenv()

# Database setup
DB_NAME = 'farmermarket.db'

def init_finance_db():
    """Initialize finance tables."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Income/Expense table
    c.execute("""CREATE TABLE IF NOT EXISTS farm_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        farmer_id INTEGER NOT NULL,
        type TEXT NOT NULL,
        category TEXT NOT NULL,
        amount REAL NOT NULL,
        description TEXT,
        date TEXT NOT NULL,
        payment_mode TEXT,
        receipt_number TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (farmer_id) REFERENCES farmers(id)
    )""")
    
    # Investment Planning table
    c.execute("""CREATE TABLE IF NOT EXISTS farm_investments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        farmer_id INTEGER NOT NULL,
        item_name TEXT NOT NULL,
        category TEXT NOT NULL,
        estimated_cost REAL NOT NULL,
        target_date TEXT,
        priority TEXT,
        status TEXT DEFAULT 'Planned',
        notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (farmer_id) REFERENCES farmers(id)
    )""")
    
    # Insurance Tracker table
    c.execute("""CREATE TABLE IF NOT EXISTS farm_insurance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        farmer_id INTEGER NOT NULL,
        insurance_type TEXT NOT NULL,
        provider TEXT,
        policy_number TEXT,
        coverage_amount REAL,
        premium_amount REAL,
        start_date TEXT,
        end_date TEXT,
        reminder_days INTEGER DEFAULT 30,
        status TEXT DEFAULT 'Active',
        notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (farmer_id) REFERENCES farmers(id)
    )""")
    
    conn.commit()
    conn.close()

class FinanceAI:
    """AI-powered financial assistant using AI."""
    
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found")
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
    
    def get_language_instruction(self):
        """Get language instruction based on selected language"""
        try:
            selected_lang = st.session_state.get('language', 'English')
            
            language_map = {
                "English": "English",
                "हिन्दी (Hindi)": "Hindi (हिन्दी)",
                "मराठी (Marathi)": "Marathi (मराठी)"
            }
            
            target_language = language_map.get(selected_lang, "English")
            
            if target_language != "English":
                return f"\n\nIMPORTANT: Reply ONLY in {target_language} language. Do not use English."
            return ""
        except:
            return ""
    
    def analyze_profit_loss(self, income_data, expense_data, period):
        """Analyze profit/loss with AI insights."""
        total_income = sum([t['amount'] for t in income_data])
        total_expense = sum([t['amount'] for t in expense_data])
        profit = total_income - total_expense
        
        language_instruction = self.get_language_instruction()
        
        prompt = f"""Analyze farm financial performance and provide actionable advice.

PERIOD: {period}

FINANCIAL SUMMARY:
Income:
- Total: ₹{total_income:,.2f} from {len(income_data)} transactions
- Sources: {', '.join(set([t['category'] for t in income_data]))}

Expenses:
- Total: ₹{total_expense:,.2f} from {len(expense_data)} transactions  
- Categories: {', '.join(set([t['category'] for t in expense_data]))}

Net Profit/Loss: ₹{profit:,.2f} ({'+' if profit >= 0 else ''}{(profit/total_income*100):.1f}% margin)

REQUIRED ANALYSIS (provide 5 sections):

1. FINANCIAL HEALTH VERDICT
[Is farm profitable? Compare to typical farm margins. 1-2 sentences.]

2. KEY PATTERNS IDENTIFIED
- Pattern 1: [Highest expense category and % of total - is it normal?]
- Pattern 2: [Income source analysis - diversified or single crop?]
- Pattern 3: [Cash flow insight - seasonal patterns visible?]

3. COST REDUCTION OPPORTUNITIES
- Action 1: [Specific expense to reduce with ₹ saving estimate]
- Action 2: [Bulk buying or timing optimization]
- Action 3: [Equipment sharing or alternative method]

4. REVENUE GROWTH STRATEGIES
- Strategy 1: [New crop/product with market potential]
- Strategy 2: [Value addition opportunity - processing, grading]
- Strategy 3: [Market timing or selling location change]

5. SEASONAL PLANNING
[Next 3 months outlook and preparation advice]

Keep advice practical for Indian small farmers.{language_instruction}"""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.3)
            )
            return response.text
        except Exception as e:
            return f"AI analysis unavailable: {str(e)}"
    
    def suggest_investments(self, budget, current_equipment, farm_size, crop_type):
        """Get AI suggestions for farm investments."""
        prompt = f"""Recommend smart farm investments for maximum ROI.

FARMER PROFILE:
- Available Budget: ₹{budget:,.2f}
- Farm Size: {farm_size}
- Current Equipment: {current_equipment}
- Primary Crop: {crop_type}

TASK:
Search current Indian market and suggest 5 prioritized investments.

For each investment, provide:

**[Equipment/Tool Name]**
- **Cost:** ₹[amount] (search current 2024-25 prices in India)
- **ROI Timeline:** [X months/years to recover investment]
- **Priority:** [HIGH/MEDIUM/LOW]
- **Annual Benefit:** ₹[estimated savings or extra income]
- **Why This:** [2-3 sentence justification with data]

EVALUATION CRITERIA:
1. Fits within budget or slightly above (financing option)
2. Addresses gap in current equipment
3. Suitable for farm size
4. Relevant for crop type
5. Good ROI (< 2-3 years payback)
6. Available in Indian market

SEARCH FOCUS:
- IndiaMART, Tractor Junction, local agricultural equipment dealers
- Government subsidy schemes (mention if applicable)
- Second-hand options if budget is tight

Prioritize practical, high-impact investments for small Indian farms."""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                    temperature=0.4
                )
            )
            return response.text
        except Exception as e:
            return f"Unable to fetch suggestions: {str(e)}"
    
    def insurance_recommendations(self, location, crop_type, farm_size):
        """Get crop insurance recommendations."""
        prompt = f"""Search and recommend best crop insurance options for this Indian farmer.

FARMER DETAILS:
- Location: {location}, India
- Crop Type: {crop_type}
- Farm Size: {farm_size}

SEARCH REQUIREMENTS:
- Find active insurance schemes for 2024-2025
- Include PMFBY (Pradhan Mantri Fasal Bima Yojana) details
- Search state-specific schemes for {location}
- Include private insurance alternatives

OUTPUT FORMAT:

## TOP 3 INSURANCE OPTIONS

**1. [Scheme Name]** (Government/Private)
- **Coverage:** [What losses covered - drought, flood, pest, hail, etc.]
- **Sum Insured:** ₹[amount per acre/hectare]
- **Premium:** ₹[farmer pays] (Government subsidizes: [X]%)
- **Eligibility:** [Who can apply - land ownership requirements]
- **Claim Process:** [3-4 step process]
- **Claim Timeline:** [Days to receive payout]
- **Best For:** [Type of farmer/situation]
- **How to Apply:** [Specific steps with website/office]

[Repeat for 2nd and 3rd options]

## COMPARISON TABLE

| Feature | Scheme 1 | Scheme 2 | Scheme 3 |
|---------|----------|----------|----------|
| Premium | ₹X | ₹Y | ₹Z |
| Coverage | [%] | [%] | [%] |
| Subsidy | [%] | [%] | [%] |

## KEY RECOMMENDATIONS

- **Best Value:** [Which scheme offers best coverage-to-cost ratio]
- **Deadline:** [Last date to enroll - usually before sowing]
- **Required Documents:** [List - Aadhar, land records, bank details]
- **Pro Tip:** [One important tip for claiming successfully]

Search official insurance websites and recent agriculture ministry updates."""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                    temperature=0.3
                )
            )
            return response.text
        except Exception as e:
            return f"Unable to fetch recommendations: {str(e)}"

def render_farm_finance_page():
    """Main finance management page."""
    st.header("💰 Farm Finance Management")
    
    # Initialize
    init_finance_db()
    
    if 'finance_ai' not in st.session_state:
        try:
            st.session_state.finance_ai = FinanceAI()
        except Exception as e:
            st.error(f"AI features unavailable: {e}")
            st.session_state.finance_ai = None
    
    # Get farmer ID from session
    farmer_name = st.session_state.get('farmer_name')
    if not farmer_name:
        st.warning("Please login to access finance features.")
        return
    
    # Get farmer profile to retrieve farmer_id
    from database.db_functions import get_farmer_profile
    farmer_profile = get_farmer_profile(farmer_name)
    if not farmer_profile:
        st.error("Could not load farmer profile.")
        return
    
    farmer_id = farmer_profile.get('id')
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        f"📊 {t('Dashboard')}",
        f"➕ {t('Add Transaction')}",
        f"📈 {t('Profit/Loss Analysis')}",
        f"🎯 {t('Investment Planning')}",
        f"🛡️ {t('Insurance Tracker')}",
        f"🧾 {t('Receipt Generator')}"
    ])
    
    # TAB 1: Dashboard
    with tab1:
        render_finance_dashboard(farmer_id)
    
    # TAB 2: Add Transaction
    with tab2:
        render_add_transaction(farmer_id)
    
    # TAB 3: Profit/Loss Analysis
    with tab3:
        render_profit_loss_analysis(farmer_id)
    
    # TAB 4: Investment Planning
    with tab4:
        render_investment_planning(farmer_id)
    
    # TAB 5: Insurance Tracker
    with tab5:
        render_insurance_tracker(farmer_id)
    
    # TAB 6: Receipt Generator
    with tab6:
        render_receipt_generator(farmer_id)

def render_finance_dashboard(farmer_id):
    """Display financial dashboard."""
    st.subheader("📊 Financial Overview")
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Get current month data
    current_month = datetime.now().strftime('%Y-%m')
    
    c.execute("""SELECT type, SUM(amount) FROM farm_transactions 
                 WHERE farmer_id = ? AND date LIKE ? 
                 GROUP BY type""", (farmer_id, f"{current_month}%"))
    monthly_data = c.fetchall()
    
    income = sum([row[1] for row in monthly_data if row[0] == 'Income'])
    expense = sum([row[1] for row in monthly_data if row[0] == 'Expense'])
    profit = income - expense
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Monthly Income", f"₹{income:,.2f}", delta=None)
    with col2:
        st.metric("Monthly Expense", f"₹{expense:,.2f}", delta=None)
    with col3:
        profit_color = "normal" if profit >= 0 else "inverse"
        st.metric("Profit/Loss", f"₹{profit:,.2f}", delta=None)
    with col4:
        margin = (profit / income * 100) if income > 0 else 0
        st.metric("Profit Margin", f"{margin:.1f}%")
    
    st.markdown("---")
    
    # Recent transactions
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💚 Recent Income")
        c.execute("""SELECT category, amount, date, description 
                     FROM farm_transactions 
                     WHERE farmer_id = ? AND type = 'Income'
                     ORDER BY date DESC LIMIT 5""", (farmer_id,))
        income_txns = c.fetchall()
        
        if income_txns:
            for txn in income_txns:
                st.write(f"**{txn[0]}** - ₹{txn[1]:,.2f}")
                st.caption(f"{txn[2]} | {txn[3]}")
        else:
            st.info("No income recorded yet")
    
    with col2:
        st.subheader("💸 Recent Expenses")
        c.execute("""SELECT category, amount, date, description 
                     FROM farm_transactions 
                     WHERE farmer_id = ? AND type = 'Expense'
                     ORDER BY date DESC LIMIT 5""", (farmer_id,))
        expense_txns = c.fetchall()
        
        if expense_txns:
            for txn in expense_txns:
                st.write(f"**{txn[0]}** - ₹{txn[1]:,.2f}")
                st.caption(f"{txn[2]} | {txn[3]}")
        else:
            st.info("No expenses recorded yet")
    
    conn.close()
    
    # Quick actions
    st.markdown("---")
    st.subheader("⚡ Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("➕ Add Income", width="stretch"):
            st.session_state.quick_action = 'add_income'
            st.rerun()
    with col2:
        if st.button("➖ Add Expense", width="stretch"):
            st.session_state.quick_action = 'add_expense'
            st.rerun()
    with col3:
        if st.button("📈 View Analysis", width="stretch"):
            st.session_state.quick_action = 'analysis'
            st.rerun()

def render_add_transaction(farmer_id):
    """Add income/expense transaction."""
    st.subheader("➕ Add Transaction")
    
    # Quick action handling
    default_type = "Income"
    if st.session_state.get('quick_action') == 'add_income':
        default_type = "Income"
        st.session_state.quick_action = None
    elif st.session_state.get('quick_action') == 'add_expense':
        default_type = "Expense"
        st.session_state.quick_action = None
    
    col1, col2 = st.columns(2)
    
    with col1:
        txn_type = st.selectbox("Transaction Type", ["Income", "Expense"], 
                                index=0 if default_type == "Income" else 1)
        
        if txn_type == "Income":
            categories = ["Crop Sale", "Tool Rental", "Livestock Sale", "Government Subsidy", "Other"]
        else:
            categories = ["Seeds", "Fertilizer", "Pesticides", "Labor", "Equipment", 
                         "Fuel", "Electricity", "Maintenance", "Other"]
        
        category = st.selectbox("Category", categories)
        amount = st.number_input("Amount (₹)", min_value=0.0, step=100.0)
    
    with col2:
        date = st.date_input("Date", value=datetime.now())
        payment_mode = st.selectbox("Payment Mode", ["Cash", "Bank Transfer", "UPI", "Cheque"], key="transaction_payment_mode")
        receipt_no = st.text_input("Receipt/Reference Number (Optional)")
    
    description = st.text_area("Description", placeholder="e.g., Sold 10 quintals wheat to APMC")
    
    if st.button("💾 Save Transaction", type="primary"):
        if amount > 0:
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            
            c.execute("""INSERT INTO farm_transactions 
                        (farmer_id, type, category, amount, description, date, payment_mode, receipt_number)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                     (farmer_id, txn_type, category, amount, description, 
                      date.isoformat(), payment_mode, receipt_no))
            
            conn.commit()
            conn.close()
            
            st.success(f"✅ {txn_type} of ₹{amount:,.2f} recorded successfully!")
            st.balloons()
        else:
            st.error("Please enter a valid amount")

def render_profit_loss_analysis(farmer_id):
    """Profit/loss analysis with AI insights."""
    st.subheader("📈 Profit/Loss Analysis")
    
    # Period selection
    col1, col2, col3 = st.columns(3)
    
    with col1:
        period = st.selectbox("Analysis Period", 
                             ["This Month", "Last Month", "This Quarter", 
                              "This Year", "Custom Range"])
    
    # Calculate date range
    if period == "This Month":
        start_date = datetime.now().replace(day=1)
        end_date = datetime.now()
    elif period == "Last Month":
        last_month = datetime.now().replace(day=1) - timedelta(days=1)
        start_date = last_month.replace(day=1)
        end_date = last_month
    elif period == "This Quarter":
        current_month = datetime.now().month
        quarter_start = ((current_month - 1) // 3) * 3 + 1
        start_date = datetime.now().replace(month=quarter_start, day=1)
        end_date = datetime.now()
    elif period == "This Year":
        start_date = datetime.now().replace(month=1, day=1)
        end_date = datetime.now()
    else:  # Custom
        with col2:
            start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=30))
        with col3:
            end_date = st.date_input("End Date", value=datetime.now())
    
    # Fetch data
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute("""SELECT * FROM farm_transactions 
                 WHERE farmer_id = ? AND date BETWEEN ? AND ?
                 ORDER BY date DESC""",
             (farmer_id, start_date.isoformat(), end_date.isoformat()))
    
    transactions = c.fetchall()
    conn.close()
    
    if not transactions:
        st.info("No transactions found for this period")
        return
    
    # Process data
    income_data = [{'amount': t[3], 'category': t[2], 'date': t[5]} 
                   for t in transactions if t[1] == 'Income']
    expense_data = [{'amount': t[3], 'category': t[2], 'date': t[5]} 
                    for t in transactions if t[1] == 'Expense']
    
    total_income = sum([t['amount'] for t in income_data])
    total_expense = sum([t['amount'] for t in expense_data])
    net_profit = total_income - total_expense
    
    # Display summary
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Income", f"₹{total_income:,.2f}", 
                 help=f"{len(income_data)} transactions")
    with col2:
        st.metric("Total Expenses", f"₹{total_expense:,.2f}",
                 help=f"{len(expense_data)} transactions")
    with col3:
        profit_delta = "📈" if net_profit >= 0 else "📉"
        st.metric("Net Profit/Loss", f"₹{net_profit:,.2f}", delta=profit_delta)
    
    # Category breakdown
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💚 Income Breakdown")
        income_by_category = {}
        for t in income_data:
            income_by_category[t['category']] = income_by_category.get(t['category'], 0) + t['amount']
        
        for cat, amt in sorted(income_by_category.items(), key=lambda x: x[1], reverse=True):
            pct = (amt / total_income * 100) if total_income > 0 else 0
            st.write(f"**{cat}:** ₹{amt:,.2f} ({pct:.1f}%)")
    
    with col2:
        st.subheader("💸 Expense Breakdown")
        expense_by_category = {}
        for t in expense_data:
            expense_by_category[t['category']] = expense_by_category.get(t['category'], 0) + t['amount']
        
        for cat, amt in sorted(expense_by_category.items(), key=lambda x: x[1], reverse=True):
            pct = (amt / total_expense * 100) if total_expense > 0 else 0
            st.write(f"**{cat}:** ₹{amt:,.2f} ({pct:.1f}%)")
    
    # AI Analysis
    st.markdown("---")
    if st.button("🤖 Get AI Analysis", type="primary"):
        if st.session_state.finance_ai:
            with st.spinner("Analyzing your finances with AI..."):
                analysis = st.session_state.finance_ai.analyze_profit_loss(
                    income_data, expense_data, period
                )
                st.subheader("🤖 AI Financial Insights")
                st.markdown(analysis)
        else:
            st.error("AI features unavailable")

def render_investment_planning(farmer_id):
    """Investment planning with AI suggestions."""
    st.subheader("🎯 Investment Planning")
    
    tab1, tab2, tab3 = st.tabs(["📝 Add Plan", "📋 My Plans", "🤖 AI Suggestions"])
    
    # TAB 1: Add Investment Plan
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            item_name = st.text_input("Item/Equipment Name", placeholder="e.g., Tractor, Drip Irrigation")
            category = st.selectbox("Category", 
                                   ["Machinery", "Irrigation", "Seeds", "Technology", "Infrastructure", "Other"])
            estimated_cost = st.number_input("Estimated Cost (₹)", min_value=0.0, step=1000.0)
        
        with col2:
            target_date = st.date_input("Target Purchase Date", 
                                       value=datetime.now() + timedelta(days=90))
            priority = st.selectbox("Priority", ["High", "Medium", "Low"])
        
        notes = st.text_area("Notes", placeholder="Why this investment? Expected benefits?")
        
        if st.button("💾 Save Investment Plan", type="primary"):
            if item_name and estimated_cost > 0:
                conn = sqlite3.connect(DB_NAME)
                c = conn.cursor()
                
                c.execute("""INSERT INTO farm_investments 
                            (farmer_id, item_name, category, estimated_cost, target_date, priority, notes)
                            VALUES (?, ?, ?, ?, ?, ?, ?)""",
                         (farmer_id, item_name, category, estimated_cost, 
                          target_date.isoformat(), priority, notes))
                
                conn.commit()
                conn.close()
                
                st.success(f"✅ Investment plan for {item_name} added!")
            else:
                st.error("Please fill required fields")
    
    # TAB 2: My Investment Plans
    with tab2:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        c.execute("""SELECT * FROM farm_investments 
                     WHERE farmer_id = ? ORDER BY priority DESC, target_date ASC""",
                 (farmer_id,))
        investments = c.fetchall()
        conn.close()
        
        if investments:
            total_planned = sum([inv[4] for inv in investments if inv[8] == 'Planned'])
            st.info(f"📊 Total Planned Investment: ₹{total_planned:,.2f}")
            
            for inv in investments:
                with st.expander(f"{inv[2]} - {inv[1]} (₹{inv[4]:,.2f})"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**Priority:** {inv[6]}")
                        st.write(f"**Category:** {inv[3]}")
                    with col2:
                        st.write(f"**Target Date:** {inv[5]}")
                        st.write(f"**Status:** {inv[8]}")
                    with col3:
                        if st.button("✅ Mark Complete", key=f"complete_{inv[0]}"):
                            conn = sqlite3.connect(DB_NAME)
                            c = conn.cursor()
                            c.execute("UPDATE farm_investments SET status = 'Completed' WHERE id = ?", (inv[0],))
                            conn.commit()
                            conn.close()
                            st.rerun()
                    
                    if inv[9]:
                        st.write(f"**Notes:** {inv[9]}")
        else:
            st.info("No investment plans yet. Add your first plan above!")
    
    # TAB 3: AI Suggestions
    with tab3:
        st.write("Get AI-powered investment recommendations based on your farm profile")
        
        col1, col2 = st.columns(2)
        
        with col1:
            budget = st.number_input("Available Budget (₹)", min_value=0.0, step=10000.0, value=50000.0)
            farm_size = st.text_input("Farm Size", value="2 acres", key="investment_farm_size")
        
        with col2:
            current_equip = st.text_input("Current Equipment", placeholder="e.g., Tractor, pump", key="investment_current_equip")
            crop_type = st.text_input("Primary Crop", placeholder="e.g., Wheat, Rice", key="investment_crop_type")
        
        if st.button("🤖 Get AI Suggestions", type="primary"):
            if st.session_state.finance_ai and budget > 0:
                with st.spinner("Fetching investment suggestions..."):
                    suggestions = st.session_state.finance_ai.suggest_investments(
                        budget, current_equip, farm_size, crop_type
                    )
                    st.markdown("### 🎯 Recommended Investments")
                    st.markdown(suggestions)
            else:
                st.error("Please enter budget and AI features must be available")

def render_insurance_tracker(farmer_id):
    """Insurance policy tracker with reminders."""
    st.subheader("🛡️ Insurance Tracker")
    
    tab1, tab2, tab3 = st.tabs(["➕ Add Policy", "📋 My Policies", "💡 Recommendations"])
    
    # TAB 1: Add Insurance
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            insurance_type = st.selectbox("Insurance Type", 
                                         ["Crop Insurance", "Livestock Insurance", "Equipment Insurance", 
                                          "Life Insurance", "Health Insurance", "Other"])
            provider = st.text_input("Insurance Provider", placeholder="e.g., ICICI Lombard, HDFC Ergo")
            policy_number = st.text_input("Policy Number")
            coverage = st.number_input("Coverage Amount (₹)", min_value=0.0, step=10000.0)
        
        with col2:
            premium = st.number_input("Annual Premium (₹)", min_value=0.0, step=1000.0)
            start_date = st.date_input("Start Date")
            end_date = st.date_input("End Date", value=datetime.now() + timedelta(days=365))
            reminder_days = st.number_input("Reminder Before (days)", min_value=7, max_value=90, value=30)
        
        notes = st.text_area("Notes", placeholder="Coverage details, exclusions, claim process...")
        
        if st.button("💾 Save Insurance Policy", type="primary"):
            if insurance_type and policy_number:
                conn = sqlite3.connect(DB_NAME)
                c = conn.cursor()
                
                c.execute("""INSERT INTO farm_insurance 
                            (farmer_id, insurance_type, provider, policy_number, coverage_amount, 
                             premium_amount, start_date, end_date, reminder_days, notes)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                         (farmer_id, insurance_type, provider, policy_number, coverage, premium,
                          start_date.isoformat(), end_date.isoformat(), reminder_days, notes))
                
                conn.commit()
                conn.close()
                
                st.success(f"✅ Insurance policy {policy_number} added!")
            else:
                st.error("Please fill required fields")
    
    # TAB 2: My Policies
    with tab2:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        c.execute("""SELECT * FROM farm_insurance 
                     WHERE farmer_id = ? ORDER BY end_date ASC""", (farmer_id,))
        policies = c.fetchall()
        conn.close()
        
        if policies:
            # Check for renewals
            renewal_alerts = []
            for policy in policies:
                end_date = datetime.fromisoformat(policy[8])
                days_left = (end_date - datetime.now()).days
                
                if 0 < days_left <= policy[9]:  # Within reminder period
                    renewal_alerts.append((policy[2], policy[3], days_left))
            
            if renewal_alerts:
                st.warning(f"⚠️ {len(renewal_alerts)} policy(ies) need renewal soon!")
                for ins_type, provider, days in renewal_alerts:
                    st.write(f"• {ins_type} ({provider}) - {days} days left")
            
            st.markdown("---")
            
            # Display policies
            for policy in policies:
                status_emoji = "✅" if policy[10] == "Active" else "⏸️"
                with st.expander(f"{status_emoji} {policy[2]} - {policy[3]} (₹{policy[5]:,.2f})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Policy Number:** {policy[4]}")
                        st.write(f"**Coverage:** ₹{policy[5]:,.2f}")
                        st.write(f"**Premium:** ₹{policy[6]:,.2f}/year")
                    
                    with col2:
                        st.write(f"**Start Date:** {policy[7]}")
                        st.write(f"**End Date:** {policy[8]}")
                        end_date = datetime.fromisoformat(policy[8])
                        days_left = (end_date - datetime.now()).days
                        st.write(f"**Days Remaining:** {days_left}")
                    
                    if policy[11]:
                        st.write(f"**Notes:** {policy[11]}")
        else:
            st.info("No insurance policies tracked yet")
    
    # TAB 3: Recommendations
    with tab3:
        st.write("Get AI-powered insurance recommendations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            location = st.text_input("Your Location", value=st.session_state.get('user_location', ''), key="insurance_location")
            crop_type = st.text_input("Primary Crop", key="insurance_crop_type")
        
        with col2:
            farm_size = st.text_input("Farm Size", value="2 acres", key="insurance_farm_size")
        
        if st.button("💡 Get Recommendations", type="primary"):
            if st.session_state.finance_ai and location and crop_type:
                with st.spinner("Fetching insurance recommendations..."):
                    recommendations = st.session_state.finance_ai.insurance_recommendations(
                        location, crop_type, farm_size
                    )
                    st.markdown("### 🛡️ Recommended Insurance Options")
                    st.markdown(recommendations)
            else:
                st.error("Please fill all fields")

def render_receipt_generator(farmer_id):
    """Generate digital receipts for sales."""
    st.subheader("🧾 Receipt Generator")
    
    # Get farmer details
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT name, location, contact FROM farmers WHERE ROWID = ?", (farmer_id,))
    farmer = c.fetchone()
    
    if not farmer:
        st.error("Farmer details not found")
        return
    
    farmer_name, farmer_location, farmer_contact = farmer
    
    st.write("Generate professional receipts for your crop sales")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Seller Details")
        st.write(f"**Name:** {farmer_name}")
        st.write(f"**Location:** {farmer_location}")
        st.write(f"**Contact:** {farmer_contact}")
        
        st.markdown("---")
        st.markdown("### Sale Details")
        
        crop_name = st.text_input("Crop/Product Name", placeholder="e.g., Wheat, Rice")
        quantity = st.number_input("Quantity", min_value=0.0, step=1.0)
        unit = st.selectbox("Unit", ["Quintals", "Kg", "Tons", "Bags", "Pieces"])
        price_per_unit = st.number_input("Price per Unit (₹)", min_value=0.0, step=10.0)
    
    with col2:
        st.markdown("### Buyer Details")
        buyer_name = st.text_input("Buyer Name")
        buyer_contact = st.text_input("Buyer Contact")
        buyer_address = st.text_area("Buyer Address")
        
        st.markdown("---")
        sale_date = st.date_input("Sale Date", value=datetime.now())
        payment_mode = st.selectbox("Payment Mode", ["Cash", "Bank Transfer", "UPI", "Cheque"], key="receipt_payment_mode")
        payment_status = st.selectbox("Payment Status", ["Paid", "Pending", "Partial"], key="receipt_payment_status")
    
    # Calculate totals
    total_amount = quantity * price_per_unit
    
    st.markdown("---")
    st.subheader(f"💰 Total Amount: ₹{total_amount:,.2f}")
    
    if st.button("🧾 Generate Receipt", type="primary"):
        if crop_name and buyer_name and quantity > 0:
            # Generate receipt number
            receipt_no = f"RCP{farmer_id}{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Store transaction
            c.execute("""INSERT INTO farm_transactions 
                        (farmer_id, type, category, amount, description, date, payment_mode, receipt_number)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                     (farmer_id, 'Income', 'Crop Sale', total_amount,
                      f"Sale of {quantity} {unit} {crop_name} to {buyer_name}",
                      sale_date.isoformat(), payment_mode, receipt_no))
            
            conn.commit()
            
            # Display receipt
            st.markdown("---")
            st.markdown("### 📄 RECEIPT")
            
            receipt_html = f"""
            <div style='border: 2px solid #4CAF50; padding: 20px; border-radius: 10px; background: white;'>
                <h2 style='color: #4CAF50; text-align: center;'>FARM SALE RECEIPT</h2>
                <p style='text-align: center;'><strong>Receipt No:</strong> {receipt_no}</p>
                <p style='text-align: center;'><strong>Date:</strong> {sale_date.strftime('%d-%m-%Y')}</p>
                
                <hr>
                
                <div style='margin: 20px 0;'>
                    <h4>Seller Details:</h4>
                    <p><strong>Name:</strong> {farmer_name}</p>
                    <p><strong>Location:</strong> {farmer_location}</p>
                    <p><strong>Contact:</strong> {farmer_contact}</p>
                </div>
                
                <div style='margin: 20px 0;'>
                    <h4>Buyer Details:</h4>
                    <p><strong>Name:</strong> {buyer_name}</p>
                    <p><strong>Contact:</strong> {buyer_contact}</p>
                    <p><strong>Address:</strong> {buyer_address}</p>
                </div>
                
                <hr>
                
                <table style='width: 100%; margin: 20px 0;'>
                    <tr style='background: #f0f0f0;'>
                        <th style='padding: 10px; text-align: left;'>Item</th>
                        <th style='padding: 10px; text-align: center;'>Quantity</th>
                        <th style='padding: 10px; text-align: right;'>Price/Unit</th>
                        <th style='padding: 10px; text-align: right;'>Total</th>
                    </tr>
                    <tr>
                        <td style='padding: 10px;'>{crop_name}</td>
                        <td style='padding: 10px; text-align: center;'>{quantity} {unit}</td>
                        <td style='padding: 10px; text-align: right;'>₹{price_per_unit:,.2f}</td>
                        <td style='padding: 10px; text-align: right;'><strong>₹{total_amount:,.2f}</strong></td>
                    </tr>
                </table>
                
                <hr>
                
                <div style='margin: 20px 0;'>
                    <p><strong>Payment Mode:</strong> {payment_mode}</p>
                    <p><strong>Payment Status:</strong> {payment_status}</p>
                    <h3 style='text-align: right; color: #4CAF50;'>Total: ₹{total_amount:,.2f}</h3>
                </div>
                
                <hr>
                
                <p style='text-align: center; font-size: 12px; color: #666;'>
                    This is a computer-generated receipt from Smart Farmer Marketplace<br>
                    Generated on {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}
                </p>
            </div>
            """
            
            st.markdown(receipt_html, unsafe_allow_html=True)
            
            st.success(f"✅ Receipt {receipt_no} generated and transaction recorded!")
            st.info("💡 Tip: Take a screenshot of this receipt for your records")
        else:
            st.error("Please fill all required fields")
    
    conn.close()


