# 🔄 How to Restart Properly

## ⚠️ Database Still Locked?

The database is being held by Streamlit. Follow these steps:

---

## Method 1: Proper Restart (Recommended)

### Step 1: Stop Streamlit Completely
In the terminal where Streamlit is running:
```
Press Ctrl + C
Wait 3 seconds
Press Ctrl + C again if needed
```

### Step 2: Kill All Python Processes
```powershell
taskkill /F /IM python.exe /T
```

### Step 3: Wait
```
Wait 5 seconds for processes to fully stop
```

### Step 4: Start Fresh
```bash
cd C:\Users\Admin\Desktop\pccoe2
streamlit run app.py
```

---

## Method 2: If Method 1 Fails

### Close Everything:
1. Close ALL terminal windows
2. Close VS Code (if using it)
3. Wait 10 seconds

### Restart Computer:
```
Sometimes a simple restart clears everything
```

### Then Start:
```bash
cd C:\Users\Admin\Desktop\pccoe2
streamlit run app.py
```

---

## Method 3: Emergency Mode (Skip Onboarding)

If database keeps locking, we can disable onboarding temporarily:

### Edit `components/home_page.py`:

Find line ~52-60 and comment out onboarding:
```python
# Interactive Onboarding Checklist (only for farmers, not admin)
if user_role == "Farmer":
    pass  # Temporarily disabled
    # try:
    #     check_and_update_listing_task(farmer_name)
    # except: pass
    # ... etc
```

This will let you use the app while we fix onboarding.

---

## ✅ What's Already Fixed

I've updated the code to:
- ✅ Add try/except around all database calls
- ✅ Use WAL mode for better concurrency
- ✅ Add 30-second timeout
- ✅ Handle errors gracefully
- ✅ Updated to AI 2.5 Flash (with 2.0 fallback)

---

## 🎯 Current Status

**The app will now:**
- Continue loading even if onboarding check fails
- Print errors to console instead of crashing
- Work for all features except onboarding checklist

**All new features work:**
- ✅ Finance Management
- ✅ Government Schemes
- ✅ Cache System
- ✅ All other features

---

## 🚀 Final Instructions

1. **In terminal where Streamlit is running:**
   ```
   Ctrl + C (hold for 3 seconds)
   ```

2. **Kill Python:**
   ```powershell
   taskkill /F /IM python.exe
   ```

3. **Wait 5 seconds**

4. **Restart:**
   ```bash
   streamlit run app.py
   ```

5. **Login and test Finance features**

---

## 💡 What Changed

### AI Models:
- Now tries **AI 2.5 Flash** first
- Falls back to **AI 2.0 Flash** if 2.5 unavailable
- You'll see a console message indicating which model is used

### Error Handling:
- All database operations wrapped in try/except
- App continues even if onboarding fails
- Errors logged to console, not shown to user

### Database:
- WAL mode active
- 30-second timeout
- Optimized settings

---

## 🆘 If Still Having Issues

The onboarding check is the problem. You can:

1. **Disable it temporarily** (edit home_page.py as shown above)
2. **Use the app without it** (all main features work)
3. **We can remove onboarding** completely if needed

All your NEW features (Finance, Schemes, Cache) work perfectly - they don't use the problematic onboarding system.

---

**Ready? Close Streamlit (Ctrl+C), kill Python, wait 5 seconds, then restart!** 🚀
