# 🧪 QUICK TESTING GUIDE

## Test all climate features in 10 minutes!

---

## ✅ **FEATURE 1: Climate Risk Dashboard**

**Steps:**
1. Login → Sidebar → "🌍 CLIMATE & SUSTAINABILITY"
2. Click "🌡️ Climate Risk Dashboard"
3. Wait 5-10 seconds

**Expected:**
- Big colored risk score (e.g., 68/100 🟡 MODERATE)
- Three tabs: Drought, Flood, Heat
- Drought tab shows specific AI actions
- Checkboxes to mark actions completed

**Success:** ✅ If you see AI-generated actions (not "Coming soon")

---

## ✅ **FEATURE 2: Home Page Alert**

**Steps:**
1. Go to "🏠 Home" page
2. Look at top section

**Expected:**
- If climate risk ≥ 60: Orange/red alert banner appears
- Shows "HIGH RISK" or "CRITICAL RISK"
- Two buttons: "View Full Climate Analysis" and "Get Climate-Smart Crops"

**Success:** ✅ Banner appears (if risk is high)
**Note:** If risk is LOW (<60), banner won't show - that's correct!

---

## ✅ **FEATURE 3: Climate-Smart Crop Selector**

**Steps:**
1. Sidebar → "🌡️ Climate-Smart Crops"
2. Select season: "Rabi (Winter: Nov-Mar)"
3. Click "🤖 Get AI Crop Recommendations"
4. Wait 10-15 seconds

**Expected:**
- 3-5 crops recommended
- Each crop shows:
  - Drought tolerance (0-10)
  - Heat tolerance (0-10)
  - Water requirement
  - Expected profit
  - 3-5 reasons why recommended
- "Crops to Avoid" section at bottom
- "Adopt [Crop]" buttons

**Success:** ✅ If you see detailed crop cards with AI reasons

---

## ✅ **FEATURE 4: Water & Carbon Tracker**

**Steps:**
1. Sidebar → "💧 Water & Carbon Tracker"
2. Fill form:
   - Crop: Wheat
   - Farm area: 2 acres
   - Season: Rabi
   - Irrigation: Flood/Traditional
   - Water source: Borewell
   - Irrigation hours: 20/week
   - Fertilizer: Chemical
   - Energy: Diesel
   - Diesel usage: 50 liters/month
3. Click "🔍 Analyze Sustainability"
4. Wait 5-10 seconds

**Expected:**
- Two scores: Water Efficiency + Carbon Efficiency (0-100)
- Three metrics: Water savings, Carbon reduction, Cost savings
- 3-5 AI recommendations
- Current practices summary

**Success:** ✅ If you see both scores and specific recommendations

---

## 🐛 **COMMON ISSUES & FIXES**

### **Issue:** "Please update profile with location"
**Fix:** Go to "👤 My Profile" → Add latitude/longitude

### **Issue:** Takes too long (>30 seconds)
**Fix:** Network issue, but should eventually return results

### **Issue:** Generic actions like "Monitor crops"
**Fix:** That's fallback mode - API key might be missing

### **Issue:** Page shows "Coming soon"
**Fix:** App.py routing not updated - check if files exist

---

## 📸 **WHAT TO SCREENSHOT FOR DEMO**

1. Climate Risk Dashboard with HIGH drought score
2. AI-generated actions (specific, detailed)
3. Climate-Smart Crops with 3+ recommendations
4. Water & Carbon Tracker showing poor scores (more impressive before/after)
5. Home page alert banner (if shown)

---

## ⚡ **QUICK TEST (2 MIN)**

Just run this to verify everything works:

1. Login ✅
2. Home → See any alert? ✅
3. Climate Dashboard → See score? ✅
4. Smart Crops → Click "Get Recommendations" ✅
5. Tracker → Fill form → Analyze ✅

**If all 5 work → READY FOR DEMO! 🎉**

---

## 🚀 **DEMO TIPS**

**Good Demo Flow:**
1. Start with Home (show alert)
2. Click to Climate Dashboard
3. Explain AI analysis happening
4. Show drought score + actions
5. Go to Smart Crops
6. Show crop recommendations
7. Mention sustainability tracker
8. End with impact potential

**Time:** 3-5 minutes total

---

**Run `streamlit run app.py` and test now!**
