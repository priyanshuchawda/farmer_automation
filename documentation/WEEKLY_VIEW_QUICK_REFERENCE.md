# Weekly Calendar View - Quick Reference

## View Toggle Button (Green Button)
**Location**: Center of screen, above calendar navigation

**Cycle Pattern**:
- Click once: Month View → Week View
- Click twice: Week View → Day View  
- Click thrice: Day View → Month View

**Button Labels**:
- 📅 Month (shows current view)
- 📆 Week (shows current view)
- 📋 Day (shows current view)

## Week View Controls

### Navigation Bar
```
[← Previous Week]  [Week: Date Range]  [Next Week →]
```

### Day Cards (7 columns)
Each card shows:
- Day name (Mon, Tue, Wed, etc.)
- Date number
- Month abbreviation
- Events with times
- "➕ Add Event" button

### Color Indicators
🟨 **Yellow**: Today's date
🟩 **Light Green**: Days with events
⬜ **White**: Empty days

## Keyboard Workflow

1. **Open Calendar**: Navigate to Calendar menu
2. **Switch to Week**: Click green view button once
3. **Navigate Weeks**: Use Previous/Next Week buttons
4. **View Event**: Click on any event in a day card
5. **Add Event**: Click "➕ Add Event" on desired day
6. **Change View**: Click green button to cycle views

## Week View Features

✓ See 7 days at once (Monday-Sunday)
✓ All events with times visible
✓ Scroll if multiple events per day
✓ Today highlighted in yellow
✓ Quick event creation per day
✓ Week range displayed in header
✓ Multi-language support
✓ Weather alerts shown in events

## Tips

- **Planning**: Week view is best for weekly task planning
- **Today**: Look for yellow highlighted day
- **Busy Days**: Green indicates days with scheduled work
- **Quick Add**: Click "➕ Add Event" for fast scheduling
- **Details**: Click any event to see full information
- **Navigation**: Week buttons move 7 days forward/backward

## Common Actions

| Action | How To |
|--------|--------|
| View next week | Click "Next Week →" |
| View last week | Click "← Previous Week" |
| See event details | Click on event button |
| Add new event | Click "➕ Add Event" on day |
| Switch to day view | Click green button twice |
| Switch to month view | Click green button (from day) |
| Go to day from week | Click "➕ Add Event" switches to day view |

## Files Modified
- ✓ `calender/week_view.py` (NEW)
- ✓ `components/calendar_integration.py`
- ✓ `calender/day_view.py`

## Integration Points
- Works with AI-generated plans
- Shows weather alerts
- Supports event editing/deletion
- Multi-language (English, Hindi, Marathi)
- Farmer profile integration
