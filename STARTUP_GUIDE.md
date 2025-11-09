# 🚀 Quick Start Guide - New Features

## What's New? 

We've added **5 major features** for farmers:

1. ✅ **Government Schemes** - Access subsidies and schemes
2. ✅ **Farm Finance Management** - Track expenses, income, loans
3. ✅ **AI Chatbot Assistant** - Get instant farming advice
4. ✅ **Notifications & Alerts** - Stay updated with price and weather alerts
5. ✅ **GPS Location Verification** - Verify location with GPS + AI

---

## 🏃 Quick Setup (5 minutes)

### Step 1: Start the Application
```bash
streamlit run app.py
```

### Step 2: Login as Farmer
- Username: Any existing farmer name
- Password: farmer123 (default)

### Step 3: Explore New Features

#### Try the AI Chatbot:
1. Go to **Assistance → AI Chatbot**
2. Ask: "What crops are best for my region?"
3. Try the quick question buttons

#### Set a Price Alert:
1. Go to **Assistance → Notifications & Alerts**
2. Click "Price Alerts" tab
3. Create an alert for your crop

#### Verify Your Location:
1. Go to **My Profile**
2. Expand "GPS + AI Location Verification"
3. Choose "Manual GPS Entry" (easiest)
4. Enter your coordinates
5. Or try "AI Only" with your city name

#### Check Government Schemes:
1. Go to **Government → Government Schemes**
2. Browse available schemes
3. Search or filter by category

#### Manage Finances:
1. Go to **Finance → Farm Finance Management**
2. Add a sample expense
3. View the dashboard

---

## ✅ Feature Checklist

After starting the app, verify these work:

- [ ] AI Chatbot responds to questions
- [ ] Can create price alerts
- [ ] Can view notifications
- [ ] Can access government schemes
- [ ] Can add expenses/income
- [ ] Can verify location (at least one method)

---

## 🐛 Common Issues

### Issue: AI Chatbot shows API error
**Solution:** Add `AI_API_KEY` to your `.env` file

### Issue: GPS browser method doesn't work
**Solution:** Use "Manual GPS Entry" method instead

### Issue: No notifications showing
**Solution:** Click "Add Sample Notifications" button to test

### Issue: Location unavailable error
**Solution:** Use "Manual Entry" or "AI Only" in profile

---

## 📊 Feature Overview

| Feature | Location | Status |
|---------|----------|--------|
| Government Schemes | Government Menu | ✅ Working |
| Farm Finance | Finance Menu | ✅ Working |
| AI Chatbot | Assistance Menu | ✅ Working (needs API key) |
| Notifications | Assistance Menu | ✅ Working |
| GPS Verification | My Profile | ✅ Working |

---

## 🎯 Test Scenarios

### Test 1: AI Chatbot
1. Open AI Chatbot
2. Click "Best crops for my region"
3. Verify response appears

### Test 2: Price Alert
1. Create alert for "Wheat" at ₹2000
2. Verify it appears in Active Alerts
3. Delete the alert

### Test 3: Location Verification
1. Open profile
2. Use "AI Only" method
3. Enter "Pune, Maharashtra"
4. Verify coordinates appear

### Test 4: Add Sample Data
1. Go to Notifications
2. Add sample notifications
3. Verify they appear
4. Mark one as read

### Test 5: Finance Tracking
1. Add expense: Seeds ₹5000
2. Add income: Wheat Sale ₹15000
3. View dashboard
4. Check summary

---

## 📱 Mobile Usage Tips

- GPS verification works better on mobile devices
- Use landscape mode for better dashboard view
- Price alerts are mobile-friendly
- AI Chatbot works great on mobile

---

## 🔧 Advanced Configuration

### Enable All Features:
1. Set `AI_API_KEY` in `.env`
2. Verify database permissions
3. Check internet connection for APIs

### Customize:
- Edit notification types in `notifications_page.py`
- Modify price alert logic
- Add more schemes in `government_schemes_page.py`
- Customize AI prompts in `ai_chatbot_page.py`

---

## 📞 Need Help?

1. Check **📖 How to Use** in the app
2. Read `NEW_FEATURES_SUMMARY.md` for details
3. Check console for error messages

---

## 🎉 You're Ready!

All features are now available to farmers. Explore and enjoy! 🌾

---

**Quick Links:**
- Main App: `streamlit run app.py`
- Features Doc: `NEW_FEATURES_SUMMARY.md`
- Database Viewer: `python db_viewer.py`

**Version:** 2.0  
**Date:** November 9, 2025
