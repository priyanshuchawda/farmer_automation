"""Utility functions for the Farming Calendar Assistant"""

def localize_number(num, lang):
    """Convert numbers to localized format based on language"""
    num_str = str(num)
    if lang == "hi" or lang == "mr":
        # Devanagari numerals
        devanagari_map = {
            '0': '०', '1': '१', '2': '२', '3': '३', '4': '४',
            '5': '५', '6': '६', '7': '७', '8': '८', '9': '९'
        }
        return ''.join(devanagari_map.get(c, c) for c in num_str)
    return num_str


def create_event_id(events):
    """Generate a unique event ID"""
    return str(len(events))


def format_date(date_str):
    """Format date string for display"""
    return date_str.split('T')[0]


def format_time(time_str):
    """Format time string for display"""
    return time_str.split('T')[1] if 'T' in time_str else time_str


def get_events_for_date(events, year, month, day):
    """Get all events for a specific date"""
    day_date = f"{year}-{month:02d}-{day:02d}"
    return [e for e in events if e["start"].startswith(day_date)]


def truncate_text(text, max_length=15):
    """Truncate text to max length with ellipsis"""
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text


def wrap_text(text, line_length=15):
    """Wrap text for better display in small spaces"""
    words = text.split()
    lines = []
    current_line = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) + 1 <= line_length:
            current_line.append(word)
            current_length += len(word) + 1
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
            current_length = len(word)
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return '\n'.join(lines) if len(lines) <= 2 else '\n'.join(lines[:2]) + "..."


