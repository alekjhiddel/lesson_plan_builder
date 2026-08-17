"""
Visual Schedule Template Builder for SPARK
Allows teachers to build visual schedules for individual students or the whole class.
"""

import json
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
SCHEDULES_DIR = os.path.join(DATA_DIR, 'visual_schedules')


def ensure_schedules_dir():
    """Ensure the visual schedules directory exists."""
    os.makedirs(SCHEDULES_DIR, exist_ok=True)


# Default activity icons (text-based for accessibility)
ACTIVITY_ICONS = {
    "arrival": "🎒",
    "morning_meeting": "☀️",
    "circle_time": "⭕",
    "work_time": "✏️",
    "centers": "🎨",
    "reading": "📚",
    "math": "🔢",
    "snack": "🍎",
    "lunch": "🍽️",
    "recess": "🏃",
    "specials": "🎵",
    "sensory_break": "💆",
    "movement_break": "🤸",
    "bathroom": "🚽",
    "pack_up": "🎒",
    "dismissal": "👋",
    "free_choice": "⭐",
    "life_skills": "🏠",
    "cooking": "👨‍🍳",
    "community": "🚶",
    "social_skills": "🤝",
    "ot_pt": "💪",
    "speech": "💬",
    "transition": "➡️",
    "calm_corner": "🧘",
    "technology": "💻",
    "art": "🖼️",
    "music": "🎶",
    "outside": "🌳",
}

# Default class schedule template
DEFAULT_CLASS_SCHEDULE = [
    {"activity": "Arrival & Unpack", "icon": "arrival", "duration": 15, "transition_cue": "Bell rings"},
    {"activity": "Morning Meeting", "icon": "morning_meeting", "duration": 20, "transition_cue": "Timer + visual card"},
    {"activity": "Work Time 1", "icon": "work_time", "duration": 30, "transition_cue": "Cleanup song"},
    {"activity": "Sensory Break", "icon": "sensory_break", "duration": 10, "transition_cue": "Break card shown"},
    {"activity": "Small Groups / Centers", "icon": "centers", "duration": 30, "transition_cue": "Timer + bell"},
    {"activity": "Snack", "icon": "snack", "duration": 15, "transition_cue": "Wash hands visual"},
    {"activity": "Specials (PE/Music/Art)", "icon": "specials", "duration": 30, "transition_cue": "Line up visual"},
    {"activity": "Life Skills", "icon": "life_skills", "duration": 30, "transition_cue": "Timer"},
    {"activity": "Lunch", "icon": "lunch", "duration": 30, "transition_cue": "Lunch visual card"},
    {"activity": "Movement Break", "icon": "movement_break", "duration": 10, "transition_cue": "Movement cards"},
    {"activity": "Work Time 2", "icon": "work_time", "duration": 30, "transition_cue": "Timer + visual"},
    {"activity": "Free Choice / Reinforcement", "icon": "free_choice", "duration": 15, "transition_cue": "Choice board"},
    {"activity": "Pack Up & Dismissal", "icon": "pack_up", "duration": 15, "transition_cue": "Dismissal song"},
]


def get_saved_schedules():
    """Get all saved visual schedule templates."""
    ensure_schedules_dir()
    schedules = []
    for filename in sorted(os.listdir(SCHEDULES_DIR)):
        if filename.endswith('.json'):
            filepath = os.path.join(SCHEDULES_DIR, filename)
            with open(filepath, 'r') as f:
                data = json.load(f)
                data['filename'] = filename
                schedules.append(data)
    return schedules


def get_schedule(filename):
    """Get a specific saved schedule."""
    filepath = os.path.join(SCHEDULES_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return None


def save_schedule(name, activities, schedule_type="class", student_id=None):
    """Save a visual schedule template.
    
    Args:
        name: Schedule name (e.g., "Monday Class Schedule" or "Child 1 Individual")
        activities: List of activity dicts
        schedule_type: "class" or "individual"
        student_id: Optional student ID for individual schedules
    
    Returns:
        filename of saved schedule
    """
    ensure_schedules_dir()
    
    schedule_data = {
        "name": name,
        "type": schedule_type,
        "student_id": student_id,
        "created": datetime.now().strftime("%Y-%m-%d"),
        "activities": activities,
    }
    
    # Generate filename
    safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in name)
    safe_name = safe_name.strip().replace(' ', '_')
    filename = f"{safe_name}_{datetime.now().strftime('%Y%m%d')}.json"
    
    filepath = os.path.join(SCHEDULES_DIR, filename)
    with open(filepath, 'w') as f:
        json.dump(schedule_data, f, indent=2)
    
    return filename


def delete_schedule(filename):
    """Delete a saved schedule."""
    filepath = os.path.join(SCHEDULES_DIR, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False


def get_default_schedule():
    """Return the default class schedule template."""
    return DEFAULT_CLASS_SCHEDULE


def get_available_icons():
    """Return all available activity icons."""
    return ACTIVITY_ICONS


def format_schedule_for_print(schedule_data):
    """Format a visual schedule for printing (text + icons).
    
    Returns a list of formatted activity strings.
    """
    formatted = []
    for activity in schedule_data.get("activities", []):
        icon_key = activity.get("icon", "transition")
        icon = ACTIVITY_ICONS.get(icon_key, "▶️")
        name = activity.get("activity", "Activity")
        duration = activity.get("duration", "")
        transition = activity.get("transition_cue", "")
        
        entry = {
            "icon": icon,
            "name": name,
            "duration": f"{duration} min" if duration else "",
            "transition": transition,
            "display": f"{icon}  {name}" + (f" ({duration} min)" if duration else ""),
        }
        formatted.append(entry)
    
    return formatted
