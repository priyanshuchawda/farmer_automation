# 🌾 Smart Farmer Marketplace

A comprehensive multilingual web application built with Streamlit to empower farmers with digital tools for marketplace, weather, AI assistance, and more.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 🌟 Features

### 🌐 **Multilingual Support**
- **3 Languages:** English, Hindi (हिंदी), Marathi (मराठी)
- **279+ Translation Keys** covering all UI elements
- **Instant Language Switching** from sidebar
- **Complete Coverage:** All buttons, labels, forms, and messages

### 👥 **User Management**
- Farmer registration and login
- Profile management with location verification
- Admin panel for farmer management
- Secure password authentication

### 🛒 **Marketplace**
- **Tool Listings:** Rent farm equipment
- **Crop Listings:** Buy/sell crops
- Filter by location and type
- Personal listing management

### 🌤️ **Weather Integration**
- Current weather display
- 5-day forecast
- Location-based weather data
- Integration with OpenWeather API

### 💰 **Market Prices**
- Real-time market prices from AgMarkNet
- Price trends and analysis
- AI-powered price predictions
- Historical price data

### 📅 **Farming Calendar**
- Schedule farming activities
- Task reminders
- Seasonal planning
- AI-powered suggestions

### 🤖 **AI Chatbot**
- Farming advice and tips
- Crop recommendations
- Pest control guidance
- Market timing suggestions
- Powered by Google Gemini AI

### 🗺️ **Location Services**
- GPS-based location detection
- Address verification
- Nearby agricultural services
- Coordinate lookup

### 🏛️ **Government Integration**
- Government schemes information
- Eligibility checker
- Financial tools
- Subsidy information

### 💵 **Farm Finance**
- Income and expense tracking
- Financial overview
- Budget planning
- Receipt generation

## 🚀 Live Demo

**Streamlit Cloud:** Coming soon!

**Repository:** [https://github.com/priyanshuchawda/streamlit_pccoe](https://github.com/priyanshuchawda/streamlit_pccoe)

## 📋 Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Git
- API Keys:
  - Google Gemini API (for AI features)
  - OpenWeather API (for weather)
  - Data.gov.in API (optional)

## 🔧 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/priyanshuchawda/streamlit_pccoe.git
cd streamlit_pccoe
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory:

```env
# Google Gemini AI API Key
GEMINI_API_KEY=your_gemini_api_key_here

# OpenWeather API Key
OPENWEATHER_API_KEY=your_openweather_api_key_here

# Data.gov.in API Key (Optional)
DATAGOVIN_API_KEY=your_datagovin_api_key_here

# Default Language (optional)
LANGUAGE=en
```

**Get API Keys:**
- Google Gemini: [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
- OpenWeather: [https://openweathermap.org/api](https://openweathermap.org/api)
- Data.gov.in: [https://data.gov.in/](https://data.gov.in/)

### 5. Run the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 📁 Project Structure

```
streamlit_pccoe/
├── app.py                          # Main application file
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
├── .streamlit/
│   ├── config.toml                # Streamlit configuration
│   └── secrets.toml.example       # Secrets template for Cloud
├── components/                     # UI components
│   ├── home_page.py               # Dashboard
│   ├── auth_page.py               # Login/Registration
│   ├── profiles_page.py           # Profile management
│   ├── tool_listings.py           # Tool marketplace
│   ├── crop_listings.py           # Crop marketplace
│   ├── view_profile_page.py       # Profile viewer
│   ├── weather_component.py       # Weather display
│   ├── ai_chatbot_page.py         # AI assistant
│   ├── translation_utils.py       # Translation functions
│   └── ...
├── translations/                   # Translation files
│   ├── en.py                      # English
│   ├── hi.py                      # Hindi
│   └── mr.py                      # Marathi
├── database/
│   └── db_functions.py            # Database operations
├── weather/
│   ├── ai_client.py               # AI/API client
│   └── config.py                  # Configuration
├── calender/                      # Calendar components
├── ai/                            # AI modules
├── tests/                         # Test files
├── documentation/                 # Guides and docs
├── farmermarket.db                # SQLite database
├── README.md                      # This file
├── STREAMLIT_CLOUD_DEPLOYMENT.md  # Deployment guide
├── TRANSLATION_COVERAGE.md        # Translation documentation
└── TRANSLATION_QUICK_REFERENCE.md # Translation guide
```

## 🌐 Language Support

| Language | Code | Keys | Status |
|----------|------|------|--------|
| English | `en` | 279 | ✅ Complete |
| Hindi | `hi` | 279 | ✅ Complete |
| Marathi | `mr` | 279 | ✅ Complete |

**Switching Languages:**
1. Look at the sidebar
2. Find the language dropdown at the top
3. Select your preferred language
4. All text updates instantly

**For Developers:**
```python
from components.translation_utils import t

# Use t() function for any text
st.header(t("My Profile"))
st.button(t("Save Changes"))
```

## 🗄️ Database

**SQLite Database** (`farmermarket.db`)

**Tables:**
- `farmers` - User profiles
- `tools` - Tool listings
- `crops` - Crop listings
- `calendar_events` - Scheduled tasks
- `market_prices_cache` - Cached price data
- `weather_cache` - Cached weather data

**Automatic Initialization:**
- Database created on first run
- Tables auto-generated
- Sample data support

## 📱 Default Users

**Admin Account:**
```
Username: admin
Password: admin123
```

**Test Farmer Account:**
```
Username: test_farmer
Password: test123
```

(Change these in production!)

## 🎨 Customization

### Theme Colors

Edit `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#2E8B57"
backgroundColor = "#F5F5F5"
secondaryBackgroundColor = "#FFFFFF"
textColor = "#262730"
```

### Adding Translations

See `TRANSLATION_QUICK_REFERENCE.md` for detailed guide.

1. Add to `translations/en.py`
2. Add to `translations/hi.py`
3. Add to `translations/mr.py`
4. Use `t("Your Text")` in code

## 🚀 Deployment to Streamlit Cloud

See **[STREAMLIT_CLOUD_DEPLOYMENT.md](STREAMLIT_CLOUD_DEPLOYMENT.md)** for complete guide.

**Quick Steps:**
1. Push to GitHub ✅ (Already done)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repository: `priyanshuchawda/streamlit_pccoe`
4. Add API keys to secrets
5. Deploy!

## 📊 Technologies Used

- **Frontend:** Streamlit
- **Backend:** Python 3.9+
- **Database:** SQLite
- **AI:** Google Gemini API
- **Weather:** OpenWeather API
- **Maps:** Google Maps Grounding
- **Data:** AgMarkNet, Data.gov.in
- **ML:** scikit-learn, XGBoost
- **Visualization:** Plotly

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

**Team AgroLink** - PCCOE

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/priyanshuchawda/streamlit_pccoe/issues)
- **Email:** support@example.com
- **Documentation:** See `/documentation` folder

## 🙏 Acknowledgments

- Streamlit team for the amazing framework
- Google for Gemini AI API
- OpenWeather for weather data
- AgMarkNet for market prices
- All open-source contributors

## 📈 Roadmap

- [ ] PostgreSQL database support
- [ ] Mobile app version
- [ ] Advanced analytics dashboard
- [ ] Community forum
- [ ] Video tutorials
- [ ] More language support (Tamil, Telugu, etc.)
- [ ] Offline mode
- [ ] Push notifications

## 🔒 Security

- Password hashing (implement bcrypt in production)
- SQL injection prevention
- XSS protection
- CSRF protection
- Secure API key management

## 📸 Screenshots

_Coming soon!_

---

**Made with ❤️ for Indian Farmers**

**⭐ Star this repo if you find it useful!**
