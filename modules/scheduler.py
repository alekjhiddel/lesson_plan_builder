"""
Scheduler Module
Handles time-of-year awareness, seasonal themes, and scheduling constraints.
"""

from datetime import datetime, date


# Monthly themes mapping
MONTHLY_THEMES = {
    1: {
        'month': 'January',
        'themes': ['Snowmen', 'Winter Wonderland', 'New Year / New Beginnings', 'Arctic Animals'],
        'colors': ['white', 'light blue', 'silver'],
        'activities': ['snowflake crafts', 'winter sensory bins', 'hot cocoa math', 'mitten matching']
    },
    2: {
        'month': 'February',
        'themes': ["Valentine's Day", 'Kindness', 'Friendship', 'Dental Health'],
        'colors': ['red', 'pink', 'white'],
        'activities': ['heart crafts', 'friendship bracelets', 'kindness chain', 'sorting hearts by size']
    },
    3: {
        'month': 'March',
        'themes': ['Dr. Seuss', "St. Patrick's Day", 'Weather', 'Lions and Lambs'],
        'colors': ['green', 'gold', 'rainbow'],
        'activities': ['green sensory play', 'rainbow sorting', 'weather chart', 'rhyming activities']
    },
    4: {
        'month': 'April',
        'themes': ['Spring', 'Easter', 'Rain & Rainbows', 'Growing Things', 'Earth Day'],
        'colors': ['pastel green', 'yellow', 'pastel blue', 'pink'],
        'activities': ['planting seeds', 'rain painting', 'egg hunts (adaptive)', 'butterfly life cycle']
    },
    5: {
        'month': 'May',
        'themes': ['Flowers', 'End of Year', 'Bugs & Insects', "Mother's Day", 'Gardens'],
        'colors': ['bright green', 'yellow', 'pink', 'purple'],
        'activities': ['flower crafts', 'memory books', 'butterfly release', 'garden sensory bin']
    },
    6: {
        'month': 'June',
        'themes': ['Summer', 'Ocean', 'End of Year Celebration', 'Travel'],
        'colors': ['blue', 'yellow', 'orange'],
        'activities': ['water play', 'ocean sensory', 'summer countdown', 'yearbook signing']
    },
    7: {
        'month': 'July',
        'themes': ['Summer Fun', 'Red White & Blue', 'Ice Cream', 'Beach'],
        'colors': ['red', 'white', 'blue'],
        'activities': ['water tables', 'ice cream craft', 'patriotic sensory', 'beach in classroom']
    },
    8: {
        'month': 'August',
        'themes': ['Back to School Prep', 'Summer Wrap-up', 'Community Helpers', 'All About Me'],
        'colors': ['yellow', 'orange', 'blue'],
        'activities': ['social stories about school', 'schedule practice', 'name recognition', 'self-portraits']
    },
    9: {
        'month': 'September',
        'themes': ['Back to School', 'Apples', 'All About Me', 'Classroom Community', 'Fall'],
        'colors': ['red', 'green', 'brown', 'yellow'],
        'activities': ['apple tasting', 'name crafts', 'routine practice', 'leaf collecting', 'apple stamping']
    },
    10: {
        'month': 'October',
        'themes': ['Halloween', 'Fall Harvest', 'Pumpkins', 'Bats & Spiders (friendly)'],
        'colors': ['orange', 'black', 'purple', 'brown'],
        'activities': ['pumpkin decorating', 'costume parade', 'fall sensory bins', 'spooky slime', 'leaf rubbings']
    },
    11: {
        'month': 'November',
        'themes': ['Thanksgiving', 'Gratitude', 'Family', 'Food', 'Native American Heritage'],
        'colors': ['brown', 'orange', 'gold', 'red'],
        'activities': ['thankful tree', 'turkey crafts', 'feast preparation', 'family collage', 'food tasting']
    },
    12: {
        'month': 'December',
        'themes': ['Christmas', 'Winter Holidays', 'Giving', 'Gingerbread', 'Snow'],
        'colors': ['red', 'green', 'gold', 'white'],
        'activities': ['ornament making', 'gift wrapping practice', 'gingerbread house', 'holiday sensory', 'winter songs']
    }
}

# Time blocks for MSD classroom
DAILY_SCHEDULE_TEMPLATE = {
    'arrival': {'time': '8:00-8:20', 'duration': 20, 'type': 'transition', 'description': 'Arrival, backpack routine, morning greeting'},
    'morning_meeting': {'time': '8:20-8:40', 'duration': 20, 'type': 'whole_group', 'description': 'Calendar, weather, hello song, schedule review'},
    'centers_block_1': {'time': '8:40-9:40', 'duration': 60, 'type': 'centers', 'description': '3 center rotations × 20 min (or 4 × 15 min)'},
    'snack': {'time': '9:40-10:00', 'duration': 20, 'type': 'daily_living', 'description': 'Snack time with embedded skills'},
    'specials_or_recess': {'time': '10:00-10:30', 'duration': 30, 'type': 'transition', 'description': 'PE/Music/Art or adapted recess'},
    'individual_work': {'time': '10:30-11:15', 'duration': 45, 'type': '1:1', 'description': '1:1 aide time, individual IEP work'},
    'lunch': {'time': '11:15-11:45', 'duration': 30, 'type': 'daily_living', 'description': 'Lunch with embedded self-help skills'},
    'rest_sensory': {'time': '11:45-12:05', 'duration': 20, 'type': 'sensory', 'description': 'Rest time / sensory break / calming activities'},
    'centers_block_2': {'time': '12:05-1:05', 'duration': 60, 'type': 'centers', 'description': '3 center rotations × 20 min'},
    'story_group': {'time': '1:05-1:25', 'duration': 20, 'type': 'whole_group', 'description': 'Read-aloud, interactive story, comprehension'},
    'individual_work_2': {'time': '1:25-2:05', 'duration': 40, 'type': '1:1', 'description': '1:1 aide time, individual IEP work'},
    'closing_circle': {'time': '2:05-2:20', 'duration': 15, 'type': 'whole_group', 'description': 'Closing song, review day, goodbye routine'},
    'dismissal': {'time': '2:20-2:35', 'duration': 15, 'type': 'transition', 'description': 'Pack up, backpack routine, dismissal'}
}

# Center types for MSD classroom
CENTER_TYPES = [
    'Fine Motor / Art',
    'Sensory / Science',
    'Academic / Table Work',
    'Life Skills / Dramatic Play',
    'Technology / Cause-Effect',
    'Communication / Literacy',
    'Math / Manipulatives',
    'Gross Motor / Movement'
]


def get_current_themes():
    """Get themes for the current month."""
    month = datetime.now().month
    return MONTHLY_THEMES.get(month, MONTHLY_THEMES[9])


def get_themes_for_month(month):
    """Get themes for a specific month (1-12)."""
    return MONTHLY_THEMES.get(month, MONTHLY_THEMES[9])


def get_week_of_month():
    """Get which week of the month we're in (1-5)."""
    today = date.today()
    first_day = today.replace(day=1)
    return (today.day - 1) // 7 + 1


def get_daily_schedule():
    """Get the daily schedule template."""
    return DAILY_SCHEDULE_TEMPLATE


def get_center_types():
    """Get available center activity types."""
    return CENTER_TYPES


def get_scheduling_context():
    """
    Build a context string about current time/themes for prompt generation.
    """
    now = datetime.now()
    themes = get_current_themes()
    week = get_week_of_month()
    
    context = f"""
CURRENT DATE CONTEXT:
- Month: {themes['month']} (Week {week})
- Suggested Themes: {', '.join(themes['themes'])}
- Theme Colors: {', '.join(themes['colors'])}
- Activity Ideas: {', '.join(themes['activities'])}

DAILY SCHEDULE STRUCTURE:
"""
    for block_name, block_info in DAILY_SCHEDULE_TEMPLATE.items():
        context += f"- {block_info['time']}: {block_info['description']} [{block_info['type']}]\n"
    
    context += f"""
CENTER ROTATION NOTES:
- 3 groups of 3 students rotating every 15-20 minutes
- Each center should have visual supports and multiple access points
- Centers should embed IEP goals across activities
- Available center types: {', '.join(CENTER_TYPES)}
"""
    
    return context
