# 📚 Smart Farmer Marketplace - Codebase Documentation

**Version:** 1.0 (Post Phase 1)  
**Last Updated:** 2025-01-09  
**Status:** Production Ready

---

## 📁 Project Structure

```
pccoe2/
│
├── 📄 app.py                          # Main application entry point
├── 📄 requirements.txt                # Python dependencies
├── 📄 .env                           # Environment variables (API keys)
├── 📄 farmermarket.db                # SQLite database
│
├── 📂 components/                    # UI Components
│   ├── auth_page.py                 # Login & Registration
│   ├── welcome_screen.py            # First-time user onboarding
│   ├── home_page.py                 # Dashboard/Home view
│   ├── view_profile_page.py         # Profile display
│   ├── profiles_page.py             # Admin: Manage profiles
│   ├── tool_listings.py             # Tool marketplace
│   ├── crop_listings.py             # Crop marketplace
│   ├── weather_component.py         # Weather forecasts
│   ├── market_price_scraper.py      # Market price data
│   └── calendar_integration.py      # Calendar with weather
│
├── 📂 database/                      # Database Layer
│   └── db_functions.py              # All database operations
│
├── 📂 weather/                       # Weather Module
│   ├── weather_assistant.py         # Weather queries
│   ├── combined_forecast.py         # Forecast aggregation
│   ├── ai_client.py             # AI AI integration
│   └── models/                      # ML prediction models
│
├── 📂 calender/                      # Calendar Module
│   ├── calendar_component.py        # Calendar UI
│   ├── ai_service.py                # AI planning service
│   ├── day_view.py                  # Day view component
│   ├── week_view.py                 # Week view component
│   ├── config.py                    # Calendar config
│   └── utils.py                     # Calendar utilities
│
├── 📂 ai/                            # AI Services
│   └── (AI-related modules)
│
├── 📂 documentation/                 # Documentation
│   └── (Project docs)
│
└── 📂 migrations/                    # Database Migrations
    └── migrate_password_column.py   # Password field migration

```

---

## 🔧 Core Files

### 1. **app.py** - Main Application
**Purpose:** Application entry point and routing  
**Lines:** ~250  
**Key Functions:**
- Initialize database
- Configure Streamlit page
- Authentication check
- Route to different pages based on menu selection
- Manage session state

**Flow:**
```
1. Load environment variables
2. Initialize database
3. Check if user logged in
   ├─ NO  → Show auth_page
   ├─ YES → Check if first login
   │         ├─ YES → Show welcome_screen
   │         └─ NO  → Show main app
4. Render sidebar with user info
5. Route to selected page
```

**Session State Variables:**
- `logged_in` (bool) - Authentication status
- `role` (str) - "Farmer" or "Admin"
- `farmer_name` (str) - Logged-in user name
- `farmer_profile` (dict) - Full user profile
- `show_welcome` (bool) - Show welcome screen
- `tools` (DataFrame) - Tools data
- `crops` (DataFrame) - Crops data

---

## 📦 Components Directory

### **auth_page.py** - Authentication Component
**Purpose:** Complete login and registration system  
**Lines:** ~594  
**Features:**
- Two-tab interface (Login / Registration)
- 4-step registration wizard
- Password strength indicator
- Coordinate auto-fetch using AI AI
- Admin login section
- Sidebar with features preview

**Functions:**
```python
def check_password_strength(password) -> tuple[int, str]
    # Returns strength score (0-3) and label

def render_auth_page() -> None
    # Main authentication interface
```

**Registration Steps:**
1. **Basic Info:** Name, Password, Contact
2. **Farm Details:** Location, Size, Unit
3. **Weather Setup:** Weather location + auto-coordinates
4. **Completion:** Summary and login redirect

---

### **welcome_screen.py** - Onboarding Component
**Purpose:** First-time user tutorial  
**Lines:** ~230  
**Features:**
- Personalized welcome message
- 6 feature cards overview
- 4-step getting started guide
- Quick action buttons
- Skip tutorial option
- Sidebar with quick skip button

**Functions:**
```python
def render_welcome_screen() -> None
    # Display welcome tutorial for new users
```

---

### **home_page.py** - Dashboard
**Purpose:** Main landing page after login  
**Lines:** ~72  
**Features:**
- Welcome banner with Unsplash image
- 3 value proposition cards
- Quick stats overview

**Functions:**
```python
def render_home_page() -> None
    # Display main dashboard

def render_db_check() -> None
    # Admin: View database tables
```

---

### **view_profile_page.py** - Profile Display
**Purpose:** Show farmer's personal profile  
**Lines:** ~27  
**Features:**
- Display all profile fields
- Location and farm details
- Weather integration info
- Coordinates display

**Functions:**
```python
def render_view_profile_page() -> None
    # Display current user's profile
```

---

### **profiles_page.py** - Profile Management (Admin)
**Purpose:** Admin tool to manage farmer profiles  
**Lines:** ~88  
**Features:**
- Add new farmer profiles
- Update existing profiles
- View all farmers table
- Coordinate fetching

**Functions:**
```python
def render_profiles_page() -> None
    # Admin: Manage all farmer profiles
```

---

### **tool_listings.py** - Tool Marketplace
**Purpose:** List and manage tool rentals  
**Lines:** ~150  
**Features:**
- Create tool listings
- Browse all tools
- Filter by farmer
- Edit/delete own listings
- Pre-fill with profile data

**Functions:**
```python
def render_tool_listing(farmer_name: str) -> None
    # Form to create tool listing

def render_tool_management(tools_df, farmer_name) -> None
    # Display and manage tool listings
```

---

### **crop_listings.py** - Crop Marketplace
**Purpose:** List and manage crop sales  
**Lines:** ~150  
**Features:**
- Create crop listings
- Browse all crops
- Filter by farmer
- Edit/delete own listings
- Pre-fill with profile data

**Functions:**
```python
def render_crop_listing(farmer_name: str) -> None
    # Form to create crop listing

def render_crop_management(crops_df, farmer_name) -> None
    # Display and manage crop listings
```

---

### **weather_component.py** - Weather Forecasts
**Purpose:** Display weather predictions  
**Lines:** ~200  
**Features:**
- 7-day forecast display
- ML model predictions
- API data integration
- Natural language queries
- Location-based forecasts

**Functions:**
```python
def render_weather_component() -> None
    # Display weather forecast interface
```

---

### **market_price_scraper.py** - Market Prices
**Purpose:** Display current market prices  
**Lines:** ~150  
**Features:**
- Scrape AGMARKNET data
- Display commodity prices
- Filter by state/district
- Cache for performance

**Functions:**
```python
def render_market_price() -> None
    # Display market price data
```

---

### **calendar_integration.py** - Smart Calendar
**Purpose:** Farming activity planner with weather  
**Lines:** ~594  
**Features:**
- Month/Week/Day views
- AI-powered plan generation
- Weather-integrated events
- CRUD operations on events
- Location-based weather alerts
- Quick task addition

**Functions:**
```python
def get_weather_for_event(farmer_profile, event_date) -> dict
    # Fetch weather for specific date

def create_weather_alert(weather_data) -> str
    # Generate alert message

def render_integrated_calendar(farmer_name: str) -> None
    # Main calendar interface
```

---

## 🗄️ Database Directory

### **db_functions.py** - Database Operations
**Purpose:** All database CRUD operations  
**Lines:** ~149  
**Database Schema:**

**Tables:**
1. **farmers**
   - name (TEXT, PRIMARY KEY)
   - location (TEXT)
   - farm_size (REAL)
   - farm_unit (TEXT)
   - contact (TEXT)
   - weather_location (TEXT)
   - latitude (REAL)
   - longitude (REAL)
   - password (TEXT)

2. **tools**
   - Farmer (TEXT)
   - Location (TEXT)
   - Tool (TEXT)
   - Rate (REAL)
   - Contact (TEXT)
   - Notes (TEXT)

3. **crops**
   - Farmer (TEXT)
   - Location (TEXT)
   - Crop (TEXT)
   - Quantity (TEXT)
   - Expected_Price (REAL)
   - Contact (TEXT)
   - Listing_Date (TEXT)

4. **calendar_events**
   - id (INTEGER, PRIMARY KEY, AUTOINCREMENT)
   - farmer_name (TEXT, FOREIGN KEY)
   - event_date (TEXT)
   - event_time (TEXT)
   - event_title (TEXT)
   - event_description (TEXT)
   - weather_alert (TEXT)
   - created_at (TEXT)

**Functions:**
```python
def init_db() -> None
    # Initialize database and create tables

def add_data(table_name: str, data_tuple: tuple) -> None
    # Insert data into specified table

def get_data(table_name: str) -> pd.DataFrame
    # Retrieve all data from table

def get_farmer_profile(name: str) -> dict
    # Get farmer profile by name

def verify_farmer_login(name: str, password: str) -> dict
    # Verify login credentials

def get_farmer_events(farmer_name: str) -> pd.DataFrame
    # Get calendar events for farmer

def update_farmer_profile(...) -> None
    # Update farmer profile

def delete_event(event_id: int) -> None
    # Delete calendar event

def update_event(...) -> None
    # Update calendar event
```

---

## 🌤️ Weather Directory

### **weather_assistant.py**
**Purpose:** Natural language weather queries  
**Functions:**
- Parse weather queries
- Fetch location-specific data
- Return formatted responses

### **combined_forecast.py**
**Purpose:** Aggregate weather predictions  
**Functions:**
- Combine ML model predictions
- Integrate API data
- Return unified forecast

### **ai_client.py**
**Purpose:** Google AI AI integration  
**Functions:**
- Coordinate lookup from location names
- Natural language processing
- AI-powered recommendations

### **models/** Directory
**Purpose:** ML prediction models  
**Contents:**
- Trained XGBoost models
- Random Forest models
- Linear Regression models
- Model metadata

---

## 📅 Calendar Directory

### **calendar_component.py**
**Purpose:** Month view calendar  
**Functions:** Render monthly calendar grid

### **day_view.py**
**Purpose:** Single day detailed view  
**Functions:** Show all events for one day

### **week_view.py**
**Purpose:** Week view calendar  
**Functions:** Show 7-day schedule

### **ai_service.py**
**Purpose:** AI farming plan generation  
**Functions:** Generate activity schedules using AI

### **config.py**
**Purpose:** Calendar configuration  
**Contents:** Translations, settings

### **utils.py**
**Purpose:** Calendar utilities  
**Functions:** Date calculations, helpers

---

## 🔐 Authentication Flow

### User Journey:

```
┌──────────────────────────────────────┐
│   1. User opens app                  │
│      ↓                               │
│   2. Database initialized            │
│      ↓                               │
│   3. Check session_state.logged_in   │
│      ├─ False → Show auth_page       │
│      └─ True → Continue              │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│   Auth Page (auth_page.py)           │
│      ├─ Tab 1: Login                 │
│      │   ├─ Enter name & password    │
│      │   ├─ Verify credentials       │
│      │   └─ Set session_state        │
│      └─ Tab 2: Registration          │
│          ├─ Step 1: Basic Info       │
│          ├─ Step 2: Farm Details     │
│          ├─ Step 3: Weather Location │
│          └─ Step 4: Complete         │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│   After Login                         │
│      ├─ Check if first login         │
│      │   └─ YES → Show welcome_screen│
│      └─ NO → Show main app           │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│   Main App                            │
│      ├─ Render sidebar with user info│
│      ├─ Show menu options            │
│      └─ Route to selected page       │
└──────────────────────────────────────┘
```

---

## 🎨 UI/UX Design Patterns

### Color Scheme
- **Primary:** #2E8B57 (SeaGreen)
- **Secondary:** #3CB371 (MediumSeaGreen)
- **Success:** #4CAF50
- **Warning:** #FF9800
- **Error:** #F44336
- **Background:** #F5F5F5
- **Cards:** #FFFFFF

### Component Patterns

**1. Info Boxes:**
```python
st.info("Message")      # Blue - Information
st.success("Message")   # Green - Success
st.warning("Message")   # Orange - Warning
st.error("Message")     # Red - Error
```

**2. Forms:**
```python
with st.form("form_name"):
    # Form fields
    submit = st.form_submit_button("Submit")
    if submit:
        # Handle submission
```

**3. Columns:**
```python
col1, col2, col3 = st.columns(3)
with col1:
    # Column 1 content
```

**4. Progress Indicators:**
```python
progress_cols = st.columns(4)
for i in range(4):
    with progress_cols[i]:
        if i < current_step:
            st.success("✓ Step")
        elif i == current_step:
            st.info("Current Step")
        else:
            st.text("Future Step")
```

---

## 🔄 Session State Management

### Critical Variables:
```python
# Authentication
st.session_state.logged_in = True/False
st.session_state.role = "Farmer" | "Admin"
st.session_state.farmer_name = "John Doe"
st.session_state.farmer_profile = {...}

# Navigation
st.session_state.show_welcome = True/False
st.session_state.menu_selection = "Page Name"

# Registration
st.session_state.reg_step = 1-4
st.session_state.reg_data = {...}

# Data
st.session_state.tools = DataFrame
st.session_state.crops = DataFrame

# Database
st.session_state.db_initialized = True/False
```

### State Lifecycle:
```
1. App starts → Check if keys exist
2. Login → Set auth keys
3. Navigation → Update menu_selection
4. Logout → Clear all keys
5. Rerun → Preserve state
```

---

## 🚀 Performance Optimizations

### 1. **Database Connection Pooling**
- Single connection per operation
- Automatic close after use

### 2. **Data Caching**
```python
st.session_state.tools = get_data("tools")  # Cached
st.session_state.crops = get_data("crops")  # Cached
```

### 3. **Lazy Loading**
- Components loaded only when needed
- Stop execution after auth check

### 4. **Efficient Queries**
```python
# Good: Fetch only needed columns
SELECT name, location FROM farmers

# Avoid: Fetch all when not needed
SELECT * FROM large_table
```

---

## 🧪 Testing Guidelines

### Manual Testing Checklist:

**Authentication:**
- [ ] Login with valid credentials
- [ ] Login with invalid credentials
- [ ] Register new farmer
- [ ] All 4 registration steps work
- [ ] Password strength indicator works
- [ ] Admin login works

**Navigation:**
- [ ] All menu items accessible
- [ ] Sidebar visible on all pages
- [ ] Logout works correctly
- [ ] Welcome screen shows for new users
- [ ] Welcome screen can be skipped

**Data Operations:**
- [ ] Create tool listing
- [ ] Create crop listing
- [ ] Edit own listings
- [ ] Delete own listings
- [ ] View other farmers' listings

**Integration:**
- [ ] Weather data loads
- [ ] Calendar syncs with profile
- [ ] Market prices display
- [ ] AI services respond

---

## 🐛 Common Issues & Solutions

### Issue 1: "no such column: password"
**Solution:** Run migration script
```bash
python migrate_password_column.py
```

### Issue 2: Sidebar not visible
**Solution:** Ensure sidebar code in each component that uses st.stop()

### Issue 3: Session state lost on rerun
**Solution:** Don't modify session_state inside callbacks

### Issue 4: Coordinates not fetching
**Solution:** Check .env file has AI_API_KEY

### Issue 5: Weather data not loading
**Solution:** Check .env file has OPENWEATHER_API_KEY

---

## 📝 Development Guidelines

### Adding New Components:
1. Create file in `components/` directory
2. Define render function: `def render_component_name():`
3. Import in `app.py`
4. Add menu option if needed
5. Update this documentation

### Database Changes:
1. Create migration script in root
2. Update `db_functions.py`
3. Test on sample database
4. Document schema changes

### API Integration:
1. Add key to `.env.example`
2. Load in component using `os.getenv()`
3. Add error handling
4. Cache responses when possible

---

## 🔒 Security Considerations

### Current Implementation:
- ✅ Password-based authentication
- ✅ Session-based authorization
- ✅ SQL injection prevention (parameterized queries)
- ✅ Admin password hardcoded (change in production)

### Future Improvements:
- [ ] Password hashing (bcrypt)
- [ ] JWT tokens
- [ ] Rate limiting
- [ ] HTTPS enforcement
- [ ] CSRF protection

---

## 📊 File Size Summary

| File | Lines | Purpose |
|------|-------|---------|
| app.py | ~250 | Main app |
| auth_page.py | ~594 | Login/Register |
| welcome_screen.py | ~230 | Onboarding |
| calendar_integration.py | ~594 | Calendar |
| db_functions.py | ~149 | Database |
| tool_listings.py | ~150 | Tools |
| crop_listings.py | ~150 | Crops |
| weather_component.py | ~200 | Weather |
| market_price_scraper.py | ~150 | Prices |

**Total Core Code:** ~2,500 lines

---

## 🎯 Next Steps (Phase 2 Preview)

1. **Refactoring:**
   - Split large files into smaller modules
   - Create helper functions directory
   - Improve code reusability

2. **Features:**
   - Dashboard with analytics
   - Reorganized menu structure
   - Search functionality
   - Notifications system

3. **Documentation:**
   - API documentation
   - User manual (PDF)
   - Video tutorials
   - Developer guide

---

## 📞 Support & Maintenance

### For Developers:
- Read this documentation first
- Check PHASE1_IMPLEMENTATION.md for recent changes
- Use QUICK_START.md for setup

### For Users:
- See QUICK_START.md for login help
- Check PHASE1_IMPLEMENTATION.md for new features
- Contact admin for access issues

---

**Document Version:** 1.0  
**Maintained By:** AgroLink Development Team  
**Last Review:** 2025-01-09
