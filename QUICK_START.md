# 🚀 Quick Start Guide - Smart Farmer Marketplace

## 🎯 For Existing Users (Quick Login)

Your database already has farmers. Use these credentials:

**Username:** `priyanshu chawda` (or any existing farmer name)  
**Password:** `farmer123`

---

## 🆕 For New Users (Registration)

### Step 1: Run the App
```bash
streamlit run app.py
```

### Step 2: Register
1. Click **"🌱 New Farmer Registration"** tab
2. Fill in your details:
   - Name (e.g., "Raj Patel")
   - Password (min 4 characters)
   - Mobile number
3. Click **"Next: Farm Details →"**
4. Add farm information:
   - Location (e.g., "Pune, Maharashtra")
   - Farm size and unit
5. Click **"Next: Weather Setup →"**
6. Confirm weather location
7. Click **"🎉 Create My Account"**
8. Wait for coordinate fetching (optional)
9. Click **"🌱 Go to Login"**
10. Login with your new credentials!

### Step 3: Explore
After login, you'll see a welcome screen with:
- Quick overview of features
- 4-step getting started guide
- Action buttons to explore

---

## 👨‍💼 For Admin

1. Scroll to bottom of login page
2. Click **"🔐 Admin Login"** expander
3. Enter password: `admin`
4. Access admin features

---

## ⚡ Features Available

### For Farmers:
- 🏠 **Home** - Dashboard overview
- 👤 **View Profile** - See and edit your profile
- ➕ **New Listing** - List tools or crops
- 🛍️ **View Listings** - Browse marketplace
- 📅 **Calendar** - Plan with AI assistance
- 🌤️ **Weather** - 7-day forecasts
- 💰 **Market Prices** - Current crop prices

### For Admin:
- All farmer features PLUS:
- 👥 **Manage Farmers** - View all profiles
- 🗄️ **Database Check** - Inspect database

---

## 🔧 Troubleshooting

**Problem:** Password error on login  
**Solution:** Run `python migrate_password_column.py`

**Problem:** Can't see login page  
**Solution:** Make sure you're not already logged in. Click logout in sidebar if needed.

**Problem:** Registration fails  
**Solution:** Name might already exist. Try a different name.

---

## 💡 Tips

1. **First-Time Users:** Don't skip the welcome tutorial!
2. **Password:** Choose something memorable (min 4 chars)
3. **Location:** Be specific for accurate weather (e.g., "Wadgaon Sheri, Pune")
4. **Weather Setup:** Coordinates are auto-fetched, may take a few seconds
5. **Logout:** Click "🚪 Logout" button in left sidebar

---

## 📱 What's Different Now?

### Before Phase 1:
- ❌ Login hidden in sidebar
- ❌ Manual profile creation (admin only)
- ❌ No clear onboarding
- ❌ No welcome screen

### After Phase 1:
- ✅ Login is the FIRST screen
- ✅ Self-service registration
- ✅ Step-by-step wizard
- ✅ Welcome tutorial
- ✅ Professional design

---

## 🎉 That's It!

You're ready to use the new and improved Smart Farmer Marketplace!

**Questions?** Check `PHASE1_IMPLEMENTATION.md` for detailed documentation.

**Next Steps:** Explore the features and provide feedback for Phase 2 improvements!
