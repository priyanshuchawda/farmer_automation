# Weekly Calendar View - Feature Documentation

## Overview
Added a new **Weekly View** to the Smart Farming Calendar, allowing farmers to see a full week at a glance with all scheduled farming activities.

## Files Created

### 1. `calender/week_view.py`
New component that renders the weekly calendar view.

**Key Features:**
- Displays 7 days (Monday to Sunday) in a grid layout
- Shows week range with navigation (Previous Week / Next Week)
- Each day card includes:
  - Day name, date, and month
  - All events for that day with times
  - Visual indicators (yellow for today, green for days with events)
  - "Add Event" button for quick event creation
  - Uniform card height (400px) with scrollable event list

**Functions:**
- `get_week_dates(year, month, day)` - Calculates the 7 days of the week containing the given date
- `render_week_view(year, month, day, events, lang)` - Renders the complete week view

## Files Modified

### 1. `components/calendar_integration.py`

**Changes:**
- Added import for `week_view` module
- Updated view switcher to cycle through three views: Month → Week → Day
- Modified button styling to show current view (📅 Month / 📆 Week / 📋 Day)
- Added rendering logic for week view
- Button now cycles through views on each click

**View Cycle:**
```
Month View → Week View → Day View → Month View (repeats)
```

### 2. `calender/day_view.py`

**Changes:**
- Added "📆 Week" button to navigation bar
- Reorganized navigation: "← Prev Day" | "📆 Week" | Date Header | "Next Day →"
- Clicking "📆 Week" button switches to week view
- Maintains current date context when switching views

## Visual Design

### Week View Layout
```
┌─────────────────────────────────────────────────────────┐
│  ← Previous Week  │  Week: 3-9 Jan 2024  │  Next Week → │
├────────┬────────┬────────┬────────┬────────┬────────┬───┤
│  Mon   │  Tue   │  Wed   │  Thu   │  Fri   │  Sat   │Sun│
│   3    │   4    │   5    │   6    │   7    │   8    │ 9 │
│  Jan   │  Jan   │  Jan   │  Jan   │  Jan   │  Jan   │Jan│
├────────┼────────┼────────┼────────┼────────┼────────┼───┤
│        │        │        │🟨TODAY│        │        │   │
│ Events │ Events │ Events │ Events │ Events │ Events │Eve│
│        │        │        │        │        │        │   │
│ 🕐 9:00│        │ 🕐10:00│ 🕐 8:00│        │        │   │
│📝Event1│        │📝Event2│📝Event3│        │        │   │
│        │        │        │        │        │        │   │
│➕ Add  │➕ Add  │➕ Add  │➕ Add  │➕ Add  │➕ Add  │➕  │
└────────┴────────┴────────┴────────┴────────┴────────┴───┘
```

### Color Coding
- **Yellow Background (#FFEB3B)**: Current day (today)
- **Light Green (#E8F5E9)**: Days with scheduled events
- **White (#FFFFFF)**: Days without events
- **Border Colors**: 
  - Orange (#F57C00) for today
  - Green (#4CAF50) for days with events
  - Gray (#BDBDBD) for empty days

## User Interactions

### Navigation
1. **Previous Week**: Shows the previous 7 days
2. **Next Week**: Shows the next 7 days
3. **View Toggle Button**: Cycles between Month/Week/Day views (green button in center)

### Event Management
1. **Click Event**: Opens event details for editing/viewing
2. **Add Event Button**: Quick add event for specific day (switches to day view)
3. **Event Display**: Shows time (🕐) and title (📝) for each event

### View Switching
- **From Month View**: Click green button → goes to Week View
- **From Week View**: Click green button → goes to Day View
- **From Day View**: Click green button → goes back to Month View
- **From Day View**: Click "📆 Week" button → goes to Week View

## Responsive Features

1. **Event Overflow**: If a day has many events, the card becomes scrollable
2. **Title Truncation**: Long event titles are truncated to 25 characters with "..."
3. **Hover Tooltips**: Full event details shown on hover
4. **Multi-language Support**: Day names, months, and numbers localized (English, Hindi, Marathi)

## Integration with Existing Features

### Weather Alerts
- Week view displays events with weather alerts
- Weather alert icon and text visible in event buttons
- Color-coded based on alert severity

### AI-Generated Plans
- Multi-day AI plans visible across the week
- Easy to see weekly farming schedule at a glance
- Quick navigation between days

### Event Editing
- Click any event to open details panel
- Edit, delete, or view full information
- Changes immediately reflected in week view

## Technical Implementation

### State Management
Uses Streamlit session state:
- `st.session_state.calendar_view`: Stores current view ("month", "week", or "day")
- `st.session_state.current_year`: Current year
- `st.session_state.current_month`: Current month
- `st.session_state.current_day`: Current day

### Week Calculation
- Week starts on Monday (ISO 8601 standard)
- Automatically handles month boundaries
- Correctly displays weeks that span multiple months

### Event Sorting
- Events sorted by time within each day
- Earliest events shown first
- 24-hour time format (HH:MM)

## Usage Examples

### Farmer Workflow
1. **View Weekly Schedule**: Farmer opens Calendar → clicks view button to switch to Week View
2. **Check Today's Tasks**: Today is highlighted in yellow
3. **Plan Ahead**: See entire week of activities in one view
4. **Add Quick Event**: Click "➕ Add Event" on any day
5. **Navigate**: Use Previous/Next Week buttons to move through calendar

### Multi-Week Planning
1. Start in Week View
2. Navigate through multiple weeks to plan seasonal activities
3. Add events to specific days
4. Review weekly workload distribution

## Accessibility Features

- Clear visual hierarchy
- High contrast colors for better readability
- Large, clickable buttons
- Tooltip hints for all interactive elements
- Support for 3 languages (en, hi, mr)

## Future Enhancements (Suggestions)

1. **Week Summary Statistics**: Show total hours, event types breakdown
2. **Drag & Drop**: Move events between days
3. **Week Templates**: Save and apply weekly patterns
4. **Print View**: Printer-friendly weekly schedule
5. **Export**: Download week as PDF or image
6. **Recurring Events**: Mark events that repeat weekly

## Benefits for Farmers

1. **Better Planning**: See entire week of farming activities
2. **Time Management**: Visual representation of workload distribution
3. **Quick Navigation**: Easy movement between days and weeks
4. **Context Awareness**: Today highlighted, events color-coded
5. **Efficient Scheduling**: Add events directly from week view
6. **Weather Integration**: Week-ahead weather planning

## Summary

The Weekly View provides a perfect middle ground between the high-level Month View and the detailed Day View, giving farmers a practical 7-day planning horizon that aligns with typical farming work cycles.
