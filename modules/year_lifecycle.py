"""
Year Lifecycle Module
Manages school year tracking, teacher stage configuration, and student lifecycle states.
Supports the full SPED pipeline: Pre-school → Elementary → Middle → High School.
"""

import json
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
CURRENT_YEAR_FILE = os.path.join(DATA_DIR, 'current_year.json')
CONFIG_FILE = os.path.join(DATA_DIR, 'config.json')
STUDENTS_DIR = os.path.join(DATA_DIR, 'students')

# Stage definitions — what each position in the pipeline looks like
STAGE_DEFINITIONS = {
    'preschool': {
        'label': 'Pre-School',
        'grade_range': ['Pre-K Year 1', 'Pre-K Year 2', 'Pre-K Year 3'],
        'receives_from': 'Early Intervention (First Steps)',
        'transitions_to': 'Elementary',
        'transition_trigger': 'Age 5 / Kindergarten eligibility',
        'typical_years': 3
    },
    'elementary': {
        'label': 'Elementary',
        'grade_range': ['K', '1st', '2nd', '3rd', '4th'],
        'receives_from': 'Pre-School',
        'transitions_to': 'Middle School',
        'transition_trigger': 'Completes highest grade in range',
        'typical_years': 5
    },
    'middle': {
        'label': 'Middle School',
        'grade_range': ['5th', '6th', '7th', '8th'],
        'receives_from': 'Elementary',
        'transitions_to': 'High School',
        'transition_trigger': 'Completes 8th grade',
        'typical_years': 4
    },
    'high_school': {
        'label': 'High School',
        'grade_range': ['9th', '10th', '11th', '12th', '12th+'],
        'receives_from': 'Middle School',
        'transitions_to': 'Post-Secondary Transition',
        'transition_trigger': 'Age 21 or graduation with modified diploma',
        'typical_years': 4
    }
}


def get_current_year():
    """Get the current active school year."""
    if os.path.exists(CURRENT_YEAR_FILE):
        with open(CURRENT_YEAR_FILE, 'r') as f:
            return json.load(f)
    return None


def set_current_year(year_string):
    """Set/create the current school year."""
    os.makedirs(DATA_DIR, exist_ok=True)
    data = {
        'year': year_string,
        'started': datetime.now().isoformat(),
        'status': 'active'
    }
    with open(CURRENT_YEAR_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    return data


def is_migrated():
    """Check if the app has been migrated to year-aware format."""
    return os.path.exists(CURRENT_YEAR_FILE)


def get_teacher_stage():
    """Get the teacher's stage configuration from config.json."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        return config.get('teacher_stage', None)
    return None


def set_teacher_stage(stage_key):
    """
    Set the teacher's stage and auto-populate stage config.
    stage_key: one of 'preschool', 'elementary', 'middle', 'high_school'
    """
    if stage_key not in STAGE_DEFINITIONS:
        raise ValueError(f"Invalid stage: {stage_key}. Must be one of: {list(STAGE_DEFINITIONS.keys())}")
    
    stage_def = STAGE_DEFINITIONS[stage_key]
    stage_config = {
        'stage': stage_key,
        'label': stage_def['label'],
        'grade_range': stage_def['grade_range'],
        'receives_from': stage_def['receives_from'],
        'transitions_to': stage_def['transitions_to'],
        'transition_trigger': stage_def['transition_trigger'],
        'typical_years': stage_def['typical_years'],
        'max_holdbacks': 3  # KY allows up to 3 total across K-12
    }
    
    # Update config.json
    config = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
    
    config['teacher_stage'] = stage_config
    
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    
    return stage_config


def get_student_lifecycle(student_id):
    """Get lifecycle data for a student (new format only)."""
    lifecycle_path = os.path.join(STUDENTS_DIR, student_id, 'lifecycle.json')
    if os.path.exists(lifecycle_path):
        with open(lifecycle_path, 'r') as f:
            return json.load(f)
    return None


def save_student_lifecycle(student_id, lifecycle_data):
    """Save lifecycle data for a student."""
    student_dir = os.path.join(STUDENTS_DIR, student_id)
    os.makedirs(student_dir, exist_ok=True)
    lifecycle_path = os.path.join(student_dir, 'lifecycle.json')
    with open(lifecycle_path, 'w') as f:
        json.dump(lifecycle_data, f, indent=2)


def create_default_lifecycle(student_id, grade='unknown', year='2026-27'):
    """Create a default lifecycle record for a student."""
    stage = get_teacher_stage()
    lifecycle = {
        'current_status': 'active',
        'current_grade': grade,
        'current_year': year,
        'entry_year': year,
        'entry_grade': grade,
        'expected_transition_year': calculate_expected_transition(
            year, grade, stage
        ) if stage else 'unknown',
        'grade_history': [
            {
                'year': year,
                'grade': grade,
                'status': 'in_progress'
            }
        ],
        'held_back_years': [],
        'held_back_count': 0,
        'transition_notes': ''
    }
    save_student_lifecycle(student_id, lifecycle)
    return lifecycle


def get_student_history(student_id):
    """List all archived year files for a student."""
    history_dir = os.path.join(STUDENTS_DIR, student_id, 'history')
    if not os.path.exists(history_dir):
        return []
    
    years = []
    for filename in sorted(os.listdir(history_dir)):
        if filename.endswith('.json'):
            filepath = os.path.join(history_dir, filename)
            with open(filepath, 'r') as f:
                year_data = json.load(f)
            years.append(year_data)
    return years


def archive_student_year(student_id, year, year_data):
    """Archive a completed year's data for a student."""
    history_dir = os.path.join(STUDENTS_DIR, student_id, 'history')
    os.makedirs(history_dir, exist_ok=True)
    
    year_data['archived_on'] = datetime.now().isoformat()
    filepath = os.path.join(history_dir, f"{year}.json")
    with open(filepath, 'w') as f:
        json.dump(year_data, f, indent=2)
    
    return filepath


def calculate_expected_transition(entry_year, entry_grade, stage_config, held_back_count=0):
    """
    Calculate when a student is expected to transition out.
    
    Args:
        entry_year: e.g. "2026-27"
        entry_grade: e.g. "K" or "2nd"
        stage_config: the teacher's stage configuration dict
        held_back_count: number of times held back
    
    Returns:
        Expected transition year string (e.g. "2030-31") or "unknown"
    """
    if not stage_config or not entry_year or entry_grade == 'unknown':
        return 'unknown'
    
    try:
        grade_range = stage_config.get('grade_range', [])
        if entry_grade not in grade_range:
            return 'unknown'
        
        # How many years from entry grade to end of range
        grade_index = grade_range.index(entry_grade)
        years_remaining = len(grade_range) - grade_index - 1 + held_back_count
        
        # Parse entry year (e.g. "2026-27" → start year 2026)
        start_year = int(entry_year.split('-')[0])
        
        # Transition happens AFTER the last year
        transition_start = start_year + years_remaining + 1
        transition_year = f"{transition_start}-{str(transition_start + 1)[-2:]}"
        
        return transition_year
    except (ValueError, IndexError):
        return 'unknown'


def get_stage_definitions():
    """Return all stage definitions (for the migration wizard)."""
    return STAGE_DEFINITIONS
