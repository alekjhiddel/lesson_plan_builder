"""
Compliance Calendar for SPARK
Tracks IEP regulatory deadlines based on 707 KAR 1:320 (Kentucky).
Provides teacher-adjustable dates for district-specific events.
"""

import json
import os
import uuid
from datetime import datetime, timedelta, date


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
COMPLIANCE_DIR = os.path.join(DATA_DIR, 'compliance')
EVENTS_FILE = os.path.join(COMPLIANCE_DIR, 'custom_events.json')
SETTINGS_FILE = os.path.join(COMPLIANCE_DIR, 'settings.json')


# ============================================================
# Kentucky Regulatory Deadlines (707 KAR 1:320)
# ============================================================

# Default grading period end dates (Kentucky typical school year)
DEFAULT_GRADING_PERIODS = [
    {"label": "Q1 Progress Report", "month": 10, "day": 15},
    {"label": "Q2 Progress Report", "month": 1, "day": 15},
    {"label": "Q3 Progress Report", "month": 3, "day": 15},
    {"label": "Q4 Progress Report", "month": 5, "day": 25},
]

# Regulatory constants
ANNUAL_REVIEW_MONTHS = 12       # IEP must be reviewed within 12 months
TRIENNIAL_YEARS = 3             # Re-evaluation every 3 years
ESY_DETERMINATION_MONTH = 3    # ESY eligibility by March 1st
ESY_DETERMINATION_DAY = 1
TRANSITION_AGE_KY = 14          # Transition planning starts at 14 in KY


def ensure_compliance_dir():
    """Ensure the compliance data directory exists."""
    os.makedirs(COMPLIANCE_DIR, exist_ok=True)


def get_compliance_settings():
    """Load compliance calendar settings (district-configurable)."""
    ensure_compliance_dir()
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    # Defaults
    return {
        "grading_periods": DEFAULT_GRADING_PERIODS,
        "school_year_start": {"month": 8, "day": 12},
        "school_year_end": {"month": 5, "day": 30},
        "warning_days_red": 0,       # 0 or fewer = overdue
        "warning_days_yellow": 14,   # within 14 days
        "warning_days_green": 60,    # more than 14 days out
    }


def save_compliance_settings(settings):
    """Save compliance calendar settings."""
    ensure_compliance_dir()
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=2)


def calculate_days_until(deadline_date):
    """Calculate days from today until a deadline.
    
    Args:
        deadline_date: date object or ISO string (YYYY-MM-DD)
    
    Returns:
        int: days until deadline (negative = overdue)
    """
    if isinstance(deadline_date, str):
        deadline_date = date.fromisoformat(deadline_date)
    elif isinstance(deadline_date, datetime):
        deadline_date = deadline_date.date()
    
    today = date.today()
    delta = deadline_date - today
    return delta.days


def _parse_date_field(date_str):
    """Parse a date string from student data. Returns date or None."""
    if not date_str:
        return None
    try:
        return date.fromisoformat(date_str)
    except (ValueError, TypeError):
        # Try other common formats
        for fmt in ("%m/%d/%Y", "%m-%d-%Y", "%Y/%m/%d"):
            try:
                return datetime.strptime(date_str, fmt).date()
            except (ValueError, TypeError):
                continue
    return None


def _get_annual_review_deadline(student):
    """Calculate annual IEP review deadline for a student.
    
    Per 707 KAR 1:320 Section 5: The IEP must be reviewed at least
    annually (within 12 months of the last review date).
    """
    review_date = _parse_date_field(student.get('iep_annual_review_date', ''))
    if not review_date:
        # If no review date set, check placement date
        placement_date = _parse_date_field(student.get('initial_placement_date', ''))
        if placement_date:
            review_date = placement_date
        else:
            return None
    
    # Next review = last review + 12 months
    try:
        next_review = review_date.replace(year=review_date.year + 1)
    except ValueError:
        # Feb 29 edge case
        next_review = review_date.replace(year=review_date.year + 1, day=28)
    
    return {
        "type": "annual_review",
        "label": "Annual IEP Review",
        "student_id": student.get('id', ''),
        "student_name": student.get('name', 'Unknown'),
        "deadline": next_review.isoformat(),
        "days_until": calculate_days_until(next_review),
        "regulation": "707 KAR 1:320 §5",
        "description": "IEP must be reviewed within 12 months of last review",
    }


def _get_triennial_deadline(student):
    """Calculate triennial re-evaluation deadline.
    
    Per IDEA/KAR: Re-evaluation must occur at least every 3 years
    unless parent and district agree it's unnecessary.
    """
    last_eval = _parse_date_field(student.get('last_evaluation_date', ''))
    if not last_eval:
        return None
    
    try:
        next_eval = last_eval.replace(year=last_eval.year + TRIENNIAL_YEARS)
    except ValueError:
        next_eval = last_eval.replace(year=last_eval.year + TRIENNIAL_YEARS, day=28)
    
    return {
        "type": "triennial_eval",
        "label": "Triennial Re-Evaluation",
        "student_id": student.get('id', ''),
        "student_name": student.get('name', 'Unknown'),
        "deadline": next_eval.isoformat(),
        "days_until": calculate_days_until(next_eval),
        "regulation": "707 KAR 1:340",
        "description": "Full re-evaluation required every 3 years",
    }


def _get_esy_deadline(student):
    """Calculate ESY (Extended School Year) eligibility determination deadline.
    
    Most KY districts require ESY determination by March 1st.
    """
    today = date.today()
    # ESY determination is typically for the upcoming summer
    year = today.year if today.month < ESY_DETERMINATION_MONTH else today.year + 1
    esy_date = date(year, ESY_DETERMINATION_MONTH, ESY_DETERMINATION_DAY)
    
    return {
        "type": "esy_determination",
        "label": "ESY Eligibility Determination",
        "student_id": student.get('id', ''),
        "student_name": student.get('name', 'Unknown'),
        "deadline": esy_date.isoformat(),
        "days_until": calculate_days_until(esy_date),
        "regulation": "707 KAR 1:320 §5(12)",
        "description": "Determine if student qualifies for Extended School Year services",
    }


def _get_transition_deadline(student):
    """Check if transition planning is due (age 14+ in Kentucky).
    
    Per KRS 158.6453 and 707 KAR 1:320: Transition planning must begin
    no later than the IEP in effect when the student turns 14.
    """
    age_str = student.get('age', '')
    try:
        age = int(age_str)
    except (ValueError, TypeError):
        return None
    
    if age >= TRANSITION_AGE_KY:
        # Check if transition plan exists
        has_transition = student.get('has_transition_plan', False)
        if not has_transition:
            return {
                "type": "transition_planning",
                "label": "Transition Plan Required",
                "student_id": student.get('id', ''),
                "student_name": student.get('name', 'Unknown'),
                "deadline": date.today().isoformat(),  # Already due
                "days_until": 0,
                "regulation": "707 KAR 1:320 §5(9)",
                "description": f"Student is {age} — transition planning must be in IEP",
            }
    return None


def _get_progress_report_deadlines(student, settings):
    """Generate progress report deadlines for each grading period."""
    today = date.today()
    deadlines = []
    
    for period in settings.get('grading_periods', DEFAULT_GRADING_PERIODS):
        month = period['month']
        day = period['day']
        
        # Determine the right year
        report_date = date(today.year, month, day)
        if report_date < today - timedelta(days=30):
            # Already well past — use next year
            report_date = date(today.year + 1, month, day)
        
        deadlines.append({
            "type": "progress_report",
            "label": period['label'],
            "student_id": student.get('id', ''),
            "student_name": student.get('name', 'Unknown'),
            "deadline": report_date.isoformat(),
            "days_until": calculate_days_until(report_date),
            "regulation": "707 KAR 1:320 §5(3)",
            "description": "Progress toward IEP goals must be reported each grading period",
        })
    
    return deadlines


def get_calendar_events(students_data):
    """Compute all upcoming regulatory deadlines for all students.
    
    Args:
        students_data: list of student dicts from student_manager
    
    Returns:
        list of deadline event dicts, sorted by date
    """
    settings = get_compliance_settings()
    events = []
    
    for student in students_data:
        # Annual IEP Review
        annual = _get_annual_review_deadline(student)
        if annual:
            events.append(annual)
        
        # Triennial Re-Evaluation
        triennial = _get_triennial_deadline(student)
        if triennial:
            events.append(triennial)
        
        # ESY Determination
        esy = _get_esy_deadline(student)
        if esy:
            events.append(esy)
        
        # Transition Planning
        transition = _get_transition_deadline(student)
        if transition:
            events.append(transition)
        
        # Progress Reports
        progress = _get_progress_report_deadlines(student, settings)
        events.extend(progress)
    
    # Add custom events
    custom = get_all_custom_events()
    for event in custom:
        event['days_until'] = calculate_days_until(event['deadline'])
    events.extend(custom)
    
    # Sort by deadline date
    events.sort(key=lambda e: e.get('deadline', '9999-12-31'))
    
    return events


def get_upcoming_deadlines(students_data, days_ahead=30):
    """Get deadlines within the next N days (includes overdue).
    
    Args:
        students_data: list of student dicts
        days_ahead: how many days ahead to look (default 30)
    
    Returns:
        list of deadline events that are overdue or due within days_ahead
    """
    all_events = get_calendar_events(students_data)
    return [e for e in all_events if e.get('days_until', 999) <= days_ahead]


def get_compliance_dashboard(students_data):
    """Generate a compliance dashboard summary.
    
    Returns:
        dict with counts, status categories, and formatted event lists
    """
    settings = get_compliance_settings()
    all_events = get_calendar_events(students_data)
    
    overdue = []
    urgent = []     # within 14 days
    upcoming = []   # 15-60 days
    on_track = []   # 60+ days
    
    for event in all_events:
        days = event.get('days_until', 999)
        if days < 0:
            event['status'] = 'overdue'
            overdue.append(event)
        elif days <= settings.get('warning_days_yellow', 14):
            event['status'] = 'urgent'
            urgent.append(event)
        elif days <= settings.get('warning_days_green', 60):
            event['status'] = 'upcoming'
            upcoming.append(event)
        else:
            event['status'] = 'on_track'
            on_track.append(event)
    
    return {
        "total_events": len(all_events),
        "overdue_count": len(overdue),
        "urgent_count": len(urgent),
        "upcoming_count": len(upcoming),
        "on_track_count": len(on_track),
        "overdue": overdue,
        "urgent": urgent,
        "upcoming": upcoming,
        "on_track": on_track,
        "all_events": all_events,
        "settings": settings,
    }


# ============================================================
# Custom Events (teacher-configurable)
# ============================================================

def get_all_custom_events():
    """Load all custom compliance events."""
    ensure_compliance_dir()
    if os.path.exists(EVENTS_FILE):
        with open(EVENTS_FILE, 'r') as f:
            return json.load(f)
    return []


def _save_custom_events(events):
    """Save custom events to file."""
    ensure_compliance_dir()
    with open(EVENTS_FILE, 'w') as f:
        json.dump(events, f, indent=2)


def add_custom_event(event_data):
    """Add a teacher-configurable deadline/event.
    
    Args:
        event_data: dict with keys:
            - title (str): event name
            - deadline (str): ISO date YYYY-MM-DD
            - student_id (str, optional): specific student or '' for class-wide
            - student_name (str, optional): student name for display
            - recurring (bool): whether to repeat annually
            - notes (str, optional): additional notes
    
    Returns:
        str: event_id of the created event
    """
    events = get_all_custom_events()
    
    event_id = str(uuid.uuid4())[:8]
    
    new_event = {
        "id": event_id,
        "type": "custom",
        "label": event_data.get('title', 'Custom Deadline'),
        "deadline": event_data.get('deadline', ''),
        "student_id": event_data.get('student_id', ''),
        "student_name": event_data.get('student_name', 'All Students'),
        "recurring": event_data.get('recurring', False),
        "notes": event_data.get('notes', ''),
        "regulation": "District/Teacher",
        "description": event_data.get('notes', 'Custom deadline'),
        "created_at": datetime.now().isoformat(),
    }
    
    events.append(new_event)
    _save_custom_events(events)
    
    return event_id


def remove_custom_event(event_id):
    """Delete a custom event by ID.
    
    Args:
        event_id: str ID of the event to remove
    
    Returns:
        bool: True if removed, False if not found
    """
    events = get_all_custom_events()
    original_count = len(events)
    events = [e for e in events if e.get('id') != event_id]
    
    if len(events) < original_count:
        _save_custom_events(events)
        return True
    return False


def get_deadline_status_class(days_until):
    """Return CSS class based on days until deadline.
    
    Args:
        days_until: int days until deadline
    
    Returns:
        str: 'overdue', 'urgent', 'upcoming', or 'on-track'
    """
    if days_until < 0:
        return 'overdue'
    elif days_until <= 14:
        return 'urgent'
    elif days_until <= 60:
        return 'upcoming'
    else:
        return 'on-track'


def format_deadline_display(days_until):
    """Format days_until for human-readable display.
    
    Args:
        days_until: int
    
    Returns:
        str: e.g. "3 days overdue", "Due today", "In 14 days"
    """
    if days_until < 0:
        return f"{abs(days_until)} day{'s' if abs(days_until) != 1 else ''} overdue"
    elif days_until == 0:
        return "Due today"
    elif days_until == 1:
        return "Due tomorrow"
    else:
        return f"In {days_until} days"
