# Calendar Features - Quick Start Guide

## 🎯 New Features Overview

### 1. **View Switcher** (Month/Day Toggle)
Located at the top of the calendar, switch between:
- **Month View**: See all events for the month at a glance
- **Day View**: Focus on a specific day's schedule with detailed time-based layout

### 2. **AI Plan Editor**
When generating farming plans, you can now:
- Edit the **date** for each activity (📅 Date Picker)
- Edit the **time** for each activity (🕐 Time Picker)
- Review and adjust before saving to calendar

### 3. **Event Editor**
Click any event to view details, then:
- Click **✏️ Edit** to modify event details
- Change date, time, title, or description
- Refresh weather forecast for new dates
- Save changes or cancel

---

## 📖 How to Use

### Switching Views

```
1. Go to Calendar menu
2. Look for "Calendar View" toggle at top
3. Click "Month" or "Day" to switch views
```

**In Month View:**
- Click on any day number to jump to Day View for that date
- Click on event cards to see details

**In Day View:**
- Use ← Previous Day / Next Day → buttons to navigate
- Events are shown in chronological order with times

---

### Creating AI Farming Plans

```
1. Click "🤖 AI Farming Plan Generator" 
2. Type your request (e.g., "Create a 5-day tomato planting schedule")
3. Click "🌱 Generate"
4. EDIT DATES AND TIMES for each step:
   - Click date pickers to choose dates
   - Click time pickers to set times
5. Click "📅 Add All to Calendar with Weather Alerts"
```

**Example Prompts:**
- "Create a 10-day wheat planting schedule for November"
- "Generate a fertilization plan for my rice crop"
- "Plan irrigation schedule for next 7 days"

---

### Editing Existing Events

```
1. Click on any event in the calendar
2. Event details will appear below
3. Click "✏️ Edit" button
4. Modify any field:
   - 📅 Date
   - 🕐 Time
   - Title
   - Description
5. (Optional) Click "🔄 Refresh Weather Forecast"
6. Click "💾 Save Changes"
```

---

## 🎨 Visual Guide

### Month View Layout
```
┌─────────────────────────────────────┐
│     ← October 2025 →                │
├──────┬──────┬──────┬──────┬────────┤
│ Sun  │ Mon  │ Tue  │ Wed  │ Thu    │
├──────┼──────┼──────┼──────┼────────┤
│  1   │  2   │  3   │  4   │  5     │
│      │      │      │[📝]  │        │
│      │      │      │Event │        │
└──────┴──────┴──────┴──────┴────────┘
      ↑ Click day → Switch to Day View
      ↑ Click event → View details
```

### Day View Layout
```
┌─────────────────────────────────────┐
│  ← Wednesday, 4 October 2025 →      │
├─────────────────────────────────────┤
│ 🕐 09:00 - Prepare soil             │
│   Description: Till and level...    │
│   🌦️ Good weather for farming      │
├─────────────────────────────────────┤
│ 🕐 14:00 - Plant seeds              │
│   Description: Plant wheat seeds... │
│   🌦️ Light rain expected            │
└─────────────────────────────────────┘
```

### AI Plan Editor
```
┌─────────────────────────────────────┐
│ 📋 Wheat Planting Schedule          │
│ ✏️ Edit dates and times before save│
├─────────────────────────────────────┤
│ ▼ 1. Prepare soil                   │
│   Description: ...                  │
│   📅 Date: [2025-11-08]            │
│   🕐 Time: [09:00]                 │
├─────────────────────────────────────┤
│ ▼ 2. Plant seeds                    │
│   Description: ...                  │
│   📅 Date: [2025-11-09]            │
│   🕐 Time: [10:00]                 │
└─────────────────────────────────────┘
│ [📅 Add All to Calendar] [❌ Cancel]│
```

---

## 💡 Pro Tips

1. **Quick Day Access**: In Month View, click any date to jump to Day View
2. **Batch Edit**: Edit all AI-generated dates/times before saving
3. **Weather Updates**: After changing event dates, refresh weather forecast
4. **Time Format**: Use 24-hour format (e.g., 14:00 for 2 PM)
5. **Navigation**: Use Previous/Next buttons in Day View for quick browsing

---

## 🔧 Technical Notes

- All times are stored in 24-hour format (HH:MM)
- Default event time is 09:00 if not specified
- Weather forecasts update automatically for selected dates
- Events are sorted chronologically in Day View
- Database automatically saves all changes

---

## ❓ FAQ

**Q: Can I change the date of an AI-generated event?**
A: Yes! Edit the date picker before clicking "Add All to Calendar"

**Q: How do I edit an existing event's time?**
A: Click the event → Click "✏️ Edit" → Change time → Click "💾 Save"

**Q: Can I switch between views while viewing an event?**
A: Yes, the view switcher is always accessible at the top

**Q: What happens if I cancel editing?**
A: All changes are discarded and the event remains unchanged

**Q: Will weather alerts update when I change the date?**
A: Click "🔄 Refresh Weather Forecast" after changing dates

---

## 📞 Support

For issues or questions, refer to:
- `CALENDAR_ENHANCEMENTS.md` - Technical implementation details
- `README.md` - General application documentation
- `INTEGRATION_SUMMARY.md` - System integration overview
