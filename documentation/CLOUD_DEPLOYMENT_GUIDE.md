# ☁️ Cloud Deployment Guide - Streamlit Cloud

## 🎯 Smart Environment Configuration

The app is now configured to work seamlessly both **locally** and on **Streamlit Cloud**.

---

## 🔧 How It Works

### Local Development:
```python
# In app.py and weather/config.py
if os.getenv("STREAMLIT_RUNTIME") is None:
    load_dotenv()  # Load .env only if running locally
```

**Behavior:**
- `STREAMLIT_RUNTIME` is `None` locally
- `.env` file is loaded
- Environment variables from `.env` are used

### Streamlit Cloud:
**Behavior:**
- `STREAMLIT_RUNTIME` is set (exists in cloud)
- `.env` file is NOT loaded
- Streamlit Secrets are used instead

---

## 📁 File Setup

### 1. Local Setup (`.env` file)

Create/Update `.env` file in project root:

```env
# API Keys
GEMINI_API_KEY=your_gemini_api_key_here
OPENWEATHER_API_KEY=your_openweather_api_key_here

# Optional Settings
LANGUAGE=en
```

**Location:** `C:\Users\Admin\Desktop\pccoe2\.env`

### 2. Cloud Setup (Streamlit Secrets)

In Streamlit Cloud Dashboard:

1. Go to your app settings
2. Click on "Secrets" section
3. Add the following in TOML format:

```toml
# Streamlit Secrets (secrets.toml format)
GEMINI_API_KEY = "your_gemini_api_key_here"
OPENWEATHER_API_KEY = "your_openweather_api_key_here"
```

---

## 🚀 API Key Loading Priority

### Weather Config (`weather/config.py`):

```python
def get_gemini_api_key():
    """Get the Gemini API key from environment variables or Streamlit secrets."""
    try:
        # Priority 1: Streamlit Secrets (Cloud)
        return st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
    except:
        # Priority 2: Environment Variables (Local)
        return os.getenv("GEMINI_API_KEY")
```

**Loading Order:**
1. **Cloud**: Tries `st.secrets` first
2. **Local**: Falls back to `os.getenv()`
3. **Fallback**: Returns from whichever source is available

---

## ✅ Verification

### Test Local Setup:
```python
# Run this in Python
import os
from dotenv import load_dotenv

load_dotenv()
print("✅ GEMINI_API_KEY:", bool(os.getenv("GEMINI_API_KEY")))
print("✅ OPENWEATHER_API_KEY:", bool(os.getenv("OPENWEATHER_API_KEY")))
```

### Test Cloud Setup:
```python
# In your Streamlit app (deployed)
import streamlit as st

st.write("✅ GEMINI_API_KEY:", bool(st.secrets.get("GEMINI_API_KEY")))
st.write("✅ OPENWEATHER_API_KEY:", bool(st.secrets.get("OPENWEATHER_API_KEY")))
```

---

## 🔐 Security Best Practices

### ✅ DO:
- Keep `.env` file in `.gitignore`
- Use Streamlit Secrets for cloud deployment
- Never commit API keys to Git
- Rotate API keys regularly

### ❌ DON'T:
- Don't hardcode API keys in code
- Don't commit `.env` to repository
- Don't share API keys publicly
- Don't use same keys for dev and production

---

## 📋 Deployment Checklist

### Before Deploying to Cloud:

- [ ] **1. Check `.gitignore`**
  ```
  .env
  *.env
  .env.local
  ```

- [ ] **2. Verify Local Setup**
  - `.env` file exists
  - All API keys present
  - App runs locally

- [ ] **3. Prepare Cloud Secrets**
  - Copy keys from `.env`
  - Convert to TOML format
  - Test format validity

- [ ] **4. Deploy to Streamlit Cloud**
  - Push code to GitHub
  - Connect repository in Streamlit Cloud
  - Add secrets in dashboard

- [ ] **5. Test Deployment**
  - Verify app loads
  - Check API key loading
  - Test all features

---

## 🔄 Migration from Old to New System

### Old Code:
```python
# Old way (only works locally)
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
```

### New Code:
```python
# New way (works both locally and cloud)
import os
from dotenv import load_dotenv

if os.getenv("STREAMLIT_RUNTIME") is None:
    load_dotenv()

# Smart loading
try:
    api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
except:
    api_key = os.getenv("GEMINI_API_KEY")
```

---

## 🛠️ Troubleshooting

### Issue: API key not loading locally
**Solution:**
1. Check `.env` file exists in project root
2. Verify format: `GEMINI_API_KEY=your_key_here` (no quotes)
3. Restart Python/Streamlit

### Issue: API key not loading on cloud
**Solution:**
1. Check Streamlit Secrets are added correctly
2. Verify TOML format (use quotes)
3. Redeploy the app

### Issue: App works locally but not on cloud
**Solution:**
1. Check all dependencies in `requirements.txt`
2. Verify Streamlit Secrets are saved
3. Check cloud logs for errors

### Issue: "STREAMLIT_RUNTIME" check not working
**Solution:**
This is expected behavior:
- Locally: `os.getenv("STREAMLIT_RUNTIME")` returns `None`
- Cloud: It returns a value (any non-None value)

---

## 📊 Environment Variables Reference

### Required:
| Variable | Description | Format |
|----------|-------------|--------|
| `GEMINI_API_KEY` | Google Gemini AI API Key | String |
| `OPENWEATHER_API_KEY` | OpenWeather API Key | String |

### Optional:
| Variable | Description | Default |
|----------|-------------|---------|
| `LANGUAGE` | Default language | `en` |

---

## 🎯 Login Flow Changes

### ✅ New Behavior:
1. User enters credentials
2. Click "Login" button
3. ✅ Verification successful
4. 🎈 Balloons animation
5. **→ Automatically redirected to Home Page**

### Before:
```
Login → Welcome Screen → Click "Continue" → Home Page
```

### After:
```
Login → Home Page (Direct)
```

**Welcome Screen:** Disabled by default. Can be re-enabled if needed for tutorials.

---

## 📝 Configuration Files

### `.gitignore` (Add these lines)
```gitignore
# Environment variables
.env
.env.local
.env.*.local
*.env

# Streamlit
.streamlit/secrets.toml
```

### `requirements.txt` (Verify these are present)
```txt
streamlit
python-dotenv
pandas
google-generativeai
requests
beautifulsoup4
deep-translator
```

---

## 🚀 Quick Start

### Local Development:
```bash
# 1. Clone repository
git clone <your-repo>

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file
echo "GEMINI_API_KEY=your_key_here" > .env
echo "OPENWEATHER_API_KEY=your_key_here" >> .env

# 4. Run app
streamlit run app.py
```

### Cloud Deployment:
```bash
# 1. Push to GitHub
git add .
git commit -m "Ready for deployment"
git push origin main

# 2. In Streamlit Cloud:
# - Connect repository
# - Add secrets in dashboard
# - Deploy

# 3. Done! App is live
```

---

## 💡 Tips

1. **Local Testing:** Always test with `.env` before deploying
2. **Cloud Testing:** Use Streamlit Cloud's "Reboot" to apply secret changes
3. **Security:** Never log or print API keys
4. **Version Control:** Keep `.env.example` in repo with dummy values
5. **Documentation:** Update this guide when adding new environment variables

---

## 📞 Support

If you encounter issues:
1. Check this guide first
2. Verify `.env` format
3. Check Streamlit Cloud logs
4. Review error messages
5. Contact development team

---

**Last Updated:** 2025-11-09  
**Version:** 2.0  
**Status:** ✅ Production Ready
