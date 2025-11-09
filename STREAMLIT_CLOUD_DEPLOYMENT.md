# 🚀 Streamlit Cloud Deployment Guide

## ✅ Your App is Ready for Deployment!

This Smart Farmer Marketplace application is fully configured and ready to deploy on Streamlit Cloud.

## 📋 Pre-Deployment Checklist

✅ **Repository Setup**
- [x] GitHub repository created: `https://github.com/priyanshuchawda/streamlit_pccoe.git`
- [x] All files committed and pushed
- [x] `.gitignore` configured properly
- [x] Environment variables template created

✅ **Application Configuration**
- [x] `requirements.txt` with all dependencies
- [x] `.streamlit/config.toml` for theme and settings
- [x] Smart environment loading (local `.env` or Cloud secrets)
- [x] Database initialization on first run
- [x] Complete translation support (English, Hindi, Marathi)

✅ **Code Quality**
- [x] No hardcoded API keys
- [x] Proper error handling
- [x] Session state management
- [x] All syntax errors fixed

## 🔧 Deployment Steps

### Step 1: Access Streamlit Cloud

1. Go to **[share.streamlit.io](https://share.streamlit.io)**
2. Sign in with your GitHub account (`priyanshuchawda`)
3. Click **"New app"**

### Step 2: Configure Your App

Fill in the deployment form:

**Repository:**
```
priyanshuchawda/streamlit_pccoe
```

**Branch:**
```
main
```

**Main file path:**
```
app.py
```

**App URL (custom URL - optional):**
```
pccoe-farmer-marketplace
```
(You'll get: `https://pccoe-farmer-marketplace.streamlit.app`)

### Step 3: Add Secrets

Click on **"Advanced settings"** → **"Secrets"**

Copy and paste this configuration (replace with your actual API keys):

```toml
# Google Gemini AI API Key
# Get from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY = "your_actual_gemini_api_key"

# OpenWeather API Key  
# Get from: https://openweathermap.org/api
OPENWEATHER_API_KEY = "your_actual_openweather_api_key"

# Data.gov.in API Key (Optional)
DATAGOVIN_API_KEY = "your_datagovin_api_key_or_leave_blank"

# Default Language (optional)
LANGUAGE = "en"
```

### Step 4: Deploy

1. Click **"Deploy!"**
2. Wait 2-5 minutes for initial deployment
3. Your app will be live at: `https://your-app-name.streamlit.app`

## 🔑 Getting API Keys

### 1. Google Gemini API Key (Required)
- Visit: [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
- Sign in with your Google account
- Click **"Get API Key"** or **"Create API Key"**
- Copy the key and add to Streamlit secrets

**Features using this:**
- AI Chatbot
- AI-powered suggestions
- Location coordinate lookup
- Address verification

### 2. OpenWeather API Key (Required)
- Visit: [https://openweathermap.org/api](https://openweathermap.org/api)
- Sign up for a free account
- Go to **"API keys"** tab
- Copy your default API key or generate a new one
- Add to Streamlit secrets

**Features using this:**
- Weather forecasts
- Current weather data
- Location-based weather

### 3. Data.gov.in API Key (Optional)
- Visit: [https://data.gov.in/](https://data.gov.in/)
- Register for an account
- Request API access
- Add to Streamlit secrets (or leave blank if not using)

**Features using this:**
- Government schemes data
- Market price data (backup source)

## 📱 Features Available on Streamlit Cloud

✅ **Full Functionality:**
- User authentication (login/register)
- Multi-language support (English, Hindi, Marathi)
- Profile management
- Tool and crop listings
- Weather forecasts
- Market prices
- AI chatbot
- Farming calendar
- Government schemes
- Farm finance management
- Location services

⚠️ **Limited Features:**
- Browser GPS (works but requires user permission on Cloud)
- File uploads (limited to 200MB)

## 🔍 Environment Variables Handling

The app automatically detects the environment:

**Local Development:**
```python
# Loads from .env file
if os.getenv("STREAMLIT_RUNTIME") is None:
    load_dotenv()
```

**Streamlit Cloud:**
```python
# Uses Streamlit secrets automatically
# Accessed via st.secrets["KEY_NAME"]
```

## 🗄️ Database Handling

The app uses SQLite database (`farmermarket.db`):

**On First Run:**
- Database is automatically created
- Tables are initialized
- Sample data can be added

**On Streamlit Cloud:**
- Database file is created in the app's runtime
- Data persists during the session
- **Note:** Data is reset when the app restarts (cloud limitations)

**For Production:**
Consider migrating to a persistent database like:
- PostgreSQL (Supabase, Neon, etc.)
- MySQL (PlanetScale, Railway, etc.)
- MongoDB Atlas

## 🎨 Customization

### Theme Colors
Edit `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#2E8B57"  # Green
backgroundColor = "#F5F5F5"  # Light gray
secondaryBackgroundColor = "#FFFFFF"  # White
textColor = "#262730"  # Dark gray
```

### App Settings
```toml
[server]
maxUploadSize = 200  # Maximum file upload size in MB
```

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError"
**Solution:** Check `requirements.txt` has all dependencies listed

### Issue: "API Key not found"
**Solution:** Add API keys to Streamlit Cloud secrets (Step 3)

### Issue: "Database locked"
**Solution:** Restart the app from Streamlit Cloud dashboard

### Issue: "Import errors"
**Solution:** Ensure all custom modules are in the repository

### Issue: "Translation not working"
**Solution:** Verify `translations/` folder is committed to GitHub

## 📊 Monitoring Your App

**Streamlit Cloud Dashboard:**
- View logs in real-time
- Monitor app health
- Check resource usage
- Restart app if needed

**Access Logs:**
1. Go to your app's dashboard
2. Click on **"Manage app"**
3. View **"Logs"** tab
4. Check for errors or warnings

## 🔄 Updating Your App

**Automatic Updates:**
- Push changes to GitHub
- Streamlit Cloud auto-detects and redeploys
- Wait 1-2 minutes for update

**Manual Update:**
```bash
git add .
git commit -m "Update description"
git push origin main
```

**Force Reboot:**
1. Go to Streamlit Cloud dashboard
2. Click **"⋮"** (three dots)
3. Select **"Reboot app"**

## 🌐 Sharing Your App

Once deployed, share your app URL:
```
https://pccoe-farmer-marketplace.streamlit.app
```

**Public Access:**
- Anyone with the URL can access
- No authentication required for viewing
- Login required for using features

**Custom Domain (optional):**
- Available on Streamlit Cloud Team/Enterprise plans
- Configure DNS settings
- Map custom domain to your app

## 📈 Performance Tips

1. **Enable Caching:**
   - Already implemented in the app
   - Uses `@st.cache_data` for API calls

2. **Optimize Images:**
   - Use appropriate image sizes
   - Compress images before upload

3. **Database Queries:**
   - Already optimized with SQLite
   - Consider pagination for large datasets

4. **Resource Usage:**
   - Free tier: Limited resources
   - Upgrade if needed for better performance

## 🎉 Post-Deployment

**Verify Everything Works:**
- [ ] Homepage loads correctly
- [ ] Language switching works
- [ ] Login/Registration functional
- [ ] Profile creation works
- [ ] Listings can be created
- [ ] Weather data displays
- [ ] Market prices load
- [ ] AI chatbot responds
- [ ] All translations display correctly

## 📞 Support

**Streamlit Community:**
- Forum: [discuss.streamlit.io](https://discuss.streamlit.io)
- Documentation: [docs.streamlit.io](https://docs.streamlit.io)
- GitHub: [github.com/streamlit/streamlit](https://github.com/streamlit/streamlit)

**Your Repository:**
- Issues: `https://github.com/priyanshuchawda/streamlit_pccoe/issues`
- Pull Requests: Welcome!

---

## 🚀 Ready to Deploy!

Your Smart Farmer Marketplace is fully configured and ready for Streamlit Cloud deployment. Follow the steps above and your app will be live in minutes!

**Repository:** `https://github.com/priyanshuchawda/streamlit_pccoe.git`

**Expected URL:** `https://[your-app-name].streamlit.app`

Good luck! 🌾✨
